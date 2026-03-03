# @Version :1.0
# @Author  : Mingyue
# @File    : app.py.py
# @Time    : 02/03/2026 20:36
import os
import logging
from flask import Flask
from dotenv import load_dotenv

load_dotenv()


def create_app() -> Flask:
    app = Flask(__name__, template_folder="templates", static_folder="static")

    # ── Config ────────────────────────────────────────────────────────────────
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "sqlite:///ai_coding_assistant.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ── Logging ───────────────────────────────────────────────────────────────
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    # ── Extensions ────────────────────────────────────────────────────────────
    from app.db import db
    db.init_app(app)

    # ── Blueprints ────────────────────────────────────────────────────────────
    from app.routes.api import api_bp
    from app.routes.web import web_bp
    app.register_blueprint(api_bp)
    app.register_blueprint(web_bp)

    # ── DB Init ───────────────────────────────────────────────────────────────
    with app.app_context():
        from app.models import Prompt, Generation, Evaluation  # noqa: F401
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=5000)
