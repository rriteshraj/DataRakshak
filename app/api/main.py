
from typing import Literal

from fastapi import (
    FastAPI, HTTPException, Depends, status
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.core.security import create_access_token
from app.core.auth_dependencies import (
    get_current_user,
    require_admin
)
from app.services.auth_service import AuthService
from app.services.privacy_engine import PrivacyEngine
from app.rag.rag_service import RAGService

from app.leaktest.evaluator import evaluate_leaktest
from app.leaktest.attack_evaluator import evaluate_attacks
from app.leaktest.advanced_attack_evaluator import evaluate_advanced_attacks
from app.leaktest.prompt_injection_evaluator import evaluate_prompt_injection


app = FastAPI(
    title="DataRakshak API",
    description="Indian PII-aware Privacy Firewall for LLM and RAG applications",
    version="1.0.0"
)

# ---------------- CORS ----------------

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# ---------------- SERVICES ----------------

engine = PrivacyEngine()
rag_service = RAGService()
auth_service = AuthService()


# ---------------- REQUEST MODELS ----------------

class PrivacyRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    action: Literal["allow", "redact", "block", "tokenize"] = "redact"


class VaultRestoreRequest(BaseModel):
    token: str = Field(..., min_length=1, max_length=100)


class RAGIngestRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=100000)
    document_id: str | None = Field(default=None, max_length=100)


class RAGSearchRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10000)
    top_k: int = Field(default=3, ge=1, le=10)


class RAGAskRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=10000)
    top_k: int = Field(default=3, ge=1, le=10)


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    password: str = Field(..., min_length=12, max_length=128)

class ChangePasswordRequest(BaseModel):
    current_password: str = Field(..., min_length=12, max_length=128)
    new_password: str = Field(..., min_length=12, max_length=128)


# ---------------- HEALTH CHECK ----------------

@app.get("/")
def home():
    return {
        "project": "DataRakshak",
        "status": "running"
    }


# ---------------- AUTHENTICATION ----------------

@app.post("/api/v1/auth/login")
def login(request: LoginRequest):

    user = auth_service.authenticate_user(
        request.username,
        request.password
    )

    if user is None:
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password."
        )

    access_token = create_access_token(
        username=user["username"],
        role=user["role"]
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": 120 * 60,
        "user": {
            "username": user["username"],
            "role": user["role"]
        }
    }

# ---------------- CHANGE ADMIN PASSWORD ----------------

@app.post("/api/v1/auth/change-password")
def change_admin_password(
    request: ChangePasswordRequest,
    admin: dict = Depends(require_admin)
):
    try:
        result = auth_service.change_admin_password(
            username=admin["username"],
            current_password=request.current_password,
            new_password=request.new_password
        )

        return {
            "project": "DataRakshak",
            **result
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
# ---------------- TOKEN VAULT ----------------

@app.post("/api/v1/vault/restore")
def restore_vault_token(
    request: VaultRestoreRequest,
    admin: dict = Depends(require_admin)
):
    try:
        restored_value = engine.vault.restore(
            token=request.token,
            actor=admin["username"]
        )

        return {
            "project": "DataRakshak",
            "status": "restored",
            "restored_value": restored_value
        }

    except KeyError:
        raise HTTPException(
            status_code=404,
            detail="Token not found."
        )

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Token has expired."
        )


# ---------------- PRIVACY ENGINE ----------------

@app.post("/api/v1/process")
def process_text(
    request: PrivacyRequest,
    user: dict = Depends(get_current_user)
):
    # Returning original unprotected data is admin-only.
    if request.action == "allow" and user["role"] != "admin":
        raise HTTPException(
            status_code=403,
            detail="Administrator permission required for allow action."
        )

    try:
        result = engine.process(
            text=request.text,
            action=request.action
        )

        return {
            "project": "DataRakshak",
            "status": result["status"],
            "action": request.action,
            "protected_text": result["text"],
            "detections": result["detections"],
            "detection_count": len(result["detections"]),
            "token_count": result.get("token_count", 0)
        }

    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="Invalid privacy processing request."
        )


# ---------------- RAG INGESTION ----------------

@app.post("/api/v1/rag/ingest")
def ingest_document(
    request: RAGIngestRequest,
    user: dict = Depends(get_current_user)
):
    try:
        result = rag_service.ingest_document(
            text=request.text,
            document_id=request.document_id
        )

        return {
            "project": "DataRakshak",
            **result
        }

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Document ingestion failed."
        )


# ---------------- RAG SEARCH ----------------

@app.post("/api/v1/rag/search")
def search_documents(
    request: RAGSearchRequest,
    user: dict = Depends(get_current_user)
):
    try:
        result = rag_service.search_documents(
            query=request.query,
            top_k=request.top_k
        )

        return {
            "project": "DataRakshak",
            **result
        }

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Document search failed."
        )


# ---------------- RAG + LOCAL LLM ----------------

@app.post("/api/v1/rag/ask")
def ask_rag(
    request: RAGAskRequest,
    user: dict = Depends(get_current_user)
):
    try:
        result = rag_service.generate_answer(
            query=request.query,
            top_k=request.top_k
        )

        return {
            "project": "DataRakshak",
            **result
        }

    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Unable to process the RAG request."
        )

    except RuntimeError:
        raise HTTPException(
            status_code=503,
            detail="Local AI service is unavailable."
        )


# ---------------- DOCUMENT DELETION ----------------

@app.delete("/api/v1/rag/documents/{document_id}")
def delete_document(
    document_id: str,
    admin: dict = Depends(require_admin)
):
    try:
        result = rag_service.delete_document(document_id)

        return {
            "project": "DataRakshak",
            "status": "deleted",
            "result": result
        }

    except (ValueError, KeyError):
        raise HTTPException(
            status_code=404,
            detail="Document not found."
        )


# ---------------- LEAKTEST ----------------

@app.post("/api/v1/leaktest/run")
def run_leaktest(admin: dict = Depends(require_admin)):
    try:
        return {
            "project": "DataRakshak",
            "status": "completed",
            **evaluate_leaktest()
        }
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="LeakTest execution failed."
        )


@app.post("/api/v1/leaktest/attacks")
def run_attack_evaluation(
    admin: dict = Depends(require_admin)
):
    try:
        return {
            "project": "DataRakshak",
            "status": "completed",
            "evaluation_type": "controlled_attack_simulation",
            **evaluate_attacks()
        }
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Attack evaluation failed."
        )


@app.post("/api/v1/leaktest/advanced")
def run_advanced_attack_evaluation(
    admin: dict = Depends(require_admin)
):
    try:
        return {
            "project": "DataRakshak",
            "status": "completed",
            **evaluate_advanced_attacks()
        }
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Advanced attack evaluation failed."
        )


@app.post("/api/v1/leaktest/prompt-injection")
def run_prompt_injection_evaluation(
    admin: dict = Depends(require_admin)
):
    try:
        return {
            "project": "DataRakshak",
            "status": "completed",
            **evaluate_prompt_injection()
        }
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Prompt injection evaluation failed."
        )


# ---------------- RUN SERVER ----------------

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
