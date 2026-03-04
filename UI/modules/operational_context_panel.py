import streamlit as st
import requests

API = "http://127.0.0.1:8000"


def render_operational_context_panel():
    st.subheader("AI Operational Context Agent (Support View)")

    user_id = st.text_input("User ID", "user_erika_01")

    if st.button("Fetch Operational Context"):
        try:
            resp = requests.get(f"{API}/operational-context/{user_id}")
            if resp.status_code == 200:
                data = resp.json()

                st.markdown("### Case Summary (Support-Ready)")
                st.success(data.get("support_case_summary", ""))

                st.markdown("### Raw Operational Context")
                st.json(data)
            else:
                st.error(f"Error {resp.status_code}: {resp.text}")
        except Exception as e:
            st.error(f"Error calling Operational Context Agent: {e}")
