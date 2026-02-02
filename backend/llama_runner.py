import json
import time
import requests
import streamlit as st

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen2.5:1.5b"

def ask_llama(prompt: str):
    """Send a prompt to Ollama and stream the model's response.
       Prints total query duration at the end.
    """
    start_time = time.perf_counter()

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": MODEL_NAME, "prompt": prompt, "stream": True},
            stream=True,
        )
        response.raise_for_status()
        print("start query qwen2.5:1.5b")
        for line in response.iter_lines(decode_unicode=True):
            if not line:
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            if "response" in data:
                yield data["response"]

            if data.get("done", False):
                break

        end_time = time.perf_counter()
        duration = end_time - start_time
        print(f"⏱️ Ollama query duration: {duration:.2f} seconds")

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
