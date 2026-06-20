import os

from app import create_app
from app.extensions import db
from app.models import Permission, Role


PERMISSIONS = [
    "create_case",
    "read_case",
    "update_case",
    "delete_case",
    "upload_document",
    "download_document",
    "manage_users",
    "view_audit_logs",
]

ROLE_PERMISSIONS = {
    "Administrator": PERMISSIONS,
    "Lawyer": [
        "create_case",
        "read_case",
        "update_case",
        "upload_document",
        "download_document",
    ],
    "Consultant": [
        "read_case",
        "upload_document",
        "download_document",
    ],
    "Client": [
        "read_case",
        "download_document",
    ],
}


def get_app():
    env = os.getenv("FLASK_ENV", "development")
    return create_app(env)


def find_or_create_permission(name: str):
    permission = Permission.query.filter_by(name=name).first()
    if permission is None:
        permission = Permission(name=name)
        db.session.add(permission)
    return permission


def find_or_create_role(name: str):
    role = Role.query.filter_by(name=name).first()
    if role is None:
        role = Role(name=name)
        db.session.add(role)
    return role


def seed_permissions():
    created = 0
    permissions = {}

    for name in PERMISSIONS:
        permission = Permission.query.filter_by(name=name).first()
        if permission is None:
            permission = Permission(name=name)
            db.session.add(permission)
            created += 1
        permissions[name] = permission

    return permissions, created


def seed_roles(permissions):
    created = 0
    roles = {}

    for role_name, permission_names in ROLE_PERMISSIONS.items():
        role = Role.query.filter_by(name=role_name).first()
        if role is None:
            role = Role(name=role_name)
            db.session.add(role)
            created += 1

        role.permissions = [permissions[name] for name in permission_names]
        roles[role_name] = role

    return roles, created


def main():
    app = get_app()
    with app.app_context():
        permissions, permission_created = seed_permissions()
        roles, role_created = seed_roles(permissions)
        db.session.commit()

        print("RBAC seeding terminé")
        print(f"Permissions créées : {permission_created}")
        print(f"Rôles créés : {role_created}")
        print("Rôles et permissions configurés :")
        for role_name, role in roles.items():
            permission_names = [permission.name for permission in role.permissions]
            print(f"  - {role_name}: {', '.join(permission_names)}")


if __name__ == "__main__":
    main()
