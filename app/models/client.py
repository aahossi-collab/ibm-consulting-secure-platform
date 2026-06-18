from app.extensions import db
from .base import BaseModel


class Client(BaseModel):
    __tablename__ = "clients"

    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(60), nullable=True)
    address = db.Column(db.Text, nullable=True)

    cases = db.relationship(
        "Case",
        back_populates="client",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    contact_messages = db.relationship(
        "ContactMessage",
        back_populates="client",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
