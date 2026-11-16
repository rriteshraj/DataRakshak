
from app.leaktest.normalization import build_attack_views
from app.recognizers.indian_pii_detector import analyze_text, redact_text


REDACTION_LABELS = {
    "IN_PAN": "<PAN_REDACTED>",
    "IN_AADHAAR": "<AADHAAR_REDACTED>",
    "IN_PHONE": "<PHONE_REDACTED>",
    "IN_GSTIN": "<GSTIN_REDACTED>",
    "IN_DL": "<DL_REDACTED>",
    "PERSON": "<PERSON_REDACTED>",
    "EMAIL_ADDRESS": "<EMAIL_REDACTED>",
}


def detect_advanced_pii(text):
    """Detect PII across original and transformed representations."""
    views = build_attack_views(text)
    findings = []
    seen = set()

    for view in views:
        view_text = view["text"]
        view_type = view["type"]

        for item in analyze_text(view_text):
            entity = item["entity_type"]
            value = view_text[item["start"]:item["end"]]

            key = (entity, value)

            if key in seen:
                continue

            seen.add(key)

            findings.append({
                "entity_type": entity,
                "representation": view_type,
                "start": item["start"],
                "end": item["end"],
                "score": item["score"],
                "source_encoded": view_type == "base64_decoded"
            })

    return {
        "input_length": len(text),
        "detection_count": len(findings),
        "detected_entities": list(dict.fromkeys(
            item["entity_type"] for item in findings
        )),
        "findings": findings
    }


def protect_advanced_text(text):
    """
    Detect and protect PII in original and transformed representations.

    Base64 candidates are replaced in the original input.
    PII found only after normalization or URL decoding causes
    the input to be blocked because safe span mapping is unavailable.
    """

    if not isinstance(text, str):
        raise TypeError("Input must be a string")

    views = build_attack_views(text)
    findings = []
    seen = set()

    for view in views:
        view_text = view["text"]
        view_type = view["type"]

        for item in analyze_text(view_text):
            entity = item["entity_type"]
            value = view_text[item["start"]:item["end"]]

            key = (entity, value)

            if key in seen:
                continue

            seen.add(key)

            findings.append({
                "entity_type": entity,
                "representation": view_type,
                "score": item["score"]
            })

    # No PII detected in any representation.
    if not findings:
        return {
            "status": "allowed",
            "text": text,
            "detections": []
        }

    # Redact PII found directly in the original input.
    protected_text = redact_text(text)

    # Detect transformed PII that cannot safely be mapped
    # back to its exact original character positions.
    unsafe_transformed = any(
        item["representation"] in ("normalized", "url_decoded")
        for item in findings
    )

    if unsafe_transformed:
        return {
            "status": "blocked",
            "text": None,
            "detections": findings,
            "reason": "PII detected in a transformed representation"
        }

    # Replace Base64 source tokens in the original input.
    replacements = []

    for view in views:
        if view["type"] != "base64_decoded":
            continue

        decoded_detections = analyze_text(view["text"])

        if decoded_detections:
            entity = decoded_detections[0]["entity_type"]
            original_token = view.get("original")

            if original_token:
                placeholder = REDACTION_LABELS.get(
                    entity, "<PII_REDACTED>"
                )
                replacements.append((original_token, placeholder))

    for original_token, placeholder in replacements:
        protected_text = protected_text.replace(
            original_token, placeholder
        )

    return {
        "status": "protected",
        "text": protected_text,
        "detections": findings
    }
