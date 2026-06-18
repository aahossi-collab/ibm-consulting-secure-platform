from app.extensions import db
from .base import BaseModel


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"

    user_id = db.Column(
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    action = db.Column(db.String(255), nullable=False)
    resource_type = db.Column(db.String(120), nullable=True)
    resource_id = db.Column(db.String(255), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    event_metadata = db.Column(db.JSON, nullable=True)

    user = db.relationship(
        "User",
        back_populates="audit_logs",
    )
