import numpy as np
from sklearn.cluster import KMeans
from typing import List, Tuple
from services.domain_services.cluster_profile import ClusterProfile
from services.analytical_engine.utils import (
    compute_t2_control_limit,
    compute_mahalanobis,
    find_optimal_k
)


class KMeansMahalanobisEngine:

    K_MIN = 2
    K_MAX = 10

    def train(self, X: np.ndarray) -> Tuple[List[ClusterProfile], float, int]:
        """
        Entrena KMeans con k óptimo por método del codo.
        Devuelve los ClusterProfiles, accuracy (silhouette) y k elegido.
        """
        k_range = list(range(self.K_MIN, min(self.K_MAX + 1, len(X))))
        inertias = []
        models = {}

        for k in k_range:
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            km.fit(X)
            inertias.append(km.inertia_)
            models[k] = km

        optimal_k = find_optimal_k(inertias, k_range)
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