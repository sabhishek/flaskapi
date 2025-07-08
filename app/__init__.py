import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api
from celery import Celery
from dotenv import load_dotenv
import yaml
from pathlib import Path

# Globals accessible elsewhere

db = SQLAlchemy()
celery_app: Celery | None = None


def make_celery(flask_app: Flask) -> Celery:
    celery_broker = flask_app.config.get("CELERY_BROKER_URL")
    celery_backend = flask_app.config.get("CELERY_RESULT_BACKEND")

    celery = Celery(flask_app.import_name, broker=celery_broker, backend=celery_backend)
    celery.conf.update(flask_app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with flask_app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    return celery


def load_config():
    # Prefer CONFIG_FILE env var, fallback to config.yaml at project root
    root_dir = Path(__file__).resolve().parent.parent
    cfg_path = Path(os.getenv("CONFIG_FILE", str(root_dir / "config.yaml")))
    with open(cfg_path, "r") as fp:
        return yaml.safe_load(fp)


def create_app() -> Flask:
    load_dotenv()
    cfg = load_config()

    app = Flask(__name__)
    # Determine whether to mock external services (Redis, Postgres)
    mock_mode = os.getenv("MOCK_RESOURCES", "true").lower() in ("1", "true", "yes")

    # Database (SQLite fallback when mocking)
    if mock_mode:
        db_uri = "sqlite:///local.db"
    else:
        db_uri = cfg.get("database_uri", os.getenv("DATABASE_URI", "postgresql://localhost/postgres"))
    app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Celery (in-memory broker/backend + eager tasks when mocking)
    if mock_mode:
        app.config.update(
            CELERY_BROKER_URL="memory://",
            CELERY_RESULT_BACKEND="cache+memory://",
            CELERY_TASK_ALWAYS_EAGER=True,
        )
    else:
        app.config["CELERY_BROKER_URL"] = cfg.get(
            "celery_broker_url", os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
        )
        app.config["CELERY_RESULT_BACKEND"] = cfg.get(
            "celery_result_backend", os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")
        )

    global celery_app
    celery_app = make_celery(app)

    # Initialize extensions
    db.init_app(app)
    api = Api(app, prefix="/api/v1")

    # Import and register resources lazily to avoid circular import
    from .api.v1.namespace import NamespaceResource
    from .api.v1.job import JobStatusResource

    # Routes follow /<resource_type>/<action> pattern via arguments
    api.add_resource(NamespaceResource, "/ns/<string:action>")
    api.add_resource(JobStatusResource, "/jobs/<string:job_id>")

    # Serve swagger.yaml
    from flask import send_from_directory

    @app.route("/swagger.yaml")
    def swagger_spec():
        root_dir = Path(__file__).resolve().parent.parent
        return send_from_directory(root_dir, "swagger.yaml")

    # Ensure DB tables exist in mock / dev environments
    with app.app_context():
        db.create_all()

    return app
