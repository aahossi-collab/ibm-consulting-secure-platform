from flask import render_template
from flask_login import login_required

from app.security.rbac import require_role, ROLE_ADMINISTRATOR
from app.services.admin_service import AdminService
from . import admin_bp


@admin_bp.route("/")
@login_required
@require_role(ROLE_ADMINISTRATOR)
def dashboard():
    stats = AdminService.statistics()
    users = AdminService.list_users()
    roles = AdminService.list_roles()
    permissions = AdminService.list_permissions()
    audit_logs = AdminService.list_audit_logs(limit=50)
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        users=users,
        roles=roles,
        permissions=permissions,
        audit_logs=audit_logs,
    )
