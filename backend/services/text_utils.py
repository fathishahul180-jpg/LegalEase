
import io


def terms_from_text(text: str) -> list[str]:
    """Convert each non-empty line into a separate term."""
    if not text:
        return []

    return [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]


def plain_text_bytes(text: str) -> bytes:
    """Convert text into UTF-8 bytes for download."""
    return text.encode("utf-8")