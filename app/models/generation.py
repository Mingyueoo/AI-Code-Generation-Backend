# @Version :1.0
# @Author  : Mingyue
# @File    : generation.py.py
# @Time    : 02/03/2026 19:44
from datetime import datetime
from app.db import db


class Generation(db.Model):
    __tablename__ = "generations"

    id = db.Column(db.Integer, primary_key=True)
    prompt_id = db.Column(db.Integer, db.ForeignKey("prompts.id"), nullable=False)
    generated_code = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default="pending")  # pending, generated, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    evaluations = db.relationship("Evaluation", backref="generation", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        latest_eval = self.evaluations[-1] if self.evaluations else None
        return {
            "id": self.id,
            "prompt_id": self.prompt_id,
            "generated_code": self.generated_code,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "evaluation": latest_eval.to_dict() if latest_eval else None,
        }