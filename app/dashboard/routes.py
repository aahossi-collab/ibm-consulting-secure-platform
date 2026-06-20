from flask import redirect, render_template, url_for
from flask_login import current_user, login_required

from . import dashboard_bp


@dashboard_bp.route("/")
@login_required
def index():
    if current_user.has_role("Administrator"):
        return redirect(url_for("admin.dashboard"))

    if current_user.has_role("Lawyer") or current_user.has_role("Consultant"):
        return redirect(url_for("consultant.index"))

    if current_user.has_role("Client"):
        return redirect(url_for("client.dashboard"))

    return render_template("dashboard/no_role.html")


@dashboard_bp.route("/admin-only")
@login_required
@role_required("Administrator")
def admin_only():
    return "Si tu vois ça, le RBAC fonctionne ✅"