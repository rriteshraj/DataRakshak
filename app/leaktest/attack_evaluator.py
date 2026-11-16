
from app.leaktest.stage_runner import run_stage
from app.services.privacy_engine import PrivacyEngine


ATTACK_CASES = [
    ("IN_PAN", "ABCDE1234F"),
    ("IN_AADHAAR", "234567890123"),
    ("IN_PHONE", "9876543210"),
    ("EMAIL_ADDRESS", "test@example.com"),
    ("IN_GSTIN", "22AAAAA0000A1Z5"),
]


def evaluate_attacks():
    engine = PrivacyEngine(vault=object())

    results = []
    detected_attacks = 0
    prevented_leaks = 0

    for entity, value in ATTACK_CASES:
        attack_text = f"Sensitive information: {value}"

        # Test whether raw PII leakage is detected.
        attack_result = run_stage(
            stage_name="Controlled Attack",
            input_text=attack_text,
            output_text=attack_text,
            expected_values=[
                {"type": entity, "value": value}
            ],
        )

        # Test whether the privacy engine prevents leakage.
        protected_text = engine.process(
            text=attack_text,
            action="redact"
        )["text"]

        defense_result = run_stage(
            stage_name="Privacy Defense",
            input_text=attack_text,
            output_text=protected_text,
            expected_values=[
                {"type": entity, "value": value}
            ],
        )

        attack_detected = attack_result["leaked_count"] > 0
        leak_prevented = defense_result["leaked_count"] == 0

        detected_attacks += int(attack_detected)
        prevented_leaks += int(leak_prevented)

        results.append({
            "entity_type": entity,
            "attack_detected": attack_detected,
            "leak_prevented": leak_prevented,
            "raw_leak_count": attack_result["leaked_count"],
            "protected_leak_count": defense_result["leaked_count"],
            "protected_text": protected_text,
        })

    # Combined multi-PII attack
    combined_values = [
        {"type": entity, "value": value}
        for entity, value in ATTACK_CASES
    ]

    combined_text = (
        "PAN ABCDE1234F, Aadhaar 234567890123, "
        "phone 9876543210, email test@example.com, "
        "GSTIN 22AAAAA0000A1Z5"
    )

    combined_raw = run_stage(
        stage_name="Combined Attack",
        input_text=combined_text,
        output_text=combined_text,
        expected_values=combined_values,
    )

    combined_protected = engine.process(
        text=combined_text,
        action="redact"
    )["text"]

    combined_defense = run_stage(
        stage_name="Combined Defense",
        input_text=combined_text,
        output_text=combined_protected,
        expected_values=combined_values,
    )

    combined_result = {
        "raw_leaks_detected": combined_raw["leaked_count"],
        "protected_leaks": combined_defense["leaked_count"],
        "all_leaks_prevented": combined_defense["leaked_count"] == 0,
        "protected_text": combined_protected,
    }

    return {
        "total_attack_cases": len(ATTACK_CASES),
        "attacks_detected": detected_attacks,
        "individual_leaks_prevented": prevented_leaks,
        "combined_attack": combined_result,
        "attack_results": results,
    }