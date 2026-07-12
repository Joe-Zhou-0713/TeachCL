import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import time

def draw_radar_chart(scores, title="Self-Regulated Learning Profile"):
    labels = list(scores.keys())
    values = list(scores.values())

    output_dir = Path(__file__).resolve().parents[1] / "outputs"
    output_dir.mkdir(exist_ok=True)

    path = output_dir / f"radar_chart_{int(time.time() * 1000)}.png"


    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()

    values += values[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))

    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.25)

    ax.set_xticks(angles[:-1])
    ax.set_xticklabels([label.replace("_", " ") for label in labels])

    ax.set_ylim(0, 5)
    ax.set_title(title, size=14, pad=20)





    fig.tight_layout()
    fig.savefig(path, dpi=160, bbox_inches="tight")
    plt.close(fig)

    return str(path)

 #   plt.show()

# scores = {
#     "Planning": 3,
#     "Monitoring": 2,
#     "Evaluation": 4,
#     "Strategy Adjustment": 1,
#     "Motivation": 3
# }

# draw_radar_chart(scores)
