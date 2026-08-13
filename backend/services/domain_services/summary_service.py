import numpy as np
from services.analytical_engine.core import KMeansMahalanobisEngine
from services.analytical_engine.utils import compute_t2_contributions
from collections import defaultdict
from data.repositories.process_repository import ProcessRepository
from data.repositories.sample_repository import SampleRepository
from data.repositories.model_repository import ModelRepository
from data.repositories.alert_repository import AlertRepository
from typing import List
from datetime import datetime


class SummaryService:

    def __init__(self):
        self.process_repository = ProcessRepository()
        self.sample_repository = SampleRepository()
        self.model_repository = ModelRepository()
        self.alert_repository = AlertRepository()

    def get_process_summary(self, process_id: str, from_date: datetime = None, to_date: datetime = None) -> dict:
        process = self.process_repository.find_by_id(process_id)
        if process is None:
            raise ValueError(f"Proceso con id {process_id} no encontrado")

        samples = self.sample_repository.find_by_process_id(process_id)
        if from_date:
            samples = [s for s in samples if s.date >= from_date]
        if to_date:
            samples = [s for s in samples if s.date <= to_date]

        models = self.model_repository.find_by_process_id(process_id)
        trained_models = [m for m in models if m.state == "trained"]

        all_alerts = []
        for model in trained_models:
            alerts = self.alert_repository.find_by_model_id(model.id)
            all_alerts.extend(alerts)

        if from_date:
            all_alerts = [a for a in all_alerts if a.detection_date >= from_date]
        if to_date:
            all_alerts = [a for a in all_alerts if a.detection_date <= to_date]

        pending_alerts = [a for a in all_alerts if not a.confirmed]

        total_samples = len(samples)
        total_anomalies = len(all_alerts)
        total_analyzed = total_anomalies

        control_rate = (
            round(((total_samples - total_anomalies) / total_samples) * 100, 1)
            if total_samples > 0 else None
        )

        anomaly_rate_chart = self._compute_anomaly_rate(samples, all_alerts)

        latest_model = max(trained_models, key=lambda m: m.training_date) if trained_models else None
        variable_charts = self._build_variable_charts(samples, latest_model)

        return {
            "process_id": process_id,
            "process_name": process.name,
            "state": process.state,
            "n_variables": len(process.variable_ids),
            "n_samples": total_samples,
            "n_models": len(models),
            "n_trained_models": len(trained_models),
            "n_pending_alerts": len(pending_alerts),
            "total_analyzed": total_analyzed,
            "control_rate": control_rate,
            "anomaly_rate_chart": anomaly_rate_chart,
            "variable_charts": variable_charts,
        }

    def _compute_anomaly_rate(self, samples, alerts) -> list:
        samples_by_day = defaultdict(int)
        for sample in samples:
            day = sample.date.strftime("%Y-%m-%d")
            samples_by_day[day] += 1

        anomalies_by_day = defaultdict(int)
        for alert in alerts:
            day = alert.detection_date.strftime("%Y-%m-%d")
            anomalies_by_day[day] += 1

        all_days = sorted(
            set(list(samples_by_day.keys()) + list(anomalies_by_day.keys()))
        )

        result = []
        for day in all_days:
            total = samples_by_day.get(day, 0)
            anomalies = anomalies_by_day.get(day, 0)
            rate = round((anomalies / total) * 100, 1) if total > 0 else 0
            result.append({
                "date": day,
                "total_samples": total,
                "anomalies": anomalies,
                "rate": rate,
            })

        return result

    def get_all_summaries(self) -> List[dict]:
        processes = self.process_repository.find_all()
        return [self.get_process_summary(p.id) for p in processes]

    def _build_variable_charts(self, samples, model) -> dict:
        variable_charts = {}

        if model is None:
            for sample in samples:
                for m in sample.measurements:
                    variable_charts.setdefault(m.variable_id, []).append({
                        "date": sample.date.isoformat(),
                        "value": m.value,
                        "contribution": None,
                        "is_anomaly": None,
                        "is_relevant": False,
                    })
            for var_id in variable_charts:
                variable_charts[var_id].sort(key=lambda x: x["date"])
            return variable_charts

        variable_ids = model.parameters.get("variable_ids", [])
        scaler_mean = np.array(model.parameters.get("scaler_mean", []))
        scaler_scale = np.array(model.parameters.get("scaler_scale", []))
        use_pca = model.parameters.get("use_pca", False)
        pca_components = np.array(model.parameters.get("pca_components", [])) if use_pca else None
        pca_mean = np.array(model.parameters.get("pca_mean", [])) if use_pca else None
        profiles_by_id = {p.cluster_id: p for p in model.cluster_profiles}
        engine = KMeansMahalanobisEngine()

        for sample in samples:
            measurements = {m.variable_id: m.value for m in sample.measurements}
            contributions, is_anomaly, relevant_vars = None, None, set()

            is_post_training = sample.date > model.training_date

            if is_post_training and variable_ids and all(v in measurements for v in variable_ids):
                try:
                    x_raw = np.array([measurements[v] for v in variable_ids], dtype=float)
                    x_scaled = (x_raw - scaler_mean) / scaler_scale
                    x_pca = (x_scaled - pca_mean) @ pca_components.T if use_pca else x_scaled

                    cluster_id, t2, limit, anomaly = engine.detect_change(x_pca, model.cluster_profiles)
                    is_anomaly = anomaly
                    assigned_profile = profiles_by_id[cluster_id]

                    if use_pca:
                        contrib_vec = engine.compute_variable_contributions(
                            x_scaled, pca_components, pca_mean, assigned_profile
                        )
                    else:
                        diff = x_scaled - np.array(assigned_profile.centroid)
                        inv_cov = np.linalg.pinv(np.array(assigned_profile.covariance_matrix))
                        contrib_vec = compute_t2_contributions(diff, inv_cov)

                    contributions = {v: float(c) for v, c in zip(variable_ids, contrib_vec)}
                    if is_anomaly and t2 > 0:
                        relevant_vars = {v for v in variable_ids if contributions[v] / t2 >= 0.15}
                except Exception:
                    contributions, is_anomaly = None, None

            for m in sample.measurements:
                variable_charts.setdefault(m.variable_id, []).append({
                    "date": sample.date.isoformat(),
                    "value": m.value,
                    "contribution": contributions.get(m.variable_id) if contributions else None,
                    "is_anomaly": is_anomaly,
                    "is_relevant": m.variable_id in relevant_vars,
                })

        for var_id in variable_charts:
            variable_charts[var_id].sort(key=lambda x: x["date"])

        return variable_charts