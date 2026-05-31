from flask import Flask, jsonify
from data.infrastructure.mongodb import get_db, close_connection
from presentation.routes import (
    process_bp,
    variable_bp,
    sample_bp,
    model_bp,
    alert_bp,
    detection_bp
)


app = Flask(__name__)

with app.app_context():
    db = get_db()
    print(f"Conectado a MongoDB: {db.name}")

app.register_blueprint(process_bp)
app.register_blueprint(variable_bp)
app.register_blueprint(sample_bp)
app.register_blueprint(model_bp)
app.register_blueprint(alert_bp)
app.register_blueprint(detection_bp)

"""@app.teardown_appcontext
def shutdown(exception=None):
    close_connection()"""

@app.get("/health")
def health():
    return jsonify({"status": "ok"})