
def calculate_metrics(
    tp=0,
    fn=0,
    fp=0,
    tn=0,
    leaked_count=0,
    total_pii=0,
    latencies_ms=None,
):
    """Calculate privacy detection and leakage metrics."""

    latencies_ms = latencies_ms or []

    detection_rate = tp / (tp + fn) if tp + fn else 0
    false_positive_rate = fp / (fp + tn) if fp + tn else 0

    leakage_rate = leaked_count / total_pii if total_pii else 0
    protection_rate = 1 - leakage_rate if total_pii else 0

    avg_latency = (
        sum(latencies_ms) / len(latencies_ms)
        if latencies_ms else 0
    )

    return {
        "detection_rate": round(detection_rate * 100, 2),
        "leakage_rate": round(leakage_rate * 100, 2),
        "protection_rate": round(protection_rate * 100, 2),
        "false_positive_rate": round(false_positive_rate * 100, 2),
        "average_latency_ms": round(avg_latency, 2),
        "counts": {
            "true_positives": tp,
            "false_negatives": fn,
            "false_positives": fp,
            "true_negatives": tn,
            "leaked_entities": leaked_count,
            "total_pii_entities": total_pii,
        },
    }
