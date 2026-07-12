import os

from openai import OpenAI


MODEL_NAME = os.getenv("OPENAI_MODEL", "gpt-5.5")


def call_openai(system_prompt, user_input, api_key=None):
    """Call OpenAI with a per-session key; never save user credentials to disk."""
    key = api_key or os.getenv("OPENAI_API_KEY")
    if not key:
        raise ValueError("An OpenAI API key is required.")

    # Create the client only for this request, so a visitor's key is not shared
    # with other Streamlit sessions.
    client = OpenAI(api_key=key)
    response = client.responses.create(
        model=MODEL_NAME,
        instructions=system_prompt,
        input=user_input,
    )
    return response.output_text
