import json
from pathlib import Path
from datetime import datetime, timezone


def _format_timestamp(timestamp):
    """Convert an ISO timestamp to a readable UTC timestamp."""
    if not timestamp:
        return "Timestamp unavailable"

    try:
        return datetime.fromisoformat(timestamp).astimezone(
            timezone.utc
        ).strftime("%Y-%m-%d %H:%M:%S UTC")
    except (ValueError, TypeError):
        return str(timestamp)



def save_conversation(
    conversation_history,
    session_id,
    output_dir="outputs",
):
    """
    Save the current conversation as JSON and Markdown.

    The files are updated with the complete conversation history
    whenever this function is called.
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    conversation_data = {
        "session_id": session_id,
        "exported_at": datetime.now(timezone.utc).isoformat(),
        "messages": conversation_history,
    }

    # Structured format for research analysis
    json_path = output_path / f"conversation_{session_id}.json"

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(
            conversation_data,
            file,
            ensure_ascii=False,
            indent=2,
        )

    # Readable format for researchers
    md_path = output_path / f"conversation_{session_id}.md"

    lines = [
        f"# Conversation Log",
        "",
        f"- Session ID: `{session_id}`",
        f"- Exported at: {_format_timestamp(conversation_data['exported_at'])}",
        "",
        "---",
        "",
    ]

    for index, message in enumerate(conversation_history, start=1):
        role = message.get("role", "unknown")
        content = message.get("content", "")
        timestamp = _format_timestamp(message.get("timestamp"))

        if role == "user":
            role_label = "Participant"
        elif role == "assistant":
            role_label = "AI Assistant"
        else:
            role_label = role

        lines.extend([
            f"## Message {index} — {role_label}",
            "",
            f"*Timestamp: {timestamp}*",
            "",
            str(content),
            "",
            "---",
            "",
        ])

    with md_path.open("w", encoding="utf-8") as file:
        file.write("\n".join(lines))

    return {
        "json_path": str(json_path),
        "markdown_path": str(md_path),
    }
