# @Version :1.0
# @Author  : Mingyue
# @File    : prompt.py.py
# @Time    : 02/03/2026 19:43
from datetime import datetime
from app.db import db


class Prompt(db.Model):
    __tablename__ = "prompts"

    id = db.Column(db.Integer, primary_key=True)
    prompt_text = db.Column(db.Text, nullable=False)
    model_name = db.Column(db.String(100), nullable=False, default="mock-gpt")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    generations = db.relationship("Generation", backref="prompt", lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "prompt_text": self.prompt_text,
            "model_name": self.model_name,
            "created_at": self.created_at.isoformat(),
            "generation_count": len(self.generations),
        }