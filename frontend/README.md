# DataRakshak

**Your Data. Your Privacy. Our Protection.**

An Indian PII-aware privacy firewall with stage-wise leakage detection for LLM and RAG applications.

## Project Overview

DataRakshak is a privacy and security prototype designed to detect and protect Indian Personally Identifiable Information (PII) throughout text-processing and retrieval workflows.

The project combines PII detection, privacy-preserving transformations, encrypted token storage, authentication, authorization and leakage testing.

## Implemented Modules

### 1. Indian PII Detection
- Aadhaar-format number detection
- PAN detection
- GSTIN detection
- Indian mobile number detection
- Driving Licence pattern detection
- Email address detection
- Presidio-based recognition with custom recognizers

### 2. Privacy Engine
- Allow
- Redact
- Block
- Tokenize

### 3. Secure Token Vault
- SQLite-based token storage
- Fernet encryption of original values
- Token expiry
- Controlled restoration
- SHA-256 token fingerprints in audit records

### 4. Authentication and Authorization
- JWT-based authentication
- Argon2 password hashing
- Admin and user roles
- Admin-only token restoration
- Protected API endpoints

### 5. Leakage Testing
- PII leakage evaluation
- Advanced attack simulation
- Prompt-injection simulation
- RAG leakage evaluation
- RAG prompt-injection evaluation

**Note:** Attack and prompt-injection evaluations are prototype-level simulations. Their results do not establish production-grade protection against all attacks.

### 6. RAG and Frontend
- ChromaDB-based document retrieval functionality
- Retrieval-stage privacy checks
- React-based application interface
- Privacy scanner, dashboard, Token Vault and simulation interfaces

LLM/Ollama integration and complete end-to-end integration should be verified separately before treating the system as production-ready.

## Technology Stack

**Backend:** Python, FastAPI, Presidio, spaCy

**Security:** Fernet, SQLite, PyJWT, Argon2

**RAG:** ChromaDB

**Frontend:** React, Vite, JavaScript, Tailwind CSS

**Testing:** Pytest

## Project Structure

```text
DataRakshak/
├── app/
│   ├── api/
│   ├── core/
│   ├── database/
│   ├── leaktest/
│   ├── rag/
│   ├── recognizers/
│   └── services/
├── data/
├── docs/
├── frontend/
├── tests/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Installation and Setup

### Prerequisites

- Python 3.12
- Node.js and npm
- Git

### 1. Clone the repository

```powershell
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd datarakshak
```

### 2. Create Python environment

```powershell
py -3.12 -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

### 3. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Generate a Fernet key:

```powershell
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Generate an authentication secret:

```powershell
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Put the generated values in `.env`:

- `VAULT_ENCRYPTION_KEY`
- `AUTH_SECRET_KEY`
- `AUTH_TOKEN_EXPIRE_MINUTES=120`

**Important:** Never commit `.env`, encryption keys, authentication secrets or database files. Keep the same vault encryption key when accessing an existing encrypted database.

### 4. Initialize the administrator

```powershell
python -m app.core.create_admin
```

Follow the prompts to create the initial administrator account.

### 5. Start the backend

From the project root:

```powershell
python -m uvicorn app.api.main:app --reload --port 8000
```

Backend:

`http://127.0.0.1:8000`

API documentation:

`http://127.0.0.1:8000/docs`

### 6. Start the frontend

Open a separate terminal:

```powershell
cd frontend
npm install
npm run dev -- --port 5174
```

Frontend:

`http://localhost:5174`

Keep both backend and frontend terminals running.

## Run Tests

Activate the Python virtual environment and run:

```powershell
python -m pytest -v
```

The current recorded regression suite contains 33 passing tests. Run the suite again after changes or integration.

## Security Considerations

- Use synthetic PII examples for testing.
- PII pattern detection does not establish identity or validate government-issued identifiers.
- Keep encryption keys and JWT secrets private.
- Do not commit `.env`, database files or real personal information.
- Token restoration requires administrator authorization through the protected API.
- Prototype-level security tests are not a substitute for independent security assessment.

## Current Development Status

DataRakshak is being developed collaboratively:

- **Student 1:** Privacy, PII detection, Token Vault and security.
- **Student 2:** LLM integration, RAG, AI functionality and frontend.

The final milestone is to integrate both modules and validate the complete application through end-to-end testing.

## Project Tagline

**Your Data. Your Privacy. Our Protection.**