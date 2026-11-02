import time
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


LABELS = {
    "task_definition": "Task\ndefinition",
    "planning_and_control": "Planning &\ncontrol",
    "monitoring": "Monitoring",
    "evaluation_and_justification": "Evaluation &\njustification",
    "metacognitive_regulation": "Metacognitive\nregulation",
}


def _closed_values(profile, labels):
    values = [profile.get(label, 0) for label in labels]
    return values + values[:1]


def draw_radar_chart(profile_data, title="SRL Process Profile"):
    """Draw current SRL indicators against a transparent design reference."""
    if "current" in profile_data:
        current = profile_data.get("current", {})
        reference = profile_data.get("reference", {})
    else:
        current = profile_data
        reference = None

    labels = list(current.keys()) or list(LABELS)
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    closed_angles = angles + angles[:1]

    output_dir = Path(__file__).resolve().parents[1] / "outputs"
    output_dir.mkdir(exist_ok=True)
    path = output_dir / f"radar_chart_{int(time.time() * 1000)}.png"

    fig, ax = plt.subplots(figsize=(7.2, 6.4), subplot_kw={"polar": True})
    ax.plot(closed_angles, _closed_values(current, labels), linewidth=2.4, color="#2F6B9A", label="Current interaction")
    ax.fill(closed_angles, _closed_values(current, labels), color="#2F6B9A", alpha=0.20)

    if reference:
        ax.plot(
            closed_angles,
            _closed_values(reference, labels),
            linewidth=2,
            linestyle="--",
            color="#D97706",
            label="Prototype reference",
        )

    ax.set_xticks(angles)
    ax.set_xticklabels([LABELS.get(label, label.replace("_", " ").title()) for label in labels])
    ax.set_ylim(0, 5)
    ax.set_yticks([1, 2, 3, 4, 5])
    ax.set_title(title, size=14, pad=24)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=2, frameon=False)
    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)
    return str(path)
