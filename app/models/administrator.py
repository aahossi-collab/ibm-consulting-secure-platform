from app.extensions import db
from .base import BaseModel


class Administrator(BaseModel):
    __tablename__ = "administrators"

    user_id = db.Column(
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    department = db.Column(db.String(120), nullable=True)
    active = db.Column(db.Boolean, default=True, nullable=False)

    user = db.relationship(
        "User",
        back_populates="administrator",
        uselist=False,
    )
