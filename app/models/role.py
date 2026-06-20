from app.extensions import db
from .base import BaseModel

role_permissions = db.Table(
    "role_permissions",
    db.Column(
        "role_id",
        db.ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
    db.Column(
        "permission_id",
        db.ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
        nullable=False,
    ),
)


class Role(BaseModel):
    __tablename__ = "roles"

    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.Text, nullable=True)

    permissions = db.relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles",
        lazy="dynamic",
    )
    users = db.relationship(
        "User",
        secondary="user_roles",
        back_populates="roles",
        lazy="dynamic",
    )
