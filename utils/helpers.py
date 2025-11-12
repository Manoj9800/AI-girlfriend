def safe_text(text, default=''):
    if text is None:
        return default
    return str(text)
