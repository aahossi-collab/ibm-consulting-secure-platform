from functools import wraps

from flask import abort, g
from flask_login import current_user

from app.models import Permission, Role

ROLE_CLIENT = "client"
ROLE_ADMINISTRATOR = "administrator"

PERMISSION_VIEW_CASE = "view_case"
PERMISSION_UPLOAD_DOCUMENT = "upload_document"
PERMISSION_MANAGE_USERS = "manage_users"
PERMISSION_MANAGE_CASES = "manage_cases"
PERMISSION_MANAGE_DOCUMENTS = "manage_documents"

SYSTEM_PERMISSIONS = {
    PERMISSION_VIEW_CASE,
    PERMISSION_UPLOAD_DOCUMENT,
    PERMISSION_MANAGE_USERS,
    PERMISSION_MANAGE_CASES,
    PERMISSION_MANAGE_DOCUMENTS,
}

SYSTEM_ROLES = {ROLE_CLIENT, ROLE_ADMINISTRATOR}


class RbacManager:
    @staticmethod
    def init_app(app):
        app.before_request(RbacManager._load_user_permissions)

    @staticmethod
    def _load_user_permissions():
        g.rbac_roles = set()
        g.rbac_permissions = set()

        if current_user.is_authenticated:
            g.rbac_roles = {role.name for role in current_user.roles}
            g.rbac_permissions = {
                permission.name
                for role in current_user.roles
                for permission in role.permissions
            }

    @staticmethod
    def get_user_roles(user):
        if not user:
            return set()
        return {role.name for role in user.roles}

    @staticmethod
    def get_user_permissions(user):
        if not user:
            return set()
        return {
            permission.name
            for role in user.roles
            for permission in role.permissions
        }

    @staticmethod
    def has_role(user, role_name: str) -> bool:
        return role_name in RbacManager.get_user_roles(user)

    @staticmethod
    def has_permission(user, permission_name: str) -> bool:
        return permission_name in RbacManager.get_user_permissions(user)

    @staticmethod
    def require_role(*role_names):
        def wrapper(fn):
            @wraps(fn)
            def decorated(*args, **kwargs):
                if not current_user.is_authenticated:
                    abort(403)

                if not any(RbacManager.has_role(current_user, role) for role in role_names):
                    abort(403)

                return fn(*args, **kwargs)

            return decorated

        return wrapper

    @staticmethod
    def require_permission(permission_name):
        def wrapper(fn):
            @wraps(fn)
            def decorated(*args, **kwargs):
                if not current_user.is_authenticated:
                    abort(403)

                if not RbacManager.has_permission(current_user, permission_name):
                    abort(403)

                return fn(*args, **kwargs)

            return decorated

        return wrapper

    @staticmethod
    def require_any_permission(*permission_names):
        def wrapper(fn):
            @wraps(fn)
            def decorated(*args, **kwargs):
                if not current_user.is_authenticated:
                    abort(403)

                if not any(
                    RbacManager.has_permission(current_user, permission)
                    for permission in permission_names
                ):
                    abort(403)

                return fn(*args, **kwargs)

            return decorated

        return wrapper


def require_role(*role_names):
    return RbacManager.require_role(*role_names)


def require_permission(permission_name):
    return RbacManager.require_permission(permission_name)


def require_any_permission(*permission_names):
    return RbacManager.require_any_permission(*permission_names)


def current_permissions():
    return getattr(g, "rbac_permissions", set())


def current_roles():
    return getattr(g, "rbac_roles", set())
