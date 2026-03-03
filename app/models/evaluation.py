# @Version :1.0
# @Author  : Mingyue
# @File    : evaluation.py.py
# @Time    : 02/03/2026 19:45
from datetime import datetime
from app.db import db


class Evaluation(db.Model):
    __tablename__ = "evaluations"

    id = db.Column(db.Integer, primary_key=True)
    generation_id = db.Column(db.Integer, db.ForeignKey("generations.id"), nullable=False)
    result = db.Column(db.String(50), nullable=False)  # correct, partially_correct, failed
    error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "generation_id": self.generation_id,
            "result": self.result,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
        }