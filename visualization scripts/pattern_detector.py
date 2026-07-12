import json

from llm_client import call_openai
from prompts import PATTERN_DETECTION_PROMPT


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
