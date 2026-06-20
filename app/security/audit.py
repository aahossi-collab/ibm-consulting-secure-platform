import uuid
from typing import Any, Dict, Optional

from flask import has_request_context, request

from app.extensions import db
from app.models.audit_log import AuditLog


class AuditLogger:
    @staticmethod
    def init_app(app):
        return None

    @staticmethod
    def log_event(
        action: str,
        user_id: Optional[uuid.UUID] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        event_metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        if ip_address is None and has_request_context():
            ip_address = request.remote_addr

        event = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            ip_address=ip_address,
            event_metadata=event_metadata or {},
        )

        db.session.add(event)
        db.session.commit()

        return event

    @staticmethod
    def log_login_success(user, ip_address: Optional[str] = None):
        return AuditLogger.log_event(
            action="login_success",
            user_id=getattr(user, "id", None),
            ip_address=ip_address,
        )

    @staticmethod
    def log_login_failure(email: str, ip_address: Optional[str] = None):
        return AuditLogger.log_event(
            action="login_failure",
            resource_type="user",
            resource_id=email,
            ip_address=ip_address,
            event_metadata={"email": email},
        )

    @staticmethod
    def log_logout(user, ip_address: Optional[str] = None):
        return AuditLogger.log_event(
            action="logout",
            user_id=getattr(user, "id", None),
            ip_address=ip_address,
        )

    @staticmethod
    def log_user_created(user, ip_address: Optional[str] = None):
        return AuditLogger.log_event(
            action="user_created",
            user_id=getattr(user, "id", None),
            resource_type="user",
            resource_id=str(getattr(user, "id", "")),
            ip_address=ip_address,
            event_metadata={"email": getattr(user, "email", None)},
        )

    @staticmethod
    def log_role_changed(user, old_roles, new_roles, ip_address: Optional[str] = None):
        return AuditLogger.log_event(
            action="role_changed",
            user_id=getattr(user, "id", None),
            resource_type="user",
            resource_id=str(getattr(user, "id", "")),
            ip_address=ip_address,
            event_metadata={
                "old_roles": list(old_roles),
                "new_roles": list(new_roles),
            },
        )

    @staticmethod
    def log_document_uploaded(user, document_id, ip_address: Optional[str] = None):
        return AuditLogger.log_event(
            action="document_uploaded",
            user_id=getattr(user, "id", None),
            resource_type="document",
            resource_id=str(document_id),
            ip_address=ip_address,
        )

    @staticmethod
    def log_document_downloaded(user, document_id, ip_address: Optional[str] = None):
        return AuditLogger.log_event(
            action="document_downloaded",
            user_id=getattr(user, "id", None),
            resource_type="document",
            resource_id=str(document_id),
            ip_address=ip_address,
        )

    @staticmethod
    def log_document_deleted(user, document_id, ip_address: Optional[str] = None):
        return AuditLogger.log_event(
            action="document_deleted",
            user_id=getattr(user, "id", None),
            resource_type="document",
            resource_id=str(document_id),
            ip_address=ip_address,
        )

    @staticmethod
    def log_password_reset_request(email: str, ip_address: Optional[str] = None):
        return AuditLogger.log_event(
            action="password_reset_requested",
            resource_type="user",
            resource_id=email,
            ip_address=ip_address,
            event_metadata={"email": email},
        )

    @staticmethod
    def log_password_reset_completed(user, ip_address: Optional[str] = None):
        return AuditLogger.log_event(
            action="password_reset_completed",
            user_id=getattr(user, "id", None),
            ip_address=ip_address,
        )

    @staticmethod
    def log_account_lockout(user, ip_address: Optional[str] = None):
        return AuditLogger.log_event(
            action="account_lockout",
            user_id=getattr(user, "id", None),
            ip_address=ip_address,
        )
