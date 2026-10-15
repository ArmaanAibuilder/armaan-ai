import os
import streamlit as st
from ollama import Client

MODEL = "gemma4:31b"


def get_reply(messages):
    """Send chat messages to Ollama's hosted API and return its reply."""

    try:
        api_key = st.secrets["OLLAMA_API_KEY"]
    except Exception:
        api_key = os.getenv("OLLAMA_API_KEY", "")

    if not api_key:
        return (
            "Ollama API key is missing. Add OLLAMA_API_KEY "
            "to your Streamlit Cloud Secrets."
        )

    try:
        client = Client(
            host="https://ollama.com",
            headers={
                "Authorization": f"Bearer {api_key}"
            },
        )

        response = client.chat(
            model=MODEL,
            messages=messages,
        )

        return response["message"]["content"]

    except Exception as exc:
        print(f"Ollama API error: {exc}")
        return (
            "I couldn't get a response from Ollama. "
            "Please check your API key, model availability, "
            "and account usage limits."
        )
