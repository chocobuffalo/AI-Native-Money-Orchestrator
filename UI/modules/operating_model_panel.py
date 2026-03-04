import streamlit as st

def render_operating_model_panel():
    st.subheader("AI-Native Decision Operating Model")

    st.markdown("""
    This system is an **AI-Native Decision Operating System** for money movement.

    It replaces fragmented, ticket-based workflows with a **single operational layer** that:
    - unifies hard rules, cognitive risk, and human overrides  
    - exposes decisions as APIs, not emails or tickets  
    - embeds continuity & failure modes into the core pipeline  
    - produces structured reasoning and audit trails by default  
    """)

    st.markdown("---")
    st.markdown("### Core Modules")

    st.markdown("""
    **1. Decision Intake & Orchestration**  
    - Normalizes raw transaction context  
    - Applies hard rules and cognitive risk  
    - Calls LLM (or fallback heuristics)  
    - Maps to next_step: approve / hold / block  

    **2. Status & Transparency Layer**  
    - Persists final status per transaction  
    - Stores risk_score, decision_reason, reasoning_log, anomaly_flags  
    - Powers the Decision Engine tab and the Support Context Agent  

    **3. Continuity & Failure Modes**  
    - Tracks LLM failures, guardrail failures, bank failures, high latency  
    - Classifies system health: healthy / degraded / failed  
    - Makes resilience observable, not implicit  
    """)

    st.markdown("---")
    st.markdown("### Operational Context & Support")

    st.markdown("""
    **4. AI Operational Context Agent**  
    - Given a user_id, aggregates:  
      - last transaction  
      - last decision & status  
      - risk_score & flags  
      - history summary  
    - Produces a **support-ready case summary**  
    - Replaces manual digging across tools with a single endpoint  
    """)

    st.markdown("---")
    st.markdown("### Logs, History & Auditability")

    st.markdown("""
    **5. Logs & History**  
    - Decision logs: transaction_id, decision, risk_score  
    - Bank latency logs: mode, latency_ms, failures  
    - Unified audit trail for risk, compliance, and support  

    **6. Cognitive Signal & Performance**  
    - Visualizes risk score evolution  
    - Connects model behavior with operational outcomes  
    - Makes the system explainable to non-ML stakeholders  
    """)

    st.markdown("---")
    st.markdown("### How this changes the operating model")

    st.markdown("""
    **Legacy model**  
    - Decisions scattered across tools  
    - Support depends on tribal knowledge  
    - Failures are invisible until they hurt customers  
    - No single source of truth for “why was this blocked?”  

    **AI-Native model**  
    - Decisions, status, and reasoning are **first-class objects**  
    - Support works from structured case summaries, not guesswork  
    - Continuity & failure modes are observable and trackable  
    - Every decision is explainable, auditable, and reproducible  
    """)
