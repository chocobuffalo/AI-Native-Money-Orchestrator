import streamlit as st
import altair as alt
import pandas as pd
from state.history_store import get_history

def _risk_color(score: float):
    if score <= 30:
        return "#2ecc71"  # green
    if score <= 70:
        return "#f1c40f"  # yellow
    return "#e74c3c"  # red

def render_risk_visualizer():
    st.subheader("Risk Score Visualization")
    
    history = get_history()
    if not history:
        st.info("No transactions available. Submit one in the Transaction tab.")
        return

    last = history[-1]
    decision = last["decision"]
    risk_score = decision.get("risk_score", None)

    if risk_score is None:
        st.warning("No risk score found in the last decision.")
        return

    st.write(f"Risk Score for transaction **{last['transaction_id']}**: **{risk_score}**")

    df = pd.DataFrame({
        "metric": ["risk_score"],
        "value": [risk_score]
    })

    color = _risk_color(risk_score)

    chart = (
        alt.Chart(df)
        .mark_bar(size=60, color=color)
        .encode(
            x=alt.X("value:Q", scale=alt.Scale(domain=[0, 100])),
            y=alt.Y("metric:N", title="")
        )
        .properties(height=120)
    )

    st.altair_chart(chart, use_container_width=True)

    st.markdown("""
    **Thresholds**
    - 0–30: Low risk (Green)
    - 31–70: Medium risk (Yellow)
    - 71–100: High risk (Red)
    """)
    