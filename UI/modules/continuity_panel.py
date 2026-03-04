import streamlit as st
import requests
import pandas as pd

API = "http://127.0.0.1:8000"

def render_continuity_panel():
    st.subheader("Continuity & Failure Modes Dashboard")

    # Botón con key único
    if st.button("Refresh Continuity Status", key="continuity_refresh_status"):
        try:
            resp = requests.get(f"{API}/continuity/status")
            data = resp.json()

            # Estado general del sistema
            st.metric("System Health", data["system_health"].upper())

            # Eventos recientes
            events = data["recent_events"]
            if events:
                df = pd.DataFrame(events)
                st.markdown("### Recent Continuity Events")
                st.dataframe(df, use_container_width=True)
            else:
                st.info("No continuity events recorded yet.")

        except Exception as e:
            st.error(f"Error fetching continuity status: {e}")
