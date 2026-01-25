import json

import requests
import streamlit as st
import os

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma3:4b"

def ask_llama(prompt: str):
    """Send a prompt to Ollama and safely return the model's response."""
    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": True},
            stream=True,
        )
        response.raise_for_status()
    #     print("request sent")
    #     data = response.json()
    #     print("response received", data)
    #     # Handle valid response
    #     if isinstance(data, dict) and "response" in data:
    #         return data["response"].strip()
    #
    #     # Handle unexpected structure
    #     return f"⚠️ Unexpected Ollama response: {data}"
    #
    # except requests.exceptions.ConnectionError:
    #     st.error("❌ Could not connect to Ollama. Make sure `ollama serve` is running.")
    #     return "Connection error — Ollama server not reachable."
    #
    # except requests.exceptions.Timeout:
    #     st.error("⏱️ The request to Ollama timed out.")
    #     return "Request timed out."
    #
    # except requests.exceptions.HTTPError as e:
    #     st.error(f"💥 LLaMA backend error ({e.response.status_code}): {e.response.text}")
    #     return f"Internal server error ({e.response.status_code}). Please retry."
    #
    # except Exception as e:
    #     st.error(f"Unexpected error: {e}")
    #     return f"Unexpected error: {e}"
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue  # skip malformed lines safely

            if "response" in data:
                yield data["response"]

            if data.get("done", False):
                break

    except requests.exceptions.ConnectionError:
        st.error("❌ Could not connect to Ollama. Make sure `ollama serve` is running.")
        yield "Connection error — Ollama server not reachable."

    except requests.exceptions.Timeout:
        st.error("⏱️ The request to Ollama timed out.")
        yield "Request timed out."

    except requests.exceptions.HTTPError as e:
        st.error(f"💥 LLaMA backend error ({e.response.status_code}): {e.response.text}")
        yield f"Internal server error ({e.response.status_code}). Please retry."

    except Exception as e:
        st.error(f"Unexpected error: {e}")
        yield f"Unexpected error: {e}"
