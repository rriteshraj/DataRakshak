
import base64
import binascii
import re
from urllib.parse import unquote


def normalize_text(text):
    """Normalize identifier separators without joining sentence words."""

    pan_pattern = (
        r"(?<![A-Za-z0-9])"
        r"[A-Za-z](?:[\s-]*[A-Za-z]){4}"
        r"[\s-]*\d(?:[\s-]*\d){3}"
        r"[\s-]*[A-Za-z]"
        r"(?![A-Za-z0-9])"
    )

    return re.sub(
        pan_pattern,
        lambda match: re.sub(r"[\s-]", "", match.group()),
        text
    )


def decode_url_text(text):
    """Decode URL-encoded text safely."""
    try:
        return unquote(text, errors="strict")
    except (UnicodeDecodeError, ValueError):
        return text


def decode_base64_candidates(text):
    """Find and decode bounded Base64-like tokens."""

    decoded = []

    candidates = re.findall(
        r"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{12,}={0,2}(?![A-Za-z0-9+/])",
        text
    )

    for candidate in candidates:
        try:
            padding = "=" * (-len(candidate) % 4)

            raw = base64.b64decode(
                candidate + padding,
                validate=True
            )

            value = raw.decode("utf-8")

            if value.isprintable():
                decoded.append({
                    "original": candidate,
                    "decoded": value
                })

        except (binascii.Error, UnicodeDecodeError, ValueError):
            continue

    return decoded


def build_attack_views(text):
    """Create representations for advanced PII evaluation."""

    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    url_decoded = decode_url_text(text)

    views = [
        {"type": "original", "text": text},
        {"type": "normalized", "text": normalize_text(text)},
        {"type": "url_decoded", "text": url_decoded}
    ]

    for item in decode_base64_candidates(text):
        views.append({
            "type": "base64_decoded",
            "text": item["decoded"],
            "original": item["original"]
        })

    return views
