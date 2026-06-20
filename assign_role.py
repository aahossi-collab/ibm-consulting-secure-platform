import sys
from app import create_app
from app.extensions import db
from app.models import User, Role


def assign_role(email, role_name):
    user = User.query.filter_by(email=email).first()
    if not user:
        print(f"Utilisateur introuvable : {email}")
        return

    role = Role.query.filter_by(name=role_name).first()
    if not role:
        print(f"Rôle introuvable : {role_name}")
        return

    if role in user.roles:
        print(f"{email} a déjà le rôle {role_name}")
        return

    user.roles.append(role)
    db.session.commit()
    print(f"Rôle '{role_name}' assigné à {email}")


if __name__ == "__main__":
    app = create_app()
    with app.app_context():
        email = sys.argv[1]
        role_name = sys.argv[2]
        assign_role(email, role_name)