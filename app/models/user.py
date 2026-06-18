from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db
from .base import BaseModel
from datetime import datetime, timedelta


user_roles = db.Table(
    "user_roles",
    db.Column(
        "user_id",
        db.ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    db.Column(
        "role_id",
        db.ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
)


class User(BaseModel, UserMixin):
    __tablename__ = "users"

    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(120), nullable=True)
    last_name = db.Column(db.String(120), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    failed_login_attempts = db.Column(db.Integer, default=0, nullable=False)
    lockout_until = db.Column(db.DateTime, nullable=True)

    roles = db.relationship(
        "Role",
        secondary=user_roles,
        back_populates="users",
        lazy="joined",
    )
    connection_history = db.relationship(
        "ConnectionHistory",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    audit_logs = db.relationship(
        "AuditLog",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    administrator = db.relationship(
        "Administrator",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def increment_failed_logins(self, max_attempts: int = 5, lock_minutes: int = 15) -> None:
        self.failed_login_attempts = (self.failed_login_attempts or 0) + 1
        if self.failed_login_attempts >= max_attempts:
            self.lockout_until = datetime.utcnow() + timedelta(minutes=lock_minutes)

    def reset_failed_logins(self) -> None:
        self.failed_login_attempts = 0
        self.lockout_until = None

    @property
    def is_locked(self) -> bool:
        if self.lockout_until is None:
            return False
        return datetime.utcnow() < self.lockout_until

    @property
    def full_name(self) -> str:
        return " ".join(filter(None, [self.first_name, self.last_name]))
