from app.extensions import db
from .base import BaseModel


class Permission(BaseModel):
    __tablename__ = "permissions"

    name = db.Column(db.String(120), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    roles = db.relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions",
        lazy="dynamic",
    )
