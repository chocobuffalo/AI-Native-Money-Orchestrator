import streamlit as st
import pandas as pd
import altair as alt
from state.latency_store import get_latency_records

def render_latency_charts():
    st.subheader("Banking Latency Visualization")
    
    records = get_latency_records()
    if not records:
        st.info("No latency data available yet. Run a bank simulation first.")
        return

    df = pd.DataFrame(records)
    st.markdown("### Latency by Simulation Mode")

    bar_chart = (
        alt.Chart(df)
        .mark_bar()
        .encode(
            x=alt.X("mode:N", title="Mode"),
            y=alt.Y("latency_ms:Q", title="Latency (ms)"),
            color="mode:N",
            tooltip=["transaction_id", "mode", "latency_ms"]
        )
        .properties(height=300)
    )

    st.altair_chart(bar_chart, use_container_width=True)

    st.markdown("### Latency Over Time")
    line_chart = (
        alt.Chart(df)
        .mark_line(point=True)
        .encode(
            x=alt.X("transaction_id:N", title="Transaction ID"),
            y=alt.Y("latency_ms:Q", title="Latency (ms)"),
            color="mode:N",
            tooltip=["transaction_id", "mode", "latency_ms"]
        )
        .properties(height=300)
    )

    st.altair_chart(line_chart, use_container_width=True)
    