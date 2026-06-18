from app.extensions import db
from .base import BaseModel


class ContactMessage(BaseModel):
    __tablename__ = "contact_messages"

    client_id = db.Column(
        db.ForeignKey("clients.id", ondelete="SET NULL"),
        nullable=True,
    )
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.String(255), nullable=True)
    message = db.Column(db.Text, nullable=False)
    received_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)

    client = db.relationship(
        "Client",
        back_populates="contact_messages",
    )
