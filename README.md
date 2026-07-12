# TeachCL Co-design Assistant

A Streamlit prototype that chats with teachers, detects an interaction pattern,
and displays a visualization.

## Run locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown in the terminal and enter an OpenAI API key in the
sidebar. The key is held only in the active Streamlit session and is not saved
to a file by this application.

## Deploy as a shareable link

1. Create a GitHub repository and upload this folder. Do not upload `.env`,
   `.streamlit/secrets.toml`, or API keys.
2. Go to [Streamlit Community Cloud](https://share.streamlit.io/) and create an app.
3. Select the GitHub repository, branch, and `app.py` as the entry point.
4. Deploy and share the generated `streamlit.app` URL.

Visitors provide their own OpenAI API key in the sidebar, so API usage is
charged to their own OpenAI account. Use the **Clear chat and API key** button
when finishing a session on a shared device.

## SRL process profile

The app codes observable teacher turns and derives a five-dimension SRL process
profile: task definition, planning and control, monitoring, evaluation and
justification, and metacognitive regulation. The radar chart compares the
current interaction with a **prototype reference profile** that is intended to
support reflection. It is not an empirically calibrated expert norm and does
not diagnose a teacher's cognitive ability.

The coding logic is kept in `srl_profile.py`. It uses the existing interaction
codes and adds `B4_evaluation` for explicit judgments of an AI suggestion
against a teaching criterion. This keeps the visualisation traceable to the
observable dialogue data.

## Configuration

The default model is `gpt-5.5`. To use a different model, set the `OPENAI_MODEL`
environment variable in the deployment platform's secret/environment settings.
