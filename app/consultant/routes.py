from flask import render_template
from flask_login import current_user, login_required

from . import consultant_bp


@consultant_bp.route("/")
@login_required
def index():
    if current_user.has_role("Lawyer") or current_user.has_role("Consultant"):
        return render_template("consultant/dashboard.html")
    return render_template("errors/403.html"), 403
