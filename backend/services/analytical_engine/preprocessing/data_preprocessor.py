import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.ensemble import IsolationForest
from typing import List


class DataPreprocessor:

    def __init__(
        self,
        contamination: float = 0.05,
        use_pca: bool = True,
        pca_variance: float = 0.95
    ):
        """
        contamination: porcentaje esperado de outliers (0.0 - 0.5)
        use_pca:       si usar reducción de dimensionalidad
        pca_variance:  varianza a retener en PCA (valor entre 0 y 1)
        """
        self.scaler = StandardScaler()
        self.iso = IsolationForest(contamination=contamination, random_state=42)

        self.use_pca = use_pca
        self.pca_variance = pca_variance
        self.pca = None

        self.variable_ids: List[str] = []

    # =====================================================
    # 🔹 VALIDACIÓN
    # =====================================================

    def _validate_matrix(self, X: np.ndarray, label: str = ""):
        tag = f"[{label}] " if label else ""

        if np.isnan(X).any():
            raise ValueError(f"❌ {tag}Hay valores NaN en los datos")

        if np.isinf(X).any():
            raise ValueError(f"❌ {tag}Hay valores infinitos en los datos")

        if X.shape[0] < 10:
            raise ValueError(f"❌ {tag}Muy pocas muestras ({X.shape[0]}), mínimo requerido: 10")

    # =====================================================
    # 🔹 CONSTRUCCIÓN DE MATRIZ
    # =====================================================

    def _build_matrix(self, samples: List[dict]) -> np.ndarray:

        if not samples:
            raise ValueError("❌ No hay muestras para procesar")

        # Extraer variables (orden consistente)
        self.variable_ids = [
            k for k in samples[0].keys() if k != "sample_id"
        ]

        matrix = []
        for sample in samples:
            try:
                row = [float(sample[var_id]) for var_id in self.variable_ids]
                matrix.append(row)
            except KeyError as e:
                raise ValueError(f"❌ Variable faltante en muestra: {e}")
            except (TypeError, ValueError) as e:
                raise ValueError(f"❌ Valor no numérico en muestra: {e}")

        return np.array(matrix, dtype=float)

    # =====================================================
    # 🔹 LIMPIEZA DE OUTLIERS
    # =====================================================

    def _remove_outliers(self, X: np.ndarray) -> np.ndarray:
        """
        Recibe datos ya escalados. IsolationForest trabaja mejor
        en espacio escalado donde las distancias son comparables.
        """
        preds = self.iso.fit_predict(X)
        mask = preds == 1

        removed = int(np.sum(preds == -1))
        print(f"🧹 Outliers eliminados: {removed} ({removed / len(preds) * 100:.1f}%)")

        return X[mask]

    # =====================================================
    # 🔹 ENTRENAMIENTO COMPLETO
    # =====================================================

    def fit_transform(self, samples: List[dict]) -> np.ndarray:
        """
        Pipeline completo para entrenamiento:
          1. Construir matriz
          2. Validar datos crudos
          3. Escalar (con todos los datos, incluidos outliers)
          4. Eliminar outliers en espacio escalado
          5. Validar que queden suficientes muestras
          6. PCA opcional
        """

        # 1. Construir matriz
        X = self._build_matrix(samples)
        print(f"📊 Muestras originales: {X.shape[0]} | Variables: {X.shape[1]}")

        # 2. Validar datos crudos
        self._validate_matrix(X, label="crudos")

        # 3. Escalar ANTES de detectar outliers
        #    El scaler se ajusta sobre todos los datos para que la referencia
        #    de media/std sea representativa del dominio completo en producción.
        X_scaled = self.scaler.fit_transform(X)
        print(f"📏 Escalado aplicado → media: {X_scaled.mean():.4f} | std: {X_scaled.std():.4f}")

        # 4. Eliminar outliers sobre espacio escalado
        X_clean = self._remove_outliers(X_scaled)
        print(f"✅ Muestras limpias: {X_clean.shape[0]}")

        # 5. Validar que queden suficientes muestras tras la limpieza
        self._validate_matrix(X_clean, label="post-limpieza")

        # 6. PCA opcional
        if self.use_pca:
            self.pca = PCA(n_components=self.pca_variance)
            X_final = self.pca.fit_transform(X_clean)
            variance_explained = self.pca.explained_variance_ratio_.sum()
            print(f"📉 PCA aplicado → {X_final.shape[1]} componentes | varianza retenida: {variance_explained:.2%}")
        else:
            X_final = X_clean

        return X_final

    # =====================================================
    # 🔹 TRANSFORMACIÓN NUEVAS MUESTRAS
    # =====================================================

    def transform(self, sample: dict) -> np.ndarray:
        """
        Procesa una muestra nueva (producción).
        No aplica detección de outliers: esa decisión
        debe tomarse en la capa de negocio si es necesario.
        """

        # Validar variables presentes
        missing = set(self.variable_ids) - set(sample.keys())
        if missing:
            raise ValueError(f"❌ Variables faltantes en la muestra: {missing}")

        try:
            row = [float(sample[var_id]) for var_id in self.variable_ids]
        except (TypeError, ValueError) as e:
            raise ValueError(f"❌ Valor no numérico en la muestra: {e}")

        X = np.array([row], dtype=float)

        # Escalar con el scaler ya ajustado
        X_scaled = self.scaler.transform(X)

        # PCA si aplica
        if self.use_pca and self.pca is not None:
            return self.pca.transform(X_scaled)[0]

        return X_scaled[0]

    # =====================================================
    # 🔹 INFO
    # =====================================================

    def get_variable_ids(self) -> List[str]:
        return self.variable_ids