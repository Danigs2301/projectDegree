from flask import jsonify, request
from datetime import datetime
from services.domain_services.summary_service import SummaryService

service = SummaryService()


def get_all_summaries():
    try:
        summaries = service.get_all_summaries()
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    return jsonify(summaries), 200


def _parse_date_range():
    from_str = request.args.get("from")
    to_str = request.args.get("to")

    from_date = datetime.strptime(from_str, "%Y-%m-%d") if from_str else None
    to_date = (
        datetime.strptime(to_str, "%Y-%m-%d").replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        if to_str else None
    )
    return from_date, to_date


def get_process_summary(process_id: str):
    try:
        from_date, to_date = _parse_date_range()
    except ValueError:
        return jsonify({"error": "Formato de fecha inválido, usa YYYY-MM-DD"}), 400

    try:
        summary = service.get_process_summary(process_id, from_date, to_date)
    except ValueError as e:
        return jsonify({"error": str(e)}), 404
    return jsonify(summary), 200