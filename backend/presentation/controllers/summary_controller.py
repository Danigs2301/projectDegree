from flask import jsonify
from services.domain_services.summary_service import SummaryService

service = SummaryService()


def get_all_summaries():
    try:
        summaries = service.get_all_summaries()
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(summaries), 200


def get_process_summary(process_id: str):
    try:
        summary = service.get_process_summary(process_id)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    return jsonify(summary), 200