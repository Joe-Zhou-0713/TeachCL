import streamlit as st

from llm_client import call_openai
from pattern_detector import detect_interaction_pattern
from prompts import CHATBOT_PROMPT
from scaffold_selector import select_scaffold
from visualization import generate_visualization


st.set_page_config(page_title="TeachCL Co-design Assistant", layout="centered")
st.title("TeachCL Co-design Assistant")

for key, default in {
    "conversation_history": [],
    "latest_scaffold": None,
    "latest_chart_path": None,
    "latest_profile_path": None,
    "visualization_message": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default


with st.sidebar:
    st.header("Connection")
    if st.button("Clear chat and API key"):
        for key in (
            "conversation_history",
            "latest_scaffold",
            "latest_chart_path",
            "latest_profile_path",
            "visualization_message",
            "api_key",
        ):
            st.session_state.pop(key, None)
        st.rerun()

    api_key = st.text_input(
        "OpenAI API key",
        type="password",
        key="api_key",
        placeholder="sk-...",
        help="Used only for this browser session. It is not written to this app's files.",
    )
    st.caption("Your key is used only to make requests on your behalf and is not saved.")


for message in st.session_state.conversation_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])


if not api_key:
    st.info("Enter your OpenAI API key in the sidebar to start the chatbot.")

user_input = st.chat_input(
    "Please share your instructional design ideas...",
    disabled=not api_key,
)
if user_input:
    st.session_state.conversation_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Generating response..."):
                ai_reply = call_openai(
                    system_prompt=CHATBOT_PROMPT,
                    user_input=str(st.session_state.conversation_history),
                    api_key=api_key,
                )
            st.write(ai_reply)
            st.session_state.conversation_history.append(
                {"role": "assistant", "content": ai_reply}
            )
        except Exception:
            st.error("The response could not be generated. Please check your API key, model access, and network connection.")


st.divider()
st.subheader("Generate visualization after collaboration")

if st.button("Analyze Interaction Pattern and Generate Visualization", disabled=not api_key):
    if len(st.session_state.conversation_history) < 2:
        st.warning("Please complete at least one round of conversation before generating a visualization.")
    else:
        try:
            with st.spinner("Analyzing interaction patterns and preparing your visualization..."):
                pattern_result = detect_interaction_pattern(
                    st.session_state.conversation_history,
                    api_key=api_key,
                )
                scaffold = select_scaffold(pattern_result)
                chart_path = generate_visualization(scaffold)
                profile_path = chart_path if scaffold["visualization_type"] == "radar" else generate_visualization({
                    "visualization_type": "radar",
                    "data": scaffold["srl_profile"],
                })

            st.session_state.latest_scaffold = scaffold
            st.session_state.latest_chart_path = chart_path
            st.session_state.latest_profile_path = profile_path
            st.session_state.visualization_message = None
        except Exception:
            st.session_state.latest_scaffold = None
            st.session_state.latest_chart_path = None
            st.error("The visualization could not be generated. Please try again after checking your API key and connection.")


if st.session_state.latest_scaffold and st.session_state.latest_chart_path:
    st.divider()
    st.subheader("Your interaction visualization")
    st.image(st.session_state.latest_chart_path, use_container_width=True)
    st.write(st.session_state.latest_scaffold["reflection_prompt"])
    st.info(f"Suggested next move: {st.session_state.latest_scaffold['actionable_tactic']}")

    if st.session_state.latest_scaffold["visualization_type"] != "radar":
        st.subheader("Your SRL process profile")
        st.image(st.session_state.latest_profile_path, use_container_width=True)

    st.caption(st.session_state.latest_scaffold["theory_note"])
