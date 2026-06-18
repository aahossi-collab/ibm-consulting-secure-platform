from flask import render_template
from . import public_bp


@public_bp.route("/")
def index():
    return render_template("public/index.html")
