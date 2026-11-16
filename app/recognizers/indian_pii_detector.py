
"""
Day 1 detector for synthetic/test text.

Important:
- Detects patterns, not real-world identity validity.
- Does not contact UIDAI or verify ownership/authenticity.
- Use synthetic test values only.
"""

from __future__ import annotations

from typing import Any

from presidio_analyzer import (
    AnalyzerEngine,
    Pattern,
    PatternRecognizer,
)
from presidio_analyzer.nlp_engine import NlpEngineProvider
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig


# Technical terms that should not be detected as PERSON.
TECHNICAL_ALLOWLIST = [
    "DataRakshak",
    "RAG",
    "LLM",
    "AI",
    "ML",
    "API",
    "ChromaDB",
    "Presidio",
    "Ollama",
    "Python",
    "TensorFlow",
    "PyTorch",
    "SQL",
    "React",
    "FastAPI",
    "Docker",
    "Kubernetes",
]


# Indian PII recognizers
CUSTOM_RECOGNIZERS = [
    PatternRecognizer(
        supported_entity="IN_AADHAAR",
        name="Indian Aadhaar format recognizer",
        patterns=[
            Pattern(
                name="aadhaar_grouped_or_contiguous",
                regex=r"\b[2-9]\d{3}[\s-]?\d{4}[\s-]?\d{4}\b",
                score=0.75,
            )
        ],
        context=["aadhaar", "uid", "identity", "unique identification"],
    ),

    PatternRecognizer(
        supported_entity="IN_PAN",
        name="Indian PAN format recognizer",
        patterns=[
            Pattern(
                name="pan_format",
                regex=r"\b[A-Z]{5}[0-9]{4}[A-Z]\b",
                score=0.85,
            )
        ],
        context=["pan", "permanent account number", "tax"],
    ),

    PatternRecognizer(
        supported_entity="IN_GSTIN",
        name="Indian GSTIN format recognizer",
        patterns=[
            Pattern(
                name="gstin_format",
                regex=r"\b[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z][1-9A-Z]Z[0-9A-Z]\b",
                score=0.85,
            )
        ],
        context=["gstin", "gst", "goods and services tax"],
    ),

    PatternRecognizer(
        supported_entity="IN_DL",
        name="Indian Driving Licence recognizer",
        patterns=[
            Pattern(
                name="indian_dl_format",
                regex=r"\b[A-Z]{2}[- ]?\d{2}[- ]?\d{4}[- ]?\d{7}\b",
                score=0.75,
            )
        ],
        context=[
            "driving licence",
            "driving license",
            "dl number",
            "licence number",
            "license number",
        ],
    ),

    PatternRecognizer(
        supported_entity="IN_PHONE",
        name="Indian mobile number recognizer",
        patterns=[
            Pattern(
                name="indian_mobile",
                regex=r"(?<!\d)(?:\+91[\s-]?)?[6-9]\d{9}(?!\d)",
                score=0.75,
            )
        ],
        context=["phone", "mobile", "contact", "call"],
    ),
]


def build_analyzer() -> AnalyzerEngine:
    """Create Presidio analyzer using the small English spaCy model."""

    nlp_configuration = {
        "nlp_engine_name": "spacy",
        "models": [
            {"lang_code": "en", "model_name": "en_core_web_sm"}
        ],
    }

    provider = NlpEngineProvider(
        nlp_configuration=nlp_configuration
    )

    nlp_engine = provider.create_engine()

    analyzer = AnalyzerEngine(
        nlp_engine=nlp_engine,
        supported_languages=["en"],
    )

    # Register Indian PII recognizers.
    for recognizer in CUSTOM_RECOGNIZERS:
        analyzer.registry.add_recognizer(recognizer)

    # Context-aware single-name detection.
    single_name_recognizer = PatternRecognizer(
        supported_entity="PERSON",
        name="Context-aware single person name recognizer",
        patterns=[
            Pattern(
                name="name_label",
                regex=r"(?i)(?<=name: )[A-Z][a-z]{2,}",
                score=0.70,
            ),
            Pattern(
                name="full_name_label",
                regex=r"(?i)(?<=full name: )[A-Z][a-z]{2,}",
                score=0.70,
            ),
            Pattern(
                name="employee_name_label",
                regex=r"(?i)(?<=employee name: )[A-Z][a-z]{2,}",
                score=0.70,
            ),
        ],
    )

    analyzer.registry.add_recognizer(single_name_recognizer)

    return analyzer


_ANALYZER = None
_ANONYMIZER = AnonymizerEngine()


def get_analyzer() -> AnalyzerEngine:
    global _ANALYZER

    if _ANALYZER is None:
        _ANALYZER = build_analyzer()

    return _ANALYZER


def analyze_text(text: str) -> list[dict[str, Any]]:
    """Return detected entities with type, offsets and confidence score."""

    if not isinstance(text, str):
        raise TypeError("text must be a string")

    results = get_analyzer().analyze(
        text=text,
        language="en",
        entities=[
            "IN_AADHAAR",
            "IN_PAN",
            "IN_GSTIN",
            "IN_PHONE",
            "IN_DL",
            "EMAIL_ADDRESS",
            "PERSON",
        ],
        allow_list=TECHNICAL_ALLOWLIST,
    )

    return [
        {
            "entity_type": item.entity_type,
            "start": item.start,
            "end": item.end,
            "score": round(float(item.score), 3),
            "text": text[item.start:item.end],
        }
        for item in results
    ]


def redact_text(text: str) -> str:
    """Replace detected identifiers with entity-labelled placeholders."""

    analyzer_results = get_analyzer().analyze(
        text=text,
        language="en",
        entities=[
            "IN_AADHAAR",
            "IN_PAN",
            "IN_GSTIN",
            "IN_DL",
            "IN_PHONE",
            "EMAIL_ADDRESS",
            "PERSON",
        ],
        allow_list=TECHNICAL_ALLOWLIST,
    )

    operators = {
        "DEFAULT": OperatorConfig(
            "replace",
            {"new_value": "<REDACTED>"},
        ),
        "IN_AADHAAR": OperatorConfig(
            "replace",
            {"new_value": "<AADHAAR_REDACTED>"},
        ),
        "IN_PAN": OperatorConfig(
            "replace",
            {"new_value": "<PAN_REDACTED>"},
        ),
        "IN_GSTIN": OperatorConfig(
            "replace",
            {"new_value": "<GSTIN_REDACTED>"},
        ),
        "IN_DL": OperatorConfig(
            "replace",
            {"new_value": "<DL_REDACTED>"},
        ),
        "IN_PHONE": OperatorConfig(
            "replace",
            {"new_value": "<PHONE_REDACTED>"},
        ),
        "EMAIL_ADDRESS": OperatorConfig(
            "replace",
            {"new_value": "<EMAIL_REDACTED>"},
        ),
        "PERSON": OperatorConfig(
            "replace",
            {"new_value": "<PERSON_REDACTED>"},
        ),
    }

    result = _ANONYMIZER.anonymize(
        text=text,
        analyzer_results=analyzer_results,
        operators=operators,
    )

    return result.text


if __name__ == "__main__":

    sample = (
        "Synthetic test: Aadhaar 2345 6789 0123, "
        "PAN ABCDE1234F, GSTIN 22AAAAA0000A1Z5, "
        "mobile 9876543210, email demo@example.com. "
        "Name: Rahul"
    )

    print("DETECTIONS")

    for detection in analyze_text(sample):
        print(detection)

    print("\nREDACTED")
    print(redact_text(sample))


