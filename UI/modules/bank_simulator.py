import streamlit as st
import requests
import time
from state.history_store import get_history
from state.latency_store import add_latency_record

API = "http://127.0.0.1:8000"

def render_bank_simulator():
    st.subheader("Bank Simulation")

    history = get_history()
    if not history:
        st.info("No transactions available. Submit one in the Transaction tab.")
        return

    last = history[-1]
    transaction_id = last["transaction_id"]

    st.write(f"Simulating bank call for transaction **{transaction_id}**")

    mode = st.selectbox("Simulation Mode", ["normal", "slow", "fail"])

    if st.button("Run Bank Simulation"):
        start = time.time()
        try:
            result = requests.post(
                f"{API}/bank/simulate", 
                json={"transaction_id": transaction_id, "mode": mode}
            ).json()

            end = time.time()
            latency_ms = round((end - start) * 1000, 2)

            st.success(f"Bank simulation completed in {latency_ms} ms")
            st.json(result)

            add_latency_record(transaction_id, mode, latency_ms)

        except Exception as e:
            st.error(f"Error calling bank simulation: {e}. Check if /mock-bank endpoint exists in your FastAPI.")
            