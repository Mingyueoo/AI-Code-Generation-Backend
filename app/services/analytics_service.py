# @Version :1.0
# @Author  : Mingyue
# @File    : analytics_service.py.py
# @Time    : 02/03/2026 19:50
import logging
import io
import base64
from collections import Counter

logger = logging.getLogger(__name__)


def get_analytics() -> dict:
    """Aggregate analytics from the database using SQLAlchemy + Pandas."""
    import pandas as pd
    from app.db import db
    from app.models import Prompt, Generation, Evaluation

    try:
        # --- Raw data ---
        prompts = db.session.query(Prompt).all()
        generations = db.session.query(Generation).all()
        evaluations = db.session.query(Evaluation).all()

        total_prompts = len(prompts)
        total_generations = len(generations)
        total_evaluations = len(evaluations)

        if total_evaluations == 0:
            return {
                "total_prompts": total_prompts,
                "total_generations": total_generations,
                "total_evaluations": 0,
                "success_rate": 0.0,
                "model_stats": {},
                "result_distribution": {},
                "common_errors": [],
                "chart_base64": None,
            }

        # --- Pandas analysis ---
        eval_data = pd.DataFrame([
            {
                "eval_id": e.id,
                "generation_id": e.generation_id,
                "result": e.result,
                "error_message": e.error_message,
            }
            for e in evaluations
        ])

        gen_data = pd.DataFrame([
            {
                "generation_id": g.id,
                "prompt_id": g.prompt_id,
                "status": g.status,
            }
            for g in generations
        ])

        prompt_data = pd.DataFrame([
            {"prompt_id": p.id, "model_name": p.model_name}
            for p in prompts
        ])

        # Merge
        merged = eval_data.merge(gen_data, on="generation_id").merge(prompt_data, on="prompt_id")

        # Success rate
        correct_count = (merged["result"] == "correct").sum()
        success_rate = round(correct_count / len(merged) * 100, 1) if len(merged) > 0 else 0.0

        # Result distribution
        result_dist = merged["result"].value_counts().to_dict()

        # Per-model stats
        model_stats = {}
        for model, group in merged.groupby("model_name"):
            total = len(group)
            correct = (group["result"] == "correct").sum()
            model_stats[model] = {
                "total": int(total),
                "correct": int(correct),
                "accuracy": round(correct / total * 100, 1) if total > 0 else 0.0,
            }

        # Common errors
        errors = merged[merged["error_message"].notna()]["error_message"].tolist()
        error_types = [e.split(":")[0] for e in errors if e]
        common_errors = [{"type": k, "count": v} for k, v in Counter(error_types).most_common(5)]

        # Chart
        chart_b64 = _generate_analytics_chart(result_dist, model_stats)

        return {
            "total_prompts": total_prompts,
            "total_generations": total_generations,
            "total_evaluations": total_evaluations,
            "success_rate": success_rate,
            "model_stats": model_stats,
            "result_distribution": result_dist,
            "common_errors": common_errors,
            "chart_base64": chart_b64,
        }

    except Exception as e:
        logger.error(f"Analytics error: {e}")
        raise


def _generate_analytics_chart(result_dist: dict, model_stats: dict) -> str | None:
    """Generate a summary chart and return as base64 PNG."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 2, figsize=(12, 5))
        fig.suptitle("AI Coding Assistant — Analytics Dashboard", fontsize=14, fontweight="bold")

        # Left: result distribution pie
        ax1 = axes[0]
        if result_dist:
            colors = {"correct": "#4CAF50", "partially_correct": "#FFC107", "failed": "#F44336"}
            pie_colors = [colors.get(k, "#90A4AE") for k in result_dist.keys()]
            ax1.pie(
                result_dist.values(),
                labels=[k.replace("_", " ").title() for k in result_dist.keys()],
                autopct="%1.1f%%",
                colors=pie_colors,
                startangle=90,
            )
            ax1.set_title("Evaluation Results")

        # Right: per-model accuracy bar
        ax2 = axes[1]
        if model_stats:
            models = list(model_stats.keys())
            accuracies = [model_stats[m]["accuracy"] for m in models]
            bar_colors = ["#2196F3", "#FF9800", "#9C27B0", "#00BCD4"]
            bars = ax2.bar(models, accuracies, color=bar_colors[: len(models)], edgecolor="white")
            ax2.bar_label(bars, labels=[f"{a:.1f}%" for a in accuracies], padding=3)
            ax2.set_ylim(0, 110)
            ax2.set_ylabel("Accuracy (%)")
            ax2.set_title("Accuracy by Model")
            ax2.spines[["top", "right"]].set_visible(False)
            ax2.tick_params(axis="x", rotation=15)

        plt.tight_layout()

        buf = io.BytesIO()
        plt.savefig(buf, format="png", dpi=130, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return base64.b64encode(buf.read()).decode("utf-8")

    except Exception as e:
        logger.error(f"Chart generation failed: {e}")
        return None