import streamlit as st
import pandas as pd
from state.history_store import get_history

def render_history_panel():
    st.subheader("Transaction History")

    history = get_history()
    if not history:
        st.info("No transactions recorded yet.")
        return

    data = []
    for h in history:
        data.append({
            "transaction_id": h["transaction_id"],
            "decision": h["decision"].get("decision", "unknown"),
            "risk_score": h["decision"].get("risk_score", None)
        })

    df = pd.DataFrame(data)
    st.dataframe(df, use_container_width=True)

    st.markdown("### Summary")
    st.write(f"Total transactions: **{len(df)}**")

    decision_counts = df["decision"].value_counts().reset_index()
    decision_counts.columns = ["decision", "count"]
    st.bar_chart(decision_counts.set_index("decision"))
    