import logging
from flask import Flask, jsonify, Response, send_from_directory
from werkzeug.exceptions import HTTPException
from app.config import Config
from app.db import Base, close_db, init_db
from app.models import User, Task  # noqa: F401
from app.openapi import OPENAPI
from app.routes.auth import bp as auth_bp
from app.routes.health import bp as health_bp
from app.routes.tasks import bp as tasks_bp
from app.utils.errors import ApiError


def create_app(config_overrides=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)
    if app.config["JWT_SECRET_KEY"] == "dev-only-change-this-secret" and not app.config.get("TESTING"):
        app.logger.warning("Using development JWT secret. Set JWT_SECRET_KEY in production.")

    init_db(app.config["DATABASE_URL"])
    Base.metadata.create_all(bind=__import__("app.db", fromlist=["engine"]).engine)
    app.teardown_appcontext(close_db)
    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(health_bp)

    @app.get("/")
    def frontend():
        return send_from_directory(app.static_folder, "index.html")

    @app.get("/openapi.json")
    def openapi():
        return jsonify(OPENAPI)

    @app.get("/api/docs")
    def docs():
        html = """<!doctype html>
<html><head><title>Task API Docs</title><link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css"></head>
<body><div id="swagger-ui"></div><script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
<script>window.ui=SwaggerUIBundle({url:'/openapi.json',dom_id:'#swagger-ui'});</script></body></html>"""
        return Response(html, mimetype="text/html")

    @app.errorhandler(ApiError)
    def handle_api_error(e):
        body = {"error": {"code": e.code, "message": e.message}}
        if e.details:
            body["error"]["details"] = e.details
        return jsonify(body), e.status

    @app.errorhandler(HTTPException)
    def handle_http_error(e):
        codes = {404: "not_found", 405: "method_not_allowed", 415: "unsupported_media_type"}
        return jsonify({"error": {"code": codes.get(e.code, "http_error"), "message": e.description}}), e.code

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        app.logger.exception("Unhandled error: %s", e)
        return jsonify({"error": {"code": "internal_error", "message": "Internal server error"}}), 500

    logging.basicConfig(level=logging.INFO)
    return app
