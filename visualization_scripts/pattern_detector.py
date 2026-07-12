import json

from llm_client import call_openai
from prompts import PATTERN_DETECTION_PROMPT


def local_pattern_fallback(conversation_history):
    """Build a transparent, displayable scaffold when the model is unavailable."""
    teacher_text = " ".join(
        str(item.get("content", "")).lower()
        for item in conversation_history
        if item.get("role") == "user"
    )
    behavior_counts = {
        "A1_context_sharing": sum(word in teacher_text for word in ("student", "learner", "class", "课程", "学生")),
        "A2_design_request": sum(word in teacher_text for word in ("design", "activity", "plan", "设计", "活动")),
        "B2_follow_up_question": teacher_text.count("?") + teacher_text.count("？"),
        "B3_challenge": sum(word in teacher_text for word in ("but", "however", "concern", "但是", "担心")),
        "B4_evaluation": sum(word in teacher_text for word in ("because", "better", "criteria", "因为", "标准")),
        "B5_explanation": sum(word in teacher_text for word in ("because", "why", "因为", "为何")),
        "C1_metacognitive_regulation": sum(word in teacher_text for word in ("reflect", "revise", "reflect", "反思", "调整")),
    }
    return {
        "pattern": "unknown",
        "confidence": 0.0,
        "evidence": "Local fallback based on the visible conversation; no API analysis was used.",
        "behavior_counts": behavior_counts,
        "stage_counts": {},
        "trigger_scaffold": True,
        "visualization_type": "radar",
        "reflection_prompt": "This chart is a local fallback. What part of the design would you like to examine next?",
    }


def detect_interaction_pattern(conversation_history, api_key=None):
    conversation_text = json.dumps(
        conversation_history,
        ensure_ascii=False,
        indent=2
    )

    result_text = call_openai(
        system_prompt=PATTERN_DETECTION_PROMPT,
        user_input=conversation_text,
        api_key=api_key,
    )

    try:
        pattern_result = json.loads(result_text)
    except json.JSONDecodeError:
        pattern_result = {
            "pattern": "unknown",
            "confidence": 0.0,
            "evidence": result_text,
            "scores": {
                "planning": 0,
                "monitoring": 0,
                "evaluation": 0,
                "strategy_adjustment": 0
            },
            "trigger_scaffold": False,
            "visualization_type": "none",
            "reflection_prompt": ""
        }

    return pattern_result
