# @Version :1.0
# @Author  : Mingyue
# @File    : seed_data.py.py
# @Time    : 02/03/2026 20:34
"""
Seed the database with sample prompts, generations, and evaluations
for a realistic demo experience.

Run with: python seed_data.py
"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app.app import create_app
from app.db import db
from app.models import Prompt, Generation, Evaluation
from app.services import model_service, evaluation_service

SEED_PROMPTS = [
    ("plot a bar chart of monthly sales", "mock-gpt"),
    ("draw a scatter plot with correlation", "mock-gpt"),
    ("create a pie chart for budget breakdown", "mock-codellama"),
    ("show a histogram of exam scores", "mock-gpt"),
    ("plot a horizontal bar chart of product revenue", "mock-codellama"),
    ("draw a heatmap of correlation matrix", "mock-gpt"),
    ("create a line chart with two series", "mock-gpt"),
    ("plot a pie chart of programming languages", "mock-codellama"),
]


def seed():
    app = create_app()
    with app.app_context():
        print("🌱 Seeding database...")

        for prompt_text, model_name in SEED_PROMPTS:
            prompt = Prompt(prompt_text=prompt_text, model_name=model_name)
            db.session.add(prompt)
            db.session.flush()

            try:
                code = model_service.generate_code(prompt_text, model_name)
                gen = Generation(prompt_id=prompt.id, generated_code=code, status="generated")
                db.session.add(gen)
                db.session.flush()

                result = evaluation_service.evaluate_code(code)
                ev = Evaluation(generation_id=gen.id, **result)
                db.session.add(ev)
            except Exception as e:
                gen = Generation(prompt_id=prompt.id, status="failed")
                db.session.add(gen)
                print(f"  ⚠️  {prompt_text}: {e}")

        db.session.commit()
        print(f"✅  Seeded {len(SEED_PROMPTS)} prompts successfully.\n")
        print("👉  Open http://localhost:5000 to explore the dashboard!\n")


if __name__ == "__main__":
    seed()