
import pytest

from app.leaktest.stage_runner import run_stage
from app.services.privacy_engine import PrivacyEngine


ATTACK_CASES = [
    ("IN_PAN", "ABCDE1234F"),
    ("IN_AADHAAR", "234567890123"),
    ("IN_PHONE", "9876543210"),
    ("EMAIL_ADDRESS", "test@example.com"),
    ("IN_GSTIN", "22AAAAA0000A1Z5"),
]


@pytest.mark.parametrize("entity,value", ATTACK_CASES)
def test_raw_pii_leak_is_detected(entity, value):
    text = f"Sensitive information: {value}"

    result = run_stage(
        stage_name="LLM Output",
        input_text=text,
        output_text=text,
        expected_values=[
            {"type": entity, "value": value}
        ],
    )

    assert result["leaked_count"] == 1
    assert entity in result["leaked_entities"]


@pytest.mark.parametrize("entity,value", ATTACK_CASES)
def test_redaction_prevents_pii_leak(entity, value):
    text = f"Sensitive information: {value}"

    engine = PrivacyEngine(vault=object())
    protected = engine.process(
        text=text,
        action="redact"
    )["text"]

    result = run_stage(
        stage_name="LLM Output",
        input_text=text,
        output_text=protected,
        expected_values=[
            {"type": entity, "value": value}
        ],
    )

    assert result["leaked_count"] == 0
    assert value not in protected


def test_multiple_pii_values_are_protected():
    text = (
        "PAN ABCDE1234F, Aadhaar 234567890123, "
        "phone 9876543210, email test@example.com, "
        "GSTIN 22AAAAA0000A1Z5"
    )

    engine = PrivacyEngine(vault=object())
    protected = engine.process(
        text=text,
        action="redact"
    )["text"]

    assert protected != text

    for _, value in ATTACK_CASES:
        assert value not in protected
