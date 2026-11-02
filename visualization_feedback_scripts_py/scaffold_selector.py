"""Map interaction patterns to visual and metacognitive scaffolds."""

from srl_profile import build_srl_profile


TACTICS = {
    "cognitive_offloading": (
        "Before asking AI to generate another complete solution, ask it to name two limitations "
        "of its proposal and explain which limitation matters most in your teaching context."
    ),
    "superficial_interaction": (
        "Before accepting the next suggestion, state in one sentence how it meets your original "
        "learner needs, learning goal, or constraint."
    ),
    "goal_misalignment": (
        "Pause the current detail-level disagreement and restate one shared criterion: what must "
        "students achieve in this activity? Then ask AI for two alternatives that meet that criterion."
    ),
    "critical_reasoning_synergy": (
        "Continue the cycle of setting a criterion, testing a suggestion, and explaining a trade-off. "
        "In the next turn, state the criterion you will use to make your decision."
    ),
    "default": (
        "Before the next turn, write one teaching goal or constraint. After AI responds, explain "
        "why you will accept or reject its suggestion."
    ),
}


def select_scaffold(pattern_result):
    """Always return a displayable visualisation plus an SRL action scaffold."""
    pattern = pattern_result.get("pattern", "unknown")
    behavior_counts = pattern_result.get("behavior_counts", {}) or {}
    stage_counts = pattern_result.get("stage_counts", {}) or {}
    profile = build_srl_profile(pattern, behavior_counts)
    reflection_prompt = pattern_result.get("reflection_prompt") or (
        "In the next turn, would you most like to strengthen task definition, monitoring, "
        "evaluation, or metacognitive regulation?"
    )

    has_count_data = any(
        isinstance(value, (int, float)) and value > 0
        for value in behavior_counts.values()
    )

    if pattern == "cognitive_offloading" and has_count_data:
        chart_type, data = "pie", behavior_counts
    elif pattern == "critical_reasoning_synergy":
        chart_type, data = "radar", profile
    elif pattern == "goal_misalignment" and stage_counts:
        chart_type, data = "stacked_bar", stage_counts
    elif pattern == "superficial_interaction" and behavior_counts:
        chart_type, data = "bar", behavior_counts
    else:
        # Short, unclear, or malformed results still receive a transparent SRL
        # profile rather than being hidden from the user.
        chart_type, data = "radar", profile

    return {
        "trigger": True,
        "pattern": pattern,
        "visualization_type": chart_type,
        "data": data,
        "srl_profile": profile,
        "reflection_prompt": reflection_prompt,
        "actionable_tactic": TACTICS.get(pattern, TACTICS["default"]),
        "theory_note": (
            "This profile is a behavioural SRL process indicator for reflection. It is not a diagnosis "
            "of personal ability or a normative ranking."
        ),
    }
