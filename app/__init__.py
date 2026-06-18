import os
from flask import Flask

from config import config_by_name
from .extensions import csrf, db, login_manager, migrate, limiter
from .auth import auth_bp
from .public import public_bp
from .client import client_bp
from .admin import admin_bp
from . import models


def create_app(config_name=None):
    config_name = config_name or os.getenv("FLASK_ENV", "development")
    config_class = config_by_name.get(config_name, config_by_name["development"])

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_class)

    register_extensions(app)
    register_blueprints(app)

    return app


def register_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    login_manager.login_view = app.config.get("LOGIN_VIEW")
    login_manager.session_protection = "strong"

    from app.models import User

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)


def register_blueprints(app):
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(client_bp, url_prefix="/client")
    app.register_blueprint(admin_bp, url_prefix="/admin")
