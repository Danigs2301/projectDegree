import numpy as np
from sklearn.cluster import KMeans
from typing import List, Tuple
from services.domain_services.cluster_profile import ClusterProfile
from services.analytical_engine.utils import (
    compute_t2_control_limit,
    compute_mahalanobis,
    compute_t2_contributions,
    find_optimal_k
)


class KMeansMahalanobisEngine:

    K_MIN = 2
    K_MAX = 10
    MIN_OBS_PER_VARIABLE = 3

    def train(self, X: np.ndarray) -> Tuple[List[ClusterProfile], float, int]:
        n_variables = X.shape[1]
        min_cluster_size = n_variables * self.MIN_OBS_PER_VARIABLE

        k_range = list(range(self.K_MIN, min(self.K_MAX + 1, len(X))))
        inertias = []
        models = {}
        valid_k_range = []
        valid_inertias = []

        for k in k_range:
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            km.fit(X)
            inertias.append(km.inertia_)
            models[k] = km

            cluster_sizes = np.bincount(km.labels_, minlength=k)
            if cluster_sizes.min() >= min_cluster_size:
                valid_k_range.append(k)
                valid_inertias.append(km.inertia_)

        if valid_k_range:
            optimal_k = find_optimal_k(valid_inertias, valid_k_range)
        else:
            optimal_k = self.K_MIN  # ningún k produjo clusters suficientemente grandes; el más conservador

        best_model = models[optimal_k]
        labels = best_model.labels_

        cluster_profiles = self._build_cluster_profiles(X, labels, optimal_k)
        accuracy = self._compute_silhouette(X, labels)

        return cluster_profiles, accuracy, optimal_k

    def _build_cluster_profiles(
        self, X: np.ndarray, labels: np.ndarray, k: int
    ) -> List[ClusterProfile]:
        profiles = []
        n_variables = X.shape[1]

        for cluster_id in range(k):
            mask = labels == cluster_id
            X_cluster = X[mask]
            n_obs = len(X_cluster)

            centroid = X_cluster.mean(axis=0).tolist()

            if n_obs > 1:
                cov_matrix = np.cov(X_cluster.T).tolist()
            else:
                cov_matrix = np.eye(n_variables).tolist()

            t2_limit = compute_t2_control_limit(
                n_variables=n_variables,
                n_observations=n_obs
            )

            profiles.append(ClusterProfile(
                cluster_id=str(cluster_id),
                centroid=centroid,
                covariance_matrix=cov_matrix,
                t2_control_limit=t2_limit,
                n_observations=n_obs
            ))

        return profiles

    def _compute_silhouette(self, X: np.ndarray, labels: np.ndarray) -> float:
        try:
            from sklearn.metrics import silhouette_score
            return float(silhouette_score(X, labels))
        except Exception:
            return 0.0

    def detect_change(
        self, x: np.ndarray, cluster_profiles: List[ClusterProfile]
    ) -> Tuple[str, float, float, bool]:
        """
        Asigna la muestra al cluster más cercano y calcula T².
        Devuelve (cluster_id, t2_statistic, control_limit, is_anomaly).
        """
        min_distance = float("inf")
        assigned_profile = None

        for profile in cluster_profiles:
            centroid = np.array(profile.centroid)
            distance = np.linalg.norm(x - centroid)
            if distance < min_distance:
                min_distance = distance
                assigned_profile = profile

        centroid = np.array(assigned_profile.centroid)
        cov_matrix = np.array(assigned_profile.covariance_matrix)
        t2 = compute_mahalanobis(x, centroid, cov_matrix)
        is_anomaly = t2 > assigned_profile.t2_control_limit

        return (
            assigned_profile.cluster_id,
            t2,
            assigned_profile.t2_control_limit,
            is_anomaly
        )
    
    def compute_variable_contributions(
        self,
        x_scaled: np.ndarray,
        pca_components: np.ndarray,
        pca_mean: np.ndarray,
        cluster_profile: ClusterProfile
    ) -> np.ndarray:
        """
        Descompone el T² de una muestra ya asignada a un cluster, atribuyendo
        la contribución a cada variable ORIGINAL (antes de PCA), aprovechando
        que los componentes de PCA son ortonormales.
        """
        centroid_pca = np.array(cluster_profile.centroid)
        cov_pca = np.array(cluster_profile.covariance_matrix)

        try:
            inv_cov_pca = np.linalg.inv(cov_pca)
        except np.linalg.LinAlgError:
            inv_cov_pca = np.linalg.pinv(cov_pca)

        # centroide reconstruido en espacio original escalado (equivalente a PCA.inverse_transform)
        centroid_scaled = centroid_pca @ pca_components + pca_mean
        diff_scaled = x_scaled - centroid_scaled

        # matriz de covarianza inversa "jalada" de vuelta al espacio original
        M = pca_components.T @ inv_cov_pca @ pca_components

        return compute_t2_contributions(diff_scaled, M)
        
        