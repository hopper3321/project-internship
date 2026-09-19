import logging
import sys
from pathlib import Path

# Allow running: python backend/app.py from project root
ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from flask import Flask
from flask_cors import CORS

from backend import config
from backend.routes.api import api_bp

logging.basicConfig(level=logging.INFO)


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": config.CORS_ORIGINS}})
    app.register_blueprint(api_bp, url_prefix="/api")
    return app


app = create_app()

if __name__ == "__main__":
    port = int(__import__("os").getenv("FLASK_PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
