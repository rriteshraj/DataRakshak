# Project scope

## Problem
Sensitive Indian personal identifiers may be included in prompts and documents processed by AI applications.

## Proposed solution
DataRakshak is a privacy layer that detects and protects identifier-like data before it enters an LLM/RAG workflow, and checks outputs for possible exposure.

## Planned original contribution
LeakTest: a stage-wise test harness that injects synthetic PII into controlled pipeline stages and reports detection, leakage, false-positive and latency metrics.

## Safety and scope boundaries
- Use synthetic data only.
- No UIDAI authentication, Aadhaar ownership checks or claims of real identity verification.
- No real Aadhaar numbers in logs, screenshots, tests or repository.
- Do not store raw identifiers in analytics.
