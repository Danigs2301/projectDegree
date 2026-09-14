import numpy as np
from scipy import stats


def compute_t2_control_limit(n_variables: int, n_observations: int, alpha: float = 0.05) -> float:
    p = n_variables
    n = max(n_observations, p + 1)
    f_critical = stats.f.ppf(1 - alpha, p, n - p)
    return (p * (n + 1) * (n - 1) / (n * (n - p))) * f_critical


def compute_mahalanobis(x: np.ndarray, centroid: np.ndarray, cov_matrix: np.ndarray) -> float:
    """
    Distancia de Mahalanobis al cuadrado (estadístico T²).
    """
    diff = x - centroid
    try:
        inv_cov = np.linalg.inv(cov_matrix)
    except np.linalg.LinAlgError:
        inv_cov = np.linalg.pinv(cov_matrix)
    return float(diff @ inv_cov @ diff)


def find_optimal_k(inertias: list[float], k_range: list[int]) -> int:
    """
    Método del codo: encuentra el k donde la reducción
    de inercia deja de ser significativa.
    """
    if len(inertias) < 3:
        return k_range[0]

    deltas = [inertias[i] - inertias[i + 1] for i in range(len(inertias) - 1)]
    second_derivatives = [deltas[i] - deltas[i + 1] for i in range(len(deltas) - 1)]
    elbow_index = int(np.argmax(second_derivatives)) + 1
    return k_range[elbow_index]

def compute_t2_contributions(diff: np.ndarray, inv_cov: np.ndarray) -> np.ndarray:
    """
    Descompone el estadístico T² en la contribución de cada dimensión.
    La suma de todas las contribuciones es exactamente igual al T² total.
    """
    return diff * (inv_cov @ diff)