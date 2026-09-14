import services.domain_services

import numpy as np
import pytest
from scipy import stats
from sklearn.cluster import KMeans

from services.analytical_engine.utils.math_utils import (
    compute_t2_control_limit,
    compute_mahalanobis,
)
from services.analytical_engine.preprocessing.data_preprocessor import DataPreprocessor
from services.analytical_engine.core.kmeans_mahalanobis_engine import KMeansMahalanobisEngine


# ---------------------------------------------------------------------------
# compute_t2_control_limit -- punto 3.b del jurado (formula prospectiva)
# ---------------------------------------------------------------------------

class TestComputeT2ControlLimit:

    def test_matches_manual_prospective_formula(self):
        p, n, alpha = 9, 1597, 0.05
        f_critical = stats.f.ppf(1 - alpha, p, n - p)
        expected = (p * (n + 1) * (n - 1) / (n * (n - p))) * f_critical
        result = compute_t2_control_limit(p, n, alpha)
        assert result == pytest.approx(expected, rel=1e-12)

    def test_regression_known_value_chemical_process(self):
        result = compute_t2_control_limit(n_variables=9, n_observations=1597)
        assert result == pytest.approx(17.068058557707012, rel=1e-9)

    def test_prospective_is_always_larger_than_retrospective(self):
        for p, n in [(3, 10), (9, 1597), (8, 878), (5, 30)]:
            f_critical = stats.f.ppf(0.95, p, n - p)
            retrospective = (p * (n - 1) / (n - p)) * f_critical
            prospective = compute_t2_control_limit(p, n)
            assert prospective > retrospective
            assert prospective / retrospective == pytest.approx((n + 1) / n, rel=1e-9)

    def test_small_cluster_correction_matches_documented_range(self):
        incr_min = (2728 / 2727 - 1) * 100
        incr_max = (31 / 30 - 1) * 100
        assert incr_min == pytest.approx(0.0367, abs=0.001)
        assert incr_max == pytest.approx(3.333, abs=0.001)

    def test_guard_against_non_positive_degrees_of_freedom(self):
        result = compute_t2_control_limit(n_variables=9, n_observations=3)
        assert np.isfinite(result)
        assert result > 0


# ---------------------------------------------------------------------------
# compute_mahalanobis
# ---------------------------------------------------------------------------

class TestComputeMahalanobis:

    def test_identity_covariance_equals_squared_euclidean_distance(self):
        x = np.array([3.0, 4.0])
        centroid = np.array([0.0, 0.0])
        cov = np.eye(2)
        # con covarianza identidad, T2 = ||x - centroide||^2 = 3^2 + 4^2 = 25
        assert compute_mahalanobis(x, centroid, cov) == pytest.approx(25.0)

    def test_zero_distance_is_zero(self):
        x = np.array([1.0, 2.0, 3.0])
        cov = np.diag([1.0, 2.0, 3.0])
        assert compute_mahalanobis(x, x.copy(), cov) == pytest.approx(0.0)

    def test_singular_covariance_uses_pseudo_inverse_without_raising(self):
        x = np.array([1.0, 1.0])
        centroid = np.array([0.0, 0.0])
        singular_cov = np.array([[1.0, 1.0], [1.0, 1.0]])  # rango 1, no invertible
        result = compute_mahalanobis(x, centroid, singular_cov)
        assert np.isfinite(result)


# ---------------------------------------------------------------------------
# DataPreprocessor -- determinismo y asimetria entrenamiento/deteccion
# ---------------------------------------------------------------------------

class TestDataPreprocessor:

    @staticmethod
    def _synthetic_samples(n=200, n_vars=5, seed=0):
        rng = np.random.default_rng(seed)
        base = rng.normal(loc=10, scale=2, size=(n, n_vars))
        n_out = max(1, n // 20)  # ~5% de outliers evidentes
        base[:n_out] += rng.normal(loc=40, scale=1, size=(n_out, n_vars))
        samples = []
        for i, row in enumerate(base):
            d = {"sample_id": str(i)}
            for j, val in enumerate(row):
                d[f"v{j}"] = float(val)
            samples.append(d)
        return samples

    def test_fit_transform_is_deterministic(self):
        samples = self._synthetic_samples()
        out1 = DataPreprocessor().fit_transform(samples)
        out2 = DataPreprocessor().fit_transform(samples)
        np.testing.assert_array_equal(out1, out2)

    def test_removes_roughly_expected_outlier_fraction(self):
        samples = self._synthetic_samples(n=200)
        pre = DataPreprocessor(contamination=0.05, use_pca=False)
        out = pre.fit_transform(samples)
        removed = 200 - out.shape[0]
        assert 5 <= removed <= 20  # contamination=0.05 sobre 200 -> ~10, con margen

    def test_transform_does_not_filter_outliers(self):
        samples = self._synthetic_samples(n=200)
        pre = DataPreprocessor(use_pca=False)
        pre.fit_transform(samples)
        extreme = {f"v{j}": 200.0 for j in range(5)}  # del mismo tipo que SI se filtraria en entrenamiento
        result = pre.transform(extreme)
        assert result.shape == (5,)
        assert np.isfinite(result).all()


# ---------------------------------------------------------------------------
# KMeansMahalanobisEngine -- sanidad del clustering + deteccion T2
# ---------------------------------------------------------------------------

class TestKMeansMahalanobisEngine:

    @staticmethod
    def _two_blobs(seed=0, scale=0.15):
        rng = np.random.default_rng(seed)
        blob_a = rng.normal(loc=[0, 0], scale=scale, size=(150, 2))
        blob_b = rng.normal(loc=[20, 20], scale=scale, size=(150, 2))
        return np.vstack([blob_a, blob_b])

    def test_never_mixes_two_clearly_separated_groups_in_one_cluster(self):
        X = self._two_blobs(scale=0.15)
        group = np.array([0] * 150 + [1] * 150)
        engine = KMeansMahalanobisEngine()
        _, _, k = engine.train(X)
        km_labels = KMeans(n_clusters=k, random_state=42, n_init=10).fit(X).labels_
        for cluster_id in range(k):
            groups_in_cluster = set(group[km_labels == cluster_id].tolist())
            assert len(groups_in_cluster) == 1, (
                f"El cluster {cluster_id} mezcla puntos de los dos grupos separados"
            )

    def test_detect_change_flags_far_point_as_anomaly(self):
        X = self._two_blobs()
        engine = KMeansMahalanobisEngine()
        profiles, _, _ = engine.train(X)
        far_point = np.array([200.0, 200.0])
        _, t2, limit, is_anomaly = engine.detect_change(far_point, profiles)
        assert is_anomaly is True
        assert t2 > limit

    def test_detect_change_does_not_flag_point_near_centroid(self):
        X = self._two_blobs()
        engine = KMeansMahalanobisEngine()
        profiles, _, _ = engine.train(X)
        near_point = np.array([0.05, -0.05])
        _, t2, limit, is_anomaly = engine.detect_change(near_point, profiles)
        assert is_anomaly is False
        assert t2 < limit
