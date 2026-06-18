from app.extensions import db
from .base import BaseModel


class ConnectionHistory(BaseModel):
    __tablename__ = "connection_history"

    user_id = db.Column(
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    login_at = db.Column(db.DateTime, default=db.func.now(), nullable=False)
    logout_at = db.Column(db.DateTime, nullable=True)

    user = db.relationship(
        "User",
        back_populates="connection_history",
    )
