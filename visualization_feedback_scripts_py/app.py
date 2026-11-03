"""Streamlit entry point for the TeachCL lesson-plan co-design assistant."""

import uuid
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st

from conversation_export import render_conversation_text, save_analysis, save_conversation
from feedback_generator import generate_feedback
from interaction_tracker import CODE_LABELS, code_interaction
from llm_client import MODEL_NAME, call_openai, conversation_input
from pattern_detector import detect_interaction_pattern
from prompts import CHATBOT_PROMPT
from scaffold_selector import select_scaffold
from visualization import generate_visualization


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"

st.set_page_config(page_title="TeachCL Co-design Assistant", layout="centered")
st.title("TeachCL Co-design Assistant")
st.caption("Co-design a lesson plan with AI, then review observable interaction evidence.")

defaults = {
    "conversation_history": [],
    "research_session_id": uuid.uuid4().hex,
    "analysis": None,
    "chart_path": None,
    "api_key": "",
}
for key, default in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = default


with st.sidebar:
    st.header("Connection")
    st.caption(f"Model: `{MODEL_NAME}`")
    api_key = st.text_input(
        "OpenAI API key", type="password", key="api_key", placeholder="sk-...",
        help="Used for this browser session and not written to project files.",
    )
    if st.button("Start a new conversation"):
        st.session_state.conversation_history = []
        st.session_state.research_session_id = uuid.uuid4().hex
        st.session_state.analysis = None
        st.session_state.chart_path = None
        st.rerun()
    st.caption("Conversation logs and analysis are saved under `outputs/` on this machine.")


for message in st.session_state.conversation_history:
    if message.get("role") in {"user", "assistant"}:
        with st.chat_message(message["role"]):
            st.markdown(message.get("content", ""))

if not api_key:
    st.info("Enter your OpenAI API key in the sidebar to start.")

user_input = st.chat_input("Share your instructional design ideas…", disabled=not api_key)
if user_input:
    st.session_state.analysis = None
    st.session_state.chart_path = None
    timestamp = datetime.now(timezone.utc).isoformat()
    st.session_state.conversation_history.append({
        "role": "user", "content": user_input, "timestamp": timestamp,
    })
    with st.chat_message("user"):
        st.markdown(user_input)
    save_conversation(st.session_state.conversation_history, st.session_state.research_session_id, OUTPUT_DIR)
    try:
        with st.chat_message("assistant"):
            with st.spinner("Preparing a response…"):
                reply = call_openai(
                    system_prompt=CHATBOT_PROMPT,
                    user_input=conversation_input(st.session_state.conversation_history),
                    api_key=api_key,
                )
            st.markdown(reply)
        st.session_state.conversation_history.append({
            "role": "assistant", "content": reply,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        st.session_state.analysis = None
        st.session_state.chart_path = None
        save_conversation(st.session_state.conversation_history, st.session_state.research_session_id, OUTPUT_DIR)
    except Exception as error:
        st.error(f"Could not generate a response: {error}")

if st.session_state.conversation_history:
    st.download_button(
        "Download conversation transcript (.txt)",
        data=render_conversation_text(
            st.session_state.conversation_history,
            st.session_state.research_session_id,
        ),
        file_name=f"conversation_{st.session_state.research_session_id}.txt",
        mime="text/plain",
        help="Save a plain-text copy on your device for later analysis.",
    )
    
st.divider()
st.subheader("Review this collaboration")
st.write("Analyze teacher interaction codes, identify a session-level interaction pattern, and generate a reflective feedback prompt.")
has_teacher_turn = any(m.get("role") == "user" for m in st.session_state.conversation_history)
if st.button("Analyze and generate visualization", disabled=not api_key or not has_teacher_turn):
    st.session_state.analysis = None
    st.session_state.chart_path = None
    try:
        with st.spinner("Coding the conversation and preparing feedback…"):
            history = st.session_state.conversation_history
            coding = code_interaction(history, api_key=api_key)
            pattern = detect_interaction_pattern(history, coding_result=coding, api_key=api_key)
            scaffold = select_scaffold(coding, pattern)
            chart_path = generate_visualization(scaffold)
            feedback = generate_feedback(
                conversation_history=history,
                pattern_result=pattern,
                interaction_codes=coding,
                api_key=api_key,
            )
            analysis = {
                "coding": coding,
                "pattern": pattern,
                "feedback": feedback,
                "visualization": {
                    "type": scaffold["visualization_type"],
                    "path": str(Path(chart_path).relative_to(BASE_DIR)),
                    "code_counts": scaffold["data"],
                },
                "reflection_prompt": scaffold["reflection_prompt"],
                "suggested_next_move": scaffold["actionable_tactic"],
            }
            save_analysis(analysis, st.session_state.research_session_id, OUTPUT_DIR)
            st.session_state.analysis = analysis
            st.session_state.chart_path = chart_path
    except Exception as error:
        st.error(f"Analysis could not be completed: {error}")


analysis = st.session_state.analysis
if analysis:
    st.divider()
    st.subheader("Interaction pattern")
    st.markdown(f"**{analysis['pattern']['pattern_label']}** · confidence {analysis['pattern']['confidence']:.0%}")
    if analysis["pattern"].get("evidence"):
        st.write(analysis["pattern"]["evidence"])

    st.subheader("Coding frequency")
    if st.session_state.chart_path and Path(st.session_state.chart_path).exists():
        st.image(st.session_state.chart_path, use_container_width=True)
    count_cols = st.columns(3)
    counts = analysis["coding"]["code_counts"]
    for index, (code, label) in enumerate(CODE_LABELS.items()):
        with count_cols[index % len(count_cols)]:
            st.metric(f"{code} · {label}", counts.get(code, 0))
    st.caption("Codes can co-occur on one teacher turn. Frequencies describe this conversation and are not a rating of teacher ability.")

    st.subheader("Feedback on our collaboration")
    feedback = analysis["feedback"]
    st.markdown(feedback["feedback"])
    if not feedback["validation"]["is_valid"]:
        st.caption("Formatting note: " + " ".join(feedback["validation"]["errors"]))
    if analysis.get("reflection_prompt"):
        st.info(analysis["reflection_prompt"])
    st.write("**Suggested next move:** " + analysis["suggested_next_move"])
    st.caption("The chart shows descriptive coding evidence. Use the feedback as a reflection aid; instructional decisions remain with the teacher.")

