"""Authentication-related service helpers.

Keep business logic (user creation, lookup) here so routes remain thin.
"""
from typing import Optional

from app.extensions import db
from app.models import User


class AuthService:
    @staticmethod
    def find_by_email(email: str) -> Optional[User]:
        if not email:
            return None
        return User.query.filter_by(email=email.lower().strip()).first()

    @staticmethod
    def create_user(email: str, password: str, first_name: str = None, last_name: str = None) -> User:
        email_norm = (email or "").lower().strip()
        if AuthService.find_by_email(email_norm):
            raise ValueError("email_exists")

        user = User(email=email_norm, first_name=first_name, last_name=last_name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user
