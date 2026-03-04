import streamlit as st
import requests
from state.history_store import get_history

API = "http://127.0.0.1:8000"

def render_decision_panel(key_prefix="decision"):
    st.subheader("AI Reasoning & Decision")
    
    history = get_history()
    if not history:
        st.info("No active transactions. Please submit one first.")
        return

    last_tx = history[-1]
    tx_id = last_tx["transaction_id"]
    decision = last_tx["decision"]

    col1, col2 = st.columns([1, 2])

    with col1:
        st.metric("Final Decision", decision.get("decision", "Unknown").upper())
        st.metric("Risk Score", f"{decision.get('risk_score', 0)}/100")

    with col2:
        st.markdown("### 🧠 AI reasoning_log")
        st.info(decision.get("reasoning_log", "No log available"))

    st.divider()
    
    if st.button("Refresh Transparency Layer", key=f"{key_prefix}_refresh_transparency_layer"):
        try:
            explanation = requests.get(f"{API}/explain/{tx_id}").json()
            st.write("#### User-Friendly Explanation:")
            st.success(explanation.get("user_message", "Generating..."))
        except:
            st.write("Waiting for Transparency Layer output...")
