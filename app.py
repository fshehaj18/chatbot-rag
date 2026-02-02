import json
import re

import streamlit as st
import os

from backend.generate_title import generate_title_from_prompt
from backend.llama_runner import ask_llama
from backend.file_loader import load_all_files
# from backend.embedder import embed_chunks, search, load_embeddings
from backend.embedder import search

CHAT_DIR = "chats"
os.makedirs(CHAT_DIR, exist_ok=True)

def new_chat():
    return []

def save_chat(chat_file, messages):
    with open(chat_file, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2)

def load_chat(chat_file):
    with open(chat_file, "r", encoding="utf-8") as f:
        return json.load(f)


# ------------------------------
# ⚙️ Streamlit page setup
# ------------------------------
st.set_page_config(page_title="💬 Project Chatbot", layout="wide")

# ------------------------------
# 🌙 Custom CSS (ChatGPT-like)
# ------------------------------
st.markdown("""
    <style>
        body {
            background-color: #0f1117;
            color: white;
            font-family: 'Inter', sans-serif;
        }
        .main {
            background-color: #0f1117;
            padding: 2rem;
            border-radius: 12px;
            max-width: 800px;
            margin: auto;
        }
        .chat-bubble {
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 12px;
            line-height: 1.5;
            max-width: 90%;
            word-wrap: break-word;
        }
        .user-bubble {
            background-color: #0057ff;
            color: white;
            align-self: flex-end;
            margin-left: auto;
        }
        .bot-bubble {
            background-color: #1e1e2e;
            color: #e3e3e3;
            border: 1px solid #2e2e3e;
            align-self: flex-start;
            margin-right: auto;
        }
        .chat-container {
            display: flex;
            flex-direction: column;
            height: 70vh;
            overflow-y: auto;
            border: 1px solid #2e2e3e;
            padding: 1rem;
            border-radius: 12px;
            background-color: #141621;
        }
        .chat-item.active button {
            background-color: #3a3b41 !important;
            color: #ffffff !important;
            font-weight: 600;
        }
        .stTextInput > div > div > input {
            background-color: #1c1c2a;
            color: white;
            border-radius: 10px;
            border: 1px solid #333;
        }
        .stButton>button {
            background-color: #2f3036;
            color: white;
            border-radius: 8px;
            border: none;
            font-weight: 500;
            padding: 0.5rem 1.5rem;
        }
        .stButton>button:hover {
            background-color: #3a3b41;
        }
:root {
    --accent: #6d7cff;
    --bg-hover: #2a2c36;
    --bg-selected: #1c1f2a;
    --border-default: rgba(255,255,255,0.08);
    --text-muted: #cfd2dc;
    --text-active: #ffffff;
}

/* Hide radio title label */
section[data-testid="stSidebar"] .stRadio > label {
    display: none;
}

/* Radio group container */
section[data-testid="stSidebar"] div[role="radiogroup"] {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

/* Hide native radio input */
section[data-testid="stSidebar"]
div[role="radiogroup"] input[type="radio"] {
    display: none;
}

/* Chat card (label is the card) */
section[data-testid="stSidebar"] div[role="radiogroup"] > label {
    display: flex;
    align-items: center;
    padding: 12px 14px;
    border-radius: 10px;
    border: 2px solid var(--border-default);
    background-color: transparent;
    cursor: pointer;
    transition:
        background-color 0.15s ease,
        border-color 0.15s ease;
    position: relative;
    width: 100%;
}

/* Left status dot */
section[data-testid="stSidebar"]
div[role="radiogroup"] > label::before {
    content: "";
    width: 14px;
    height: 14px;
    border-radius: 50%;
    background-color: var(--dot-inactive);
    margin-right: 12px;
    flex-shrink: 0;
}

/* Chat text */
section[data-testid="stSidebar"]
div[role="radiogroup"] > label > div {
    color: var(--text-muted);
    font-size: 14px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Hover */
section[data-testid="stSidebar"]
div[role="radiogroup"] > label:hover {
    background-color: var(--bg-hover);
}

/* Selected card */
section[data-testid="stSidebar"]
div[role="radiogroup"] > label:has(input:checked) {
    background-color: var(--bg-selected);
    border-color: var(--border-selected);
}

/* Selected text */
section[data-testid="stSidebar"]
div[role="radiogroup"] > label:has(input:checked) > div {
    color: var(--text-active);
    font-weight: 500;
}

/* Selected dot */
section[data-testid="stSidebar"]
div[role="radiogroup"] > label:has(input:checked)::before {
    background-color: var(--dot-active);
}       
    </style>
""", unsafe_allow_html=True)

# ------------------------------
# 🧠 Page Header
# ------------------------------
st.markdown("<h2 style='text-align:center;'>🚗🔑 GSK Chatbot</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;color:gray;'>Ask anything about your code, docs, or data files in the project.</p>", unsafe_allow_html=True)

# ------------------------------
# 🧩 Initialize embeddings once
# ------------------------------
# if "initialized" not in st.session_state:
#     os.makedirs("data", exist_ok=True)
#
#     # Try loading saved FAISS index first
#     try:
#         load_embeddings()
#         print("✅ Loaded existing embeddings.")
#     except Exception:
#         print("⚠️ No saved embeddings found, embedding all files...")
#         all_files = load_all_files("data", recursive=True)
#         embed_chunks(all_files)
#
#     st.session_state.initialized = True


# ------------------------------
# 💬 Initialize chat history
# ------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_file" not in st.session_state:
    st.session_state.chat_file = None
if "last_query" not in st.session_state:
    st.session_state.last_query = None

if "creating_new_chat" not in st.session_state:
    st.session_state.creating_new_chat = False

# ------------------------------
# 💬 Display chat messages
# ------------------------------
# st.markdown('<div class="chat-container" id="chat-window">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

with st.sidebar:
    st.markdown("### Your chats")

    chat_files = sorted(os.listdir(CHAT_DIR), reverse=True)
    chat_names = [c.replace(".json", "") for c in chat_files]

    if st.button("➕ New chat"):
        st.session_state.messages = new_chat()
        st.session_state.chat_file = None
        st.session_state.last_query = None
        st.session_state.creating_new_chat = True
        st.rerun()

    if chat_files:
        if st.session_state.chat_file and not st.session_state.creating_new_chat:
            current = os.path.basename(st.session_state.chat_file).replace(".json", "")
            index = chat_names.index(current)
        else:
            index = None  # allow no selection

        selected = st.radio(
            label="",
            options=chat_names,
            index=index,
            key="chat_selector",
        )

        if selected:
            selected_file = f"{CHAT_DIR}/{selected}.json"

            if st.session_state.chat_file != selected_file:
                st.session_state.messages = load_chat(selected_file)
                st.session_state.chat_file = selected_file
                st.session_state.creating_new_chat = False
                st.session_state.last_query = None
                st.rerun()
# ------------------------------
# ✏️ Input area (form-based to prevent re-runs)
# ------------------------------
user_input = st.chat_input("Ask something about your project...")


# ------------------------------
# 🚀 On submit (ChatGPT-style)
# ------------------------------
if user_input and user_input != st.session_state.last_query:
    st.session_state.last_query = user_input

    # --- show user message immediately ---
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    st.session_state.creating_new_chat = False

    with st.chat_message("user"):
        st.markdown(user_input)

    # --- assistant placeholder ---
    # with st.chat_message("assistant"):
    #     placeholder = st.empty()
    #     placeholder.markdown("🤔 Thinking...")
    #
    #     context_chunks = search(user_input)
    #     context = "\n".join(chunk for chunk, _ in context_chunks)
    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_response = ""
        thinking = True

        # show thinking inside the SAME bubble
        placeholder.markdown("🤔 Thinking...")

        context_chunks = search(user_input)
        context = "\n".join(chunk for chunk, _ in context_chunks)
        prompt = f"""
You are a helpful assistant that answers questions ONLY using the context below.
Provide detailed answers full of information for developers.

[Context]
{context}

[Question]
{user_input}

If the answer is not found in the context, say:
"I could not find that information in the uploaded project files."
"""
        for token in ask_llama(prompt):
            if thinking:
                placeholder.markdown("")  # remove "Thinking..."
                thinking = False

            full_response += token
            placeholder.markdown(full_response + "▌")

        placeholder.markdown(full_response)
        #     response = ask_llama(prompt)
        #     placeholder.markdown(response)
        #
        # # --- persist assistant message ---
        # st.session_state.messages.append(
        #     {"role": "assistant", "content": response}
        # )
        # --- assistant streaming ---
        # with st.chat_message("assistant"):
        #     placeholder = st.empty()
        #     full_response = ""
        #
        #     for token in ask_llama(prompt):
        #         full_response += token
        #         placeholder.markdown(full_response + "▌")
        #
        #     placeholder.markdown(full_response)

        # --- persist assistant message (STRING only) ---
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

    # --- create chat file if new ---
    if not st.session_state.chat_file:
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        chat_title = generate_title_from_prompt(user_input)
        st.session_state.chat_file = f"{CHAT_DIR}/{chat_title}.json"

    # --- save chat ---
    save_chat(st.session_state.chat_file, st.session_state.messages)

    st.rerun()


# ------------------------------
# 🗑️ Optional: Clear chat button
# ------------------------------
# col1, col2, _ = st.columns([3, 1, 4])
# with col1:
#     if st.button("🗑️ Clear Chat"):
#         st.session_state.messages = new_chat()
#         st.session_state.chat_file = None
#         st.session_state.last_query = None
#         st.rerun()

