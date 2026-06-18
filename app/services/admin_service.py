"""Admin domain services for dashboard operations."""

from app.models import AuditLog, Permission, Role, User


class AdminService:
    @staticmethod
    def list_users():
        return User.query.order_by(User.created_at.desc()).all()

    @staticmethod
    def list_roles():
        return Role.query.order_by(Role.name).all()

    @staticmethod
    def list_permissions():
        return Permission.query.order_by(Permission.name).all()

    @staticmethod
    def list_audit_logs(limit=100):
        return AuditLog.query.order_by(AuditLog.created_at.desc()).limit(limit).all()

    @staticmethod
    def statistics():
        return {
            "users": User.query.count(),
            "roles": Role.query.count(),
            "permissions": Permission.query.count(),
            "audit_events": AuditLog.query.count(),
        }
