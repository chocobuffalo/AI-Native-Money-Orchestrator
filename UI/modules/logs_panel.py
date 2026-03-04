import streamlit as st
import pandas as pd
from state.history_store import get_history
from state.latency_store import get_latency_records

def render_logs_panel(key_prefix=""):
    st.subheader("Live Logs")

    # Botón con key único para evitar duplicados entre tabs
    if st.button("Refresh Logs", key=f"refresh_logs_{key_prefix}"):

        st.markdown("### Decision Logs")
        history = get_history()
        if history:
            data = []
            for h in history:
                data.append({
                    "transaction_id": h["transaction_id"],
                    "decision": h["decision"].get("decision", "unknown"),
                    "risk_score": h["decision"].get("risk_score", None)
                })
            df_decisions = pd.DataFrame(data)
            st.dataframe(df_decisions, use_container_width=True)
        else:
            st.info("No decisions logged yet.")

        st.markdown("### Bank Latency Logs")
        latency = get_latency_records()
        if latency:
            df_latency = pd.DataFrame(latency)
            st.dataframe(df_latency, use_container_width=True)
        else:
            st.info("No latency logs yet.")
