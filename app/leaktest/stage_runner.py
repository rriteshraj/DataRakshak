
from app.recognizers.indian_pii_detector import analyze_text


def run_stage(stage_name, input_text, output_text=None, expected_values=None):
    """
    Evaluate PII leakage using independent ground-truth values.
    """

    if output_text is None:
        output_text = ""

    if expected_values is None:
        expected_values = []

    input_detections = analyze_text(input_text)
    output_detections = analyze_text(output_text)

    # Check actual ground-truth PII values in the output.
    leaked_entities = [
        item["type"]
        for item in expected_values
        if item["value"] and item["value"] in output_text
    ]

    return {
        "stage": stage_name,
        "input_detection_count": len(input_detections),
        "output_detection_count": len(output_detections),
        "leaked_count": len(leaked_entities),
        "leaked_entities": leaked_entities,
        "input_length": len(input_text),
        "output_length": len(output_text),
        "output_text": output_text,
    }
