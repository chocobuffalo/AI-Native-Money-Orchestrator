import streamlit as st
from modules.transaction_form import render_transaction_form
from modules.decision_panel import render_decision_panel
from modules.bank_simulator import render_bank_simulator
from modules.logs_panel import render_logs_panel
from modules.history_panel import render_history_panel
from modules.risk_visualizer import render_risk_visualizer
from modules.latency_charts import render_latency_charts
from modules.operational_context_panel import render_operational_context_panel
from modules.continuity_panel import render_continuity_panel
from modules.operating_model_panel import render_operating_model_panel

st.set_page_config(page_title="AI-Native Orchestrator", layout="wide")

st.title("🛡️ AI-Native Money Movement Decision Operating System")
st.markdown("---")

# Organización por Tabs para una navegación limpia
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "💸 Decision Intake",
    "🧠 Decision Engine",
    "🏦 Continuity & Failure Modes",
    "📊 Cognitive Signal & Performance",
    "📉 Reasoning Trace & Audit Trail",
    "📋 Logs & History (Operating Model)",
    "🧩 Operational Context (Support)",
    "ℹ️ Operating Model"
])

with tab1:
    st.subheader("Decision Intake & Orchestration Trigger")
    render_transaction_form()

with tab2:
    st.subheader("Decision Engine Output & Status Layer")
    render_decision_panel(key_prefix="tab2")

with tab3:
    st.subheader("Continuity & Failure Mode Harness")
    render_continuity_panel()
    st.markdown("---")
    st.subheader("Bank Simulation & Latency")
    render_bank_simulator()

with tab4:
    st.subheader("Cognitive Risk Signal Inspector")
    render_risk_visualizer()
    st.markdown("---")
    st.subheader("Operational Performance & Latency Analytics")
    render_latency_charts()

with tab5:
    st.subheader("Operational Reasoning Trace")
    render_decision_panel(key_prefix="tab5")
    st.markdown("---")
    st.subheader("Unified Decision Audit Trail")
    render_history_panel()

with tab6:
    st.subheader("Live Logs")
    render_logs_panel(key_prefix="tab6")
    st.markdown("---")
    st.subheader("Latency & Bank Simulation History")
    render_latency_charts() 

with tab7:
    render_operational_context_panel()

with tab8:
    render_operating_model_panel()
