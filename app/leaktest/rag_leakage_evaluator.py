
import tempfile

from app.rag.rag_service import RAGService
from app.recognizers.indian_pii_detector import analyze_text


def evaluate_rag_indirect_leakage():
    synthetic_pan = "ABCDE1234F"

    raw_document = (
        "Employee record for Rahul Sharma. "
        "Department: Finance. "
        f"Employee PAN: {synthetic_pan}. "
        "This document contains confidential employee information."
    )

    # Isolated temporary ChromaDB database.
    # Kept until process exit to avoid Windows file-lock errors.
    temp_db = tempfile.mkdtemp(
        prefix="datarakshak_rag_test_"
    )

    service = RAGService(
        db_path=temp_db,
        collection_name="isolated_leakage_test"
    )

    # Simulate bypassing normal protected ingestion.
    service.collection.add(
        ids=["bypass_document_001"],
        documents=[raw_document],
        metadatas=[{
            "document_id": "bypass_document_001",
            "chunk_index": 0,
            "insertion_method": "direct_database_bypass"
        }]
    )

    # Retrieve through the actual RAG search method.
    search_result = service.search_documents(
        query="Employee record for Rahul Sharma in Finance department",
        top_k=3
    )

    retrieved_chunks = search_result["results"]

    # Check whether the original synthetic PAN was exposed.
    leaked_chunks = [
        item for item in retrieved_chunks
        if synthetic_pan in item["text"]
    ]

    # Detect PII in the content actually returned.
    detected_entities = sorted({
        detection["entity_type"]
        for item in retrieved_chunks
        for detection in analyze_text(item["text"])
    })

    leakage_detected = len(leaked_chunks) > 0

    # Read protection metrics from RAG retrieval.
    protected_chunks = search_result.get("protected_chunks", 0)
    blocked_chunks = search_result.get("blocked_chunks", 0)

    # Classify the evaluation result.
    if leakage_detected:
        evaluation_status = "vulnerability_confirmed"
    elif protected_chunks > 0 or blocked_chunks > 0:
        evaluation_status = "protected"
    else:
        evaluation_status = "no_leak_observed"

    return {
        "evaluation": "indirect_rag_leakage",
        "status": evaluation_status,
        "insertion_method": "direct_chromadb_bypass",
        "documents_inserted": 1,
        "retrieved_chunks": len(retrieved_chunks),
        "pii_detected_in_retrieved_chunks": detected_entities,
        "raw_pii_exposed": leakage_detected,
        "leaked_chunk_count": len(leaked_chunks),
        "protected_chunks": protected_chunks,
        "blocked_chunks": blocked_chunks,
        "retrieval_guard": search_result.get(
            "retrieval_guard", "unknown"
        ),
        "normal_ingestion_bypassed": True,
        "query_blocked": search_result.get("query_blocked", False),
        "note": (
            "Synthetic PII was inserted directly into an isolated "
            "ChromaDB collection, bypassing protected ingestion. "
            "The actual RAG retrieval method was then evaluated."
        )
    }


if __name__ == "__main__":
    result = evaluate_rag_indirect_leakage()

    print("\n========== RAG INDIRECT LEAKAGE EVALUATION ==========\n")

    for key, value in result.items():
        print(f"{key}: {value}")

    print("\n=====================================================")
