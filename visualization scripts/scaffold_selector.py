"""Choose a displayable visualization for every detected interaction.

During the prototype phase, the UI should always show a chart.  Pattern-specific
charts are retained where possible; unclear or malformed results fall back to a
radar chart constructed from the available behaviour counts.
"""


RADAR_DIMENSIONS = (
    "information_sharing",
    "design_request",
    "critical_reflection",
    "explanation",
    "metacognitive_regulation",
)


def _radar_scores(pattern_result):
    """Return complete 1--5 radar scores, deriving them from code counts if needed."""
    counts = pattern_result.get("behavior_counts", {}) or {}
    supplied_scores = pattern_result.get("radar_scores", {}) or {}
    derived_scores = {
        "information_sharing": counts.get("A1_context_sharing", 0),
        "design_request": counts.get("A2_design_request", 0),
        "critical_reflection": counts.get("B2_follow_up_question", 0) + counts.get("B3_challenge", 0),
        "explanation": counts.get("B5_explanation", 0),
        "metacognitive_regulation": counts.get("C1_metacognitive_regulation", 0),
    }

    scores = {}
    for dimension in RADAR_DIMENSIONS:
        value = supplied_scores.get(dimension, derived_scores[dimension])
        try:
            value = float(value)
        except (TypeError, ValueError):
            value = derived_scores[dimension]
        # A minimum value keeps an early/short conversation visible in the prototype.
        scores[dimension] = max(1, min(5, value))
    return scores


def select_scaffold(pattern_result):
    pattern = pattern_result.get("pattern", "unknown")
    reflection_prompt = pattern_result.get("reflection_prompt") or (
        "从这次互动的维度分布来看，下一轮你希望在哪个方面加入更多主动思考？"
    )
    behavior_counts = pattern_result.get("behavior_counts", {}) or {}

    has_count_data = any(
        isinstance(value, (int, float)) and value > 0
        for value in behavior_counts.values()
    )

    if pattern == "cognitive_offloading" and has_count_data:
        chart_type, data = "pie", behavior_counts
    elif pattern == "critical_reasoning_synergy":
        chart_type, data = "radar", _radar_scores(pattern_result)
    elif pattern == "goal_misalignment" and pattern_result.get("stage_counts"):
        chart_type, data = "stacked_bar", pattern_result["stage_counts"]
    elif pattern == "superficial_interaction" and behavior_counts:
        chart_type, data = "bar", behavior_counts
    else:
        # no_clear_pattern, unknown, parser fallbacks, and incomplete data
        # are intentionally visualized as a radar chart in this prototype.
        chart_type, data = "radar", _radar_scores(pattern_result)

    return {
        "trigger": True,
        "pattern": pattern,
        "visualization_type": chart_type,
        "data": data,
        "reflection_prompt": reflection_prompt,
    }
