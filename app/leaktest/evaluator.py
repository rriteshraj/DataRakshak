
import os
import time

from app.leaktest.test_dataset import TEST_CASES
from app.leaktest.stage_runner import run_stage
from app.leaktest.metrics import calculate_metrics
from app.recognizers.indian_pii_detector import analyze_text, redact_text
from app.rag.rag_service import RAGService
from app.services.privacy_engine import PrivacyEngine


ENTITY_TYPES = [
    "IN_PAN",
    "IN_AADHAAR",
    "IN_PHONE",
    "EMAIL_ADDRESS",
    "IN_GSTIN",
]

STAGES = [
    "User Prompt",
    "Document Ingestion",
    "Vector Retrieval",
    "LLM Input",
    "LLM Output",
]


def evaluate_leaktest():
    tp = fn = fp = tn = 0
    latencies = []
    stage_results = []

    baseline_leaks = 0
    baseline_stage_summary = {}

    temp_db = os.path.join("data", "leaktest_chroma")
    os.makedirs(temp_db, exist_ok=True)

    for stage in STAGES:
        baseline_stage_summary[stage] = {
            "evaluations": 0,
            "leaked_count": 0,
        }

    for case in TEST_CASES:
        text = case["text"]
        expected = set(case["expected_entities"])
        ground_truth = case["expected_values"]

        # Detection and redaction
        start = time.perf_counter()

        detections = analyze_text(text)
        protected_text = redact_text(text)

        latencies.append(
            (time.perf_counter() - start) * 1000
        )

        actual = {
            item["entity_type"] for item in detections
        }

        for entity in ENTITY_TYPES:
            if entity in expected and entity in actual:
                tp += 1
            elif entity in expected:
                fn += 1
            elif entity in actual:
                fp += 1
            else:
                tn += 1

        # Simulated unprotected baseline:
        # Original PII is allowed to pass through every stage.
        for stage in STAGES:
            baseline_result = run_stage(
                stage_name=stage,
                input_text=text,
                output_text=text,
                expected_values=ground_truth,
            )

            baseline_stage_summary[stage]["evaluations"] += 1
            baseline_stage_summary[stage]["leaked_count"] += (
                baseline_result["leaked_count"]
            )

            baseline_leaks += baseline_result["leaked_count"]

        # Stage 2: Actual protected document ingestion
        case_db = os.path.join(temp_db, case["id"])

        rag = RAGService(
            db_path=case_db,
            collection_name="leaktest_documents"
        )

        rag.ingest_document(
            text=text,
            document_id=case["id"]
        )

        stored = rag.collection.get(
            where={"document_id": case["id"]},
            include=["documents"]
        )

        ingested_text = "\n".join(
            stored.get("documents") or []
        )

        # Stage 3: Actual protected vector retrieval
        retrieval = rag.search_documents(
            query=text,
            top_k=3
        )

        retrieved_text = "\n".join(
            item["text"]
            for item in retrieval["results"]
        )

        # Stage 4: LLM input privacy guard
        raw_llm_input = (
            f"Prompt: {protected_text}\n"
            f"Context: {retrieved_text}"
        )

        input_guard = PrivacyEngine()

        llm_guard_result = input_guard.process(
            text=raw_llm_input,
            action="redact"
        )

        llm_input = llm_guard_result["text"]

        # Stage 5: Simulated LLM response
        simulated_response = (
            f"Simulated response based on: {llm_input}"
        )

        output_guard = PrivacyEngine()

        output_guard_result = output_guard.process(
            text=simulated_response,
            action="redact"
        )

        llm_output = output_guard_result["text"]

        stage_outputs = [
            protected_text,
            ingested_text,
            retrieved_text,
            llm_input,
            llm_output,
        ]

        stage_input = text

        for stage_name, stage_output in zip(
            STAGES, stage_outputs
        ):
            result = run_stage(
                stage_name=stage_name,
                input_text=stage_input,
                output_text=stage_output,
                expected_values=ground_truth,
            )

            stage_results.append({
                "test_id": case["id"],
                **result,
            })

            stage_input = stage_output

    # Total expected PII across the dataset
    total_pii = sum(
        len(case["expected_values"])
        for case in TEST_CASES
    )

    total_leaks = sum(
        result["leaked_count"]
        for result in stage_results
    )

    total_baseline_values = sum(
        item["leaked_count"]
        for item in baseline_stage_summary.values()
    )

    # Existing benchmark metrics
    metrics = calculate_metrics(
        tp=tp,
        fn=fn,
        fp=fp,
        tn=tn,
        leaked_count=total_leaks,
        total_pii=total_pii * len(STAGES),
        latencies_ms=latencies,
    )

    # Stage-wise protected summary
    stage_summary = {}

    for stage in STAGES:
        results = [
            result for result in stage_results
            if result["stage"] == stage
        ]

        leaked = sum(
            result["leaked_count"] for result in results
        )

        stage_summary[stage] = {
            "evaluations": len(results),
            "leaked_count": leaked,
            "protected_count": total_pii - leaked,
        }

    # Comparative baseline vs protected evaluation
    comparison_by_stage = {}

    for stage in STAGES:
        baseline = baseline_stage_summary[stage]["leaked_count"]

        protected = stage_summary[stage]["leaked_count"]

        reduction = (
            ((baseline - protected) / baseline) * 100
            if baseline else 0
        )

        comparison_by_stage[stage] = {
            "baseline_leaks": baseline,
            "protected_leaks": protected,
            "leakage_reduction_rate": round(reduction, 2),
        }

    overall_reduction = (
        ((total_baseline_values - total_leaks)
         / total_baseline_values) * 100
        if total_baseline_values else 0
    )

    comparative_metrics = {
        "baseline_leaks": total_baseline_values,
        "protected_leaks": total_leaks,
        "leaks_prevented": total_baseline_values - total_leaks,
        "leakage_reduction_rate": round(
            overall_reduction, 2
        ),
        "baseline_type": "SIMULATED_UNPROTECTED_PASS_THROUGH",
        "protected_type": "ACTUAL_PROTECTED_PIPELINE",
        "stage_comparison": comparison_by_stage,
    }

    return {
        "total_test_cases": len(TEST_CASES),
        "stages_tested": len(STAGES),
        "metrics": metrics,
        "comparative_metrics": comparative_metrics,
        "stage_summary": stage_summary,
        "stage_results": stage_results,

        "stage_modes": {
            "User Prompt": "LIVE",
            "Document Ingestion": "LIVE",
            "Vector Retrieval": "LIVE",
            "LLM Input": "LIVE_GUARD_NO_MODEL",
            "LLM Output": "SIMULATED_WITH_GUARD",
        },

        "simulation_note": (
            "User Prompt, Document Ingestion and Vector Retrieval "
            "use actual processing. LLM Input uses a live privacy "
            "guard without model transmission. LLM Output uses "
            "a simulated response followed by an actual privacy guard. "
            "The baseline is a simulated unprotected pass-through "
            "reference, not a separately deployed unprotected RAG system."
        ),
    }
