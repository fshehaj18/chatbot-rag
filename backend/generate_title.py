# import re
#
# def generate_title_from_prompt(prompt: str, max_len=40) -> str:
#     prompt = prompt.strip()
#
#     # Remove question mark
#     prompt = prompt.replace("?", "")
#
#     # Remove common question starters
#     prompt = re.sub(
#         r"^(how|what|why|when|where|which|who|does|do|is|are|can|should)\s+",
#         "",
#         prompt,
#         flags=re.IGNORECASE,
#     )
#
#     # Remove filler phrases
#     prompt = re.sub(
#         r"\b(explain|describe|tell me|help me|please)\b",
#         "",
#         prompt,
#         flags=re.IGNORECASE,
#     )
#
#     # Normalize spaces
#     prompt = re.sub(r"\s+", " ", prompt).strip()
#
#     # Capitalize first letter
#     prompt = prompt[:1].upper() + prompt[1:]
#
#     # Truncate cleanly
#     if len(prompt) > max_len:
#         prompt = prompt[:max_len].rsplit(" ", 1)[0]
#
#     return prompt
import spacy

nlp = spacy.load("en_core_web_sm")

ALLOWED_POS = {"NOUN", "PROPN", "ADJ"}

def generate_title_from_prompt(prompt: str, max_len: int = 40) -> str:
    prompt = prompt.strip().replace("?", "")

    doc = nlp(prompt)

    tokens = [
        token.text
        for token in doc
        if token.pos_ in ALLOWED_POS
        and not token.is_stop
        and token.text.isalnum()
    ]
    print("Tokens: ", tokens)

    title = " ".join(tokens).title()

    if not title:
        title = "New Chat"

    if len(title) > max_len:
        title = title[:max_len].rsplit(" ", 1)[0]

    return title
