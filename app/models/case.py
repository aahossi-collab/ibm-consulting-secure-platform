from app.extensions import db
from .base import BaseModel


class Case(BaseModel):
    __tablename__ = "cases"

    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(80), nullable=False, default="new")

    client_id = db.Column(
        db.ForeignKey("clients.id", ondelete="CASCADE"),
        nullable=False,
    )
    client = db.relationship(
        "Client",
        back_populates="cases",
    )

    documents = db.relationship(
        "Document",
        back_populates="case",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
