from flask import Blueprint

consultant_bp = Blueprint("consultant", __name__)

from . import routes
