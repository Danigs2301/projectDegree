from collections import defaultdict
from data.repositories.process_repository import ProcessRepository
from data.repositories.sample_repository import SampleRepository
from data.repositories.model_repository import ModelRepository
from data.repositories.alert_repository import AlertRepository
from typing import List


class SummaryService:

    def __init__(self):
        self.process_repository = ProcessRepository()
        self.sample_repository = SampleRepository()
        self.model_repository = ModelRepository()
        self.alert_repository = AlertRepository()

    def get_process_summary(self, process_id: str) -> dict:
        process = self.process_repository.find_by_id(process_id)
        if process is None:
            raise ValueError(f"Proceso con id {process_id} no encontrado")

        samples = self.sample_repository.find_by_process_id(process_id)
        models = self.model_repository.find_by_process_id(process_id)
        trained_models = [m for m in models if m.state == "trained"]

        all_alerts = []
        for model in trained_models:
            alerts = self.alert_repository.find_by_model_id(model.id)
            all_alerts.extend(alerts)

        pending_alerts = [a for a in all_alerts if not a.confirmed]

        total_samples = len(samples)
        total_anomalies = len(all_alerts)
        total_analyzed = total_anomalies

        control_rate = (
            round(((total_samples - total_anomalies) / total_samples) * 100, 1)
            if total_samples > 0 else None
        )

        anomaly_rate_chart = self._compute_anomaly_rate(samples, all_alerts)

        variable_charts = {}
        for sample in samples:
            for m in sample.measurements:
                if m.variable_id not in variable_charts:
                    variable_charts[m.variable_id] = []
                variable_charts[m.variable_id].append({
                    "date": sample.date.isoformat(),
                    "value": m.value,
                })

        for var_id in variable_charts:
            variable_charts[var_id].sort(key=lambda x: x["date"])

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