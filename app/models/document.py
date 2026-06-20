from app.extensions import db
from .base import BaseModel


class Document(BaseModel):
    __tablename__ = "documents"

    title = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    storage_path = db.Column(db.String(500), nullable=False)
    mime_type = db.Column(db.String(120), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    version = db.Column(db.Integer, nullable=False, default=1)
    confidential = db.Column(db.Boolean, default=False, nullable=False)
    parent_id = db.Column(
        db.ForeignKey("documents.id", ondelete="SET NULL"), nullable=True
    )

    case_id = db.Column(
        db.ForeignKey("cases.id", ondelete="CASCADE"),
        nullable=False,
    )
    case = db.relationship(
        "Case",
        back_populates="documents",
    )
    parent = db.relationship(
        "Document",
        remote_side=lambda: [Document.id],
        backref="revisions",
    )
