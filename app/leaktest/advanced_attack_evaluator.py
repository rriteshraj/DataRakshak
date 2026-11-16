
from app.leaktest.advanced_detector import (
    detect_advanced_pii,
    protect_advanced_text
)


ATTACK_CASES = [
    {
        "id": "ADV_001",
        "category": "Base64 Encoding",
        "text": "QUJDREUxMjM0Rg==",
        "expected_entity": "IN_PAN",
        "expected_value": "ABCDE1234F"
    },
    {
        "id": "ADV_002",
        "category": "URL Encoding",
        "text": "%41%42%43%44%45%31%32%33%34%46",
        "expected_entity": "IN_PAN",
        "expected_value": "ABCDE1234F"
    },
    {
        "id": "ADV_003",
        "category": "Space Obfuscation",
        "text": "My PAN is ABCDE 1234 F",
        "expected_entity": "IN_PAN",
        "expected_value": "ABCDE1234F"
    },
    {
        "id": "ADV_004",
        "category": "Hyphen Obfuscation",
        "text": "My PAN is ABCDE-1234-F",
        "expected_entity": "IN_PAN",
        "expected_value": "ABCDE1234F"
    },
    {
        "id": "ADV_005",
        "category": "Aadhaar Separator",
        "text": "Aadhaar: 2345-6789-0123",
        "expected_entity": "IN_AADHAAR",
        "expected_value": "2345-6789-0123"
    },
]

BENIGN_CASES = [
    "This is an ordinary project status update.",
    "The meeting is scheduled for Monday morning.",
    "DataRakshak protects sensitive information."
]


def evaluate_advanced_attacks():
    results = []
    detected_count = 0
    prevented_count = 0
    leaked_count = 0

    category_summary = {}

    for case in ATTACK_CASES:
        detection = detect_advanced_pii(case["text"])
        protection = protect_advanced_text(case["text"])

        detected_entities = detection["detected_entities"]

        attack_detected = (
            case["expected_entity"] in detected_entities
        )

        protected_text = protection["text"]

        # Check both canonical and supplied expected values.
        leaked = False

        if isinstance(protected_text, str):
            leaked = (
                case["expected_value"] in protected_text
                or case["text"] in protected_text
            )

        leak_prevented = (
            attack_detected
            and not leaked
            and protection["status"] in ("protected", "blocked")
        )

        detected_count += int(attack_detected)
        prevented_count += int(leak_prevented)
        leaked_count += int(leaked)

        category = case["category"]

        if category not in category_summary:
            category_summary[category] = {
                "total": 0,
                "detected": 0,
                "prevented": 0,
                "leaks": 0
            }

        category_summary[category]["total"] += 1
        category_summary[category]["detected"] += int(attack_detected)
        category_summary[category]["prevented"] += int(leak_prevented)
        category_summary[category]["leaks"] += int(leaked)

        results.append({
            "test_id": case["id"],
            "category": category,
            "expected_entity": case["expected_entity"],
            "attack_detected": attack_detected,
            "protection_status": protection["status"],
            "leak_prevented": leak_prevented,
            "leak_detected": leaked,
            "detection_count": detection["detection_count"],
            "protected_output": protected_text
        })

    # Evaluate ordinary text for false positives.
    false_positives = 0

    for text in BENIGN_CASES:
        detection = detect_advanced_pii(text)
        protection = protect_advanced_text(text)

        if detection["detection_count"] > 0:
            false_positives += 1

    total_attacks = len(ATTACK_CASES)
    total_benign = len(BENIGN_CASES)

    detection_rate = (
        detected_count / total_attacks * 100
        if total_attacks else 0
    )

    protection_rate = (
        prevented_count / total_attacks * 100
        if total_attacks else 0
    )

    false_positive_rate = (
        false_positives / total_benign * 100
        if total_benign else 0
    )

    for category, values in category_summary.items():
        total = values["total"]

        values["detection_rate"] = round(
            values["detected"] / total * 100, 2
        )

        values["protection_rate"] = round(
            values["prevented"] / total * 100, 2
        )

    return {
        "evaluation_type": "advanced_encoded_and_obfuscated_pii",
        "total_attack_cases": total_attacks,
        "attacks_detected": detected_count,
        "leaks_prevented": prevented_count,
        "remaining_leaks": leaked_count,
        "detection_rate": round(detection_rate, 2),
        "protection_rate": round(protection_rate, 2),
        "total_benign_cases": total_benign,
        "false_positives": false_positives,
        "false_positive_rate": round(false_positive_rate, 2),
        "category_summary": category_summary,
        "attack_results": results,
        "limitations": [
            "Only the listed synthetic encoded and obfuscated PII cases are evaluated.",
            "Prompt injection and indirect RAG leakage are not included.",
            "Exact-value checks do not establish resistance to every encoding or evasion technique."
        ]
    }
