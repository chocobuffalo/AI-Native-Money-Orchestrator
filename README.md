🛡️ AI‑Native Money Movement Decision Operating System
An end‑to‑end AI‑native decision system designed to rebuild money‑movement workflows from first principles. The system integrates deterministic rules, cognitive risk scoring, guardrails, fallback heuristics, continuity tracking, and full explainability — all wrapped in a modular FastAPI backend and a multi‑tab Streamlit UI.

This project was built as a real system. It follows modern principles of AI-native architecture, operational resilience, and transparent decision‑making.


🚀 System Architecture Overview

1. Decision Intake Layer
Normalizes transaction context.

Triggers the orchestration pipeline.

Stores transaction history for continuity and support.


2. Decision Orchestrator
Coordinates the full decision pipeline:

Hard Rules Engine

Cognitive Risk Engine (LLM + heuristics)

Guardrails

Fallback Engine

Decision Mapping (green / yellow / red)

Outputs:

decision

next_step

risk_score

reasoning_log

anomaly_flags


3. Status Engine
Maintains the lifecycle of each transaction.

Enforces valid state transitions (Approved, Held, Blocked).

Logs timestamps and decision metadata.


4. Continuity Engine
Tracks:

LLM failures

Guardrail violations

Fallback activations

Latency spikes

Operational anomalies

Provides a real‑time view of system health.


5. Transparency Layer
Generates user‑friendly explanations that combine:

reasoning logs

risk signals

anomaly flags

historical context

Designed for both clients and support teams.


6. Streamlit UI
A multi‑tab operational console:

Decision Intake

Decision Engine

Continuity & Failure Modes

Cognitive Signals

Reasoning Trace & Audit Trail

Logs & History

Operational Context (Support)

Operating Model


🧠 Decision Pipeline

1. Hard Rules
Deterministic checks:

KYC

account blocks

transaction caps

device/IP mismatch

destination risk


2. Cognitive Risk Engine
LLM produces an initial risk score.

Behavioral heuristics adjust the score.

Flags include:

unusual_hour

new_destination

amount_spike

device_ip_mismatch


3. Guardrails
Validate:

JSON structure

score ranges

schema compliance

If guardrails fail → fallback mode.


4. Fallback Engine
Deterministic risk scoring when:

LLM times out

LLM output is invalid

guardrails fail


5. Decision Mapping
green → approve

yellow → hold

red → block


6. Status Engine
Applies the operational state.


7. Continuity Engine
Logs every step for auditability.


🧪 Tech Stack
FastAPI — backend services

Pydantic — data models & validation

Uvicorn — ASGI server

Streamlit — UI

Requests — client calls

Python 3.11

Modular architecture with clear separation of concerns


📦 Running the Project

Backend
bash
uvicorn app.main:app --reload --port 8000

UI
bash
streamlit run UI/app.py

flowchart TD

    %% Intake
    A[User / Client App] --> B[Decision Intake Layer<br/>Normalize + Validate Payload]

    %% Orchestrator
    B --> C[Decision Orchestrator]

    %% Hard Rules
    C --> D[Hard Rules Engine<br/>Deterministic Checks]
    D -->|Fail| Fallback1[Fallback Engine<br/>Deterministic Risk Score]
    D -->|Pass| E[Cognitive Risk Engine<br/>LLM + Heuristics]

    %% Guardrails
    E --> G[Guardrails Validation]
    G -->|Fail| Fallback2[Fallback Engine<br/>Guardrail Failure]
    G -->|Pass| H[Risk Score Mapping<br/>Green / Yellow / Red]

    %% Status Engine
    H --> I[Status Engine<br/>State Transitions]

    %% Continuity Engine
    Fallback1 --> J[Continuity Engine<br/>Failure / Degradation Logs]
    Fallback2 --> J
    E --> J
    G --> J
    I --> J

    %% Transparency Layer
    I --> K[Transparency Layer<br/>User-Friendly Explanation]

    %% UI
    K --> L[Streamlit UI<br/>Decision Engine Tab]
    J --> M[Streamlit UI<br/>Continuity & Failure Modes Tab]
    I --> N[Streamlit UI<br/>Audit Trail & History Tab]

