# import streamlit as st
# import os
# from backend.llama_runner import ask_llama
# from backend.file_loader import load_all_files
# from backend.embedder import embed_chunks, search, load_embeddings
#
# # ------------------------------
# # ⚙️ Streamlit page setup
# # ------------------------------
# st.set_page_config(page_title="💬 Project Chatbot", layout="wide")
#
# # ------------------------------
# # 🌙 Custom CSS (ChatGPT-like)
# # ------------------------------
# st.markdown("""
#     <style>
#         body {
#             background-color: #0f1117;
#             color: white;
#             font-family: 'Inter', sans-serif;
#         }
#         .main {
#             background-color: #0f1117;
#             padding: 2rem;
#             border-radius: 12px;
#             max-width: 800px;
#             margin: auto;
#         }
#         .chat-bubble {
#             padding: 1rem;
#             margin: 0.5rem 0;
#             border-radius: 12px;
#             line-height: 1.5;
#             max-width: 90%;
#             word-wrap: break-word;
#         }
#         .user-bubble {
#             background-color: #0057ff;
#             color: white;
#             align-self: flex-end;
#             margin-left: auto;
#         }
#         .bot-bubble {
#             background-color: #1e1e2e;
#             color: #e3e3e3;
#             border: 1px solid #2e2e3e;
#             align-self: flex-start;
#             margin-right: auto;
#         }
#         .chat-container {
#             display: flex;
#             flex-direction: column;
#             height: 70vh;
#             overflow-y: auto;
#             border: 1px solid #2e2e3e;
#             padding: 1rem;
#             border-radius: 12px;
#             background-color: #141621;
#         }
#         .stTextInput > div > div > input {
#             background-color: #1c1c2a;
#             color: white;
#             border-radius: 10px;
#             border: 1px solid #333;
#         }
#         .stButton>button {
#             background-color: #0057ff;
#             color: white;
#             border-radius: 8px;
#             border: none;
#             font-weight: 500;
#             padding: 0.5rem 1.5rem;
#         }
#         .stButton>button:hover {
#             background-color: #1a66ff;
#         }
#     </style>
# """, unsafe_allow_html=True)
#
# # ------------------------------
# # 🧠 Page Header
# # ------------------------------
# st.markdown("<h2 style='text-align:center;'>🚗🔑 GSK Chatbot</h2>", unsafe_allow_html=True)
# st.markdown("<p style='text-align:center;color:gray;'>Ask anything about your code, docs, or data files in the project.</p>", unsafe_allow_html=True)
#
# # ------------------------------
# # 🧩 Initialize embeddings once
# # ------------------------------
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
#
# # ------------------------------
# # 💬 Initialize chat history
# # ------------------------------
# if "messages" not in st.session_state:
#     st.session_state.messages = []
#
# # ------------------------------
# # 💬 Display chat messages
# # ------------------------------
# # st.markdown('<div class="chat-container" id="chat-window">', unsafe_allow_html=True)
# # for msg in st.session_state.messages:
# #     role_class = "user-bubble" if msg["role"] == "user" else "bot-bubble"
# #     st.markdown(f'<div class="chat-bubble {role_class}">{msg["content"]}</div>', unsafe_allow_html=True)
# # st.markdown("</div>", unsafe_allow_html=True)
#
# # ------------------------------
# # 🗑️ Optional: Clear chat button
# # ------------------------------
# col1, col2, _ = st.columns([1, 1, 6])
# with col1:
#     if st.button("🗑️ Clear Chat"):
#         st.session_state.messages = []
#         st.session_state.last_query = None
#         st.rerun()
#
# # ------------------------------
# # ✏️ Input area (form-based to prevent re-runs)
# # ------------------------------
# with st.form("chat_form", clear_on_submit=True):
#     user_input = st.chat_input(placeholder="Ask something about your project...")
#     submitted = st.form_submit_button("Send")
#
# # ------------------------------
# # 🚀 On submit (runs once per send)
# # ------------------------------
# if submitted and user_input:
#     # Prevent repeated queries for same question
#     if st.session_state.get("last_query") != user_input:
#         st.session_state.last_query = user_input
#         st.session_state.messages.append({"role": "user", "content": user_input})
#
#         with st.spinner("🤔 Thinking..."):
#             context_chunks = search(user_input)
#             context = "\n".join([chunk for chunk, _ in context_chunks])
#
#             prompt = f"""
#             You are a helpful assistant that answers questions **only** based on these project files:
#
#             [Context]:
#             {context}
#
#             [Question]:
#             {user_input}
#
#             [Answer]:
#             If the answer is not found in the context above, reply:
#             "I could not find that information in the uploaded project files."
#             """
#
#             response = ask_llama(prompt)
#
#         st.session_state.messages.append({"role": "bot", "content": response})
#         st.rerun()
import json
import re

import streamlit as st
import os

from backend.generate_title import generate_title_from_prompt
from backend.llama_runner import ask_llama
from backend.file_loader import load_all_files
from backend.embedder import embed_chunks, search, load_embeddings

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
if "initialized" not in st.session_state:
    os.makedirs("data", exist_ok=True)

    # Try loading saved FAISS index first
    try:
        load_embeddings()
        print("✅ Loaded existing embeddings.")
    except Exception:
        print("⚠️ No saved embeddings found, embedding all files...")
        all_files = load_all_files("data", recursive=True)
        embed_chunks(all_files)

    st.session_state.initialized = True


# ------------------------------
# 💬 Initialize chat history
# ------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat_file" not in st.session_state:
    st.session_state.chat_file = None
if "last_query" not in st.session_state:
    st.session_state.last_query = None

# ------------------------------
# 💬 Display chat messages
# ------------------------------
# st.markdown('<div class="chat-container" id="chat-window">', unsafe_allow_html=True)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

with st.sidebar:
    st.title("💬 Chats")

    if st.button("➕ New Chat"):
        st.session_state.messages = new_chat()
        st.session_state.chat_file = None
        st.rerun()

    st.divider()

    chat_files = sorted(os.listdir(CHAT_DIR), reverse=True)

    for chat in chat_files:
        chat_path = f"{CHAT_DIR}/{chat}"
        is_active = st.session_state.chat_file == chat_path
        css_class = "chat-item active" if is_active else "chat-item"
        if st.button(chat.replace(".json", "")):
            st.session_state.messages = load_chat(f"{CHAT_DIR}/{chat}")
            st.session_state.chat_file = f"{CHAT_DIR}/{chat}"
            st.session_state.last_query = None
            st.rerun()

    # chat_files = sorted(os.listdir(CHAT_DIR), reverse=True)
    #
    # for chat in chat_files:
    #     if st.button(chat.replace(".json", "")):
    #         st.session_state.messages = load_chat(f"{CHAT_DIR}/{chat}")
    #         st.session_state.chat_file = f"{CHAT_DIR}/{chat}"
    #         st.rerun()


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
col1, col2, _ = st.columns([3, 1, 4])
with col1:
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = new_chat()
        st.session_state.chat_file = None
        st.session_state.last_query = None
        st.rerun()

