"""Map interaction patterns to visual and metacognitive scaffolds."""

from srl_profile import build_srl_profile


TACTICS = {
    "cognitive_offloading": (
        "如果你准备再次请 AI 直接生成完整方案，那么先要求它列出两项方案局限，"
        "并由你说明哪一项最影响当前教学情境。"
    ),
    "superficial_interaction": (
        "在接受下一项建议前，先用一句话判断：它如何满足你最初设定的学习者、目标或约束？"
    ),
    "goal_misalignment": (
        "先暂停当前细节争论，重新写下一个共同标准：这个活动最需要让学生达成什么？"
        "再请 AI 按该标准提出两个备选方案。"
    ),
    "critical_reasoning_synergy": (
        "继续保持“提出标准—检验建议—说明取舍”的循环；下一轮请明确写出你将采用的判断标准。"
    ),
    "default": (
        "下一轮对话前，请先写出一个教学目标或约束，并在 AI 回复后说明你采用或拒绝建议的理由。"
    ),
}


def select_scaffold(pattern_result):
    """Always return a displayable visualisation plus an SRL action scaffold."""
    pattern = pattern_result.get("pattern", "unknown")
    behavior_counts = pattern_result.get("behavior_counts", {}) or {}
    stage_counts = pattern_result.get("stage_counts", {}) or {}
    profile = build_srl_profile(pattern, behavior_counts)
    reflection_prompt = pattern_result.get("reflection_prompt") or (
        "从当前互动过程来看，下一轮你希望优先加强任务定义、监控、评价，还是调节策略？"
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
            "该剖面是基于对话行为的 SRL 过程代理指标，用于反思，不是对个人能力的诊断或常模排名。"
        ),
    }
