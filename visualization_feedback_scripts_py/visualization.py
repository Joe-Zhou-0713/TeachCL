"""Reliable local chart rendering for the TeachCL prototype.

This module deliberately has no network or model dependency: once a scaffold is
available, the participant can always see a chart.
"""

from pathlib import Path
from uuid import uuid4

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


OUTPUT_DIR = Path(__file__).resolve().parent / "generated_charts"


def _clean_values(data):
    """Return non-negative numeric values, preserving the supplied labels."""
    return {
        str(label).replace("_", " ").title(): max(0, float(value))
        for label, value in (data or {}).items()
        if isinstance(value, (int, float))
    }


def _save(fig):
    OUTPUT_DIR.mkdir(exist_ok=True)
    path = OUTPUT_DIR / f"chart-{uuid4().hex}.png"
    fig.tight_layout()
    fig.savefig(path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return str(path)


def _radar(profile):
    current = _clean_values(profile.get("current", {}))
    reference = _clean_values(profile.get("reference", {}))
    labels = list(current) or list(reference) or ["Interaction evidence"]
    current_values = [current.get(label, 0) for label in labels]
    reference_values = [reference.get(label, 0) for label in labels]
    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(8, 6), subplot_kw={"polar": True})
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels, fontsize=9)
    ax.set_ylim(0, 5)
    ax.set_yticks(range(1, 6))
    ax.set_yticklabels([str(i) for i in range(1, 6)], fontsize=8)
    ax.plot(angles, current_values + current_values[:1], color="#2563eb", linewidth=2, label="Current interaction")
    ax.fill(angles, current_values + current_values[:1], color="#2563eb", alpha=0.18)
    ax.plot(angles, reference_values + reference_values[:1], color="#64748b", linewidth=2, linestyle="--", label="Reflection reference")
    ax.set_title("SRL process profile", pad=24, fontsize=16, fontweight="bold")
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15))
    return _save(fig)


def generate_visualization(scaffold):
    """Create a PNG for every supported scaffold, including sparse fallback data."""
    chart_type = scaffold.get("visualization_type", "bar")
    if chart_type == "radar":
        return _radar(scaffold.get("data", {}))

    values = _clean_values(scaffold.get("data", {}))
    if not values:
        values = {"Interaction evidence": 0}
    labels, numbers = list(values), list(values.values())
    fig, ax = plt.subplots(figsize=(8, 4.8))

    if chart_type == "pie" and any(numbers):
        ax.pie(numbers, labels=labels, autopct="%1.0f%%", startangle=90,
               colors=plt.cm.Blues(np.linspace(0.45, 0.85, len(numbers))))
        ax.set_title("Observed interaction pattern", fontsize=16, fontweight="bold")
    else:
        bars = ax.bar(labels, numbers, color="#2563eb")
        ax.bar_label(bars, fmt="%.0f", padding=3)
        ax.set_ylim(0, max(5, max(numbers) * 1.25))
        ax.set_ylabel("Observed instances")
        ax.set_title("Observed interaction pattern", fontsize=16, fontweight="bold")
        ax.grid(axis="y", alpha=0.25)
        ax.spines[["top", "right"]].set_visible(False)
        plt.setp(ax.get_xticklabels(), rotation=18, ha="right")

    return _save(fig)
