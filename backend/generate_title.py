import re

def generate_title_from_prompt(prompt: str, max_len=40) -> str:
    prompt = prompt.strip()

    # Remove question mark
    prompt = prompt.replace("?", "")

    # Remove common question starters
    prompt = re.sub(
        r"^(how|what|why|when|where|which|who|does|do|is|are|can|should)\s+",
        "",
        prompt,
        flags=re.IGNORECASE,
    )

    # Remove filler phrases
    prompt = re.sub(
        r"\b(explain|describe|tell me|help me|please)\b",
        "",
        prompt,
        flags=re.IGNORECASE,
    )

    # Normalize spaces
    prompt = re.sub(r"\s+", " ", prompt).strip()

    # Capitalize first letter
    prompt = prompt[:1].upper() + prompt[1:]

    # Truncate cleanly
    if len(prompt) > max_len:
        prompt = prompt[:max_len].rsplit(" ", 1)[0]

    return prompt
