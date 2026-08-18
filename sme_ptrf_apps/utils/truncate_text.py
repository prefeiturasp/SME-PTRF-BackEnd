def truncate_text(text: str, max_length: int = 50) -> str:
    if len(text) <= max_length:
        return text

    return text[:max_length] + "..."
