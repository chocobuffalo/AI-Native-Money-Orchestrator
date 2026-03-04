import streamlit as st
import requests
from state.history_store import add_transaction_record
from datetime import datetime


API = "http://127.0.0.1:8000"

def render_transaction_form():
    st.subheader("Submit Transaction")
    
    with st.form("transaction_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            transaction_id = st.text_input("Transaction ID", "txn-001")
            amount = st.number_input("Amount (CAD)", min_value=1.0, value=100.0)
            currency = st.selectbox("Currency", ["CAD", "USD"])
            destination = st.text_input("Destination Account", "trusted_account_77")

        with col2:
            risk_region = st.selectbox("Risk Region", ["CA", "US", "INTL"])
            channel = st.selectbox("Channel", ["mobile_app", "web"])
            device_id = st.text_input("Device ID", "dev_123456")
            ip_address = st.text_input("IP Address", "192.168.1.50")

        submitted = st.form_submit_button("Run AI Orchestration")

    if submitted:
        # 1. Preparamos el contexto enriquecido que espera el Decision Orchestrator
        raw_context = {
            "user_id": "user_erika_01",
            "amount": amount,
            "currency": currency,
            "destination": destination,
            "risk_region": risk_region,
            "channel": channel,
            "device_id": device_id,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat() + "Z", # Timestamp simulado
            "is_kyc_verified": True,
            "is_account_blocked": False,
            "destination_country": risk_region
        }

        # 2. Simulamos el historial del usuario para que la IA tenga contexto
        mock_history = {
            "historical_avg_amount": 120.0,
            "known_destinations": ["trusted_account_77", "savings_01"],
            "last_device_id": device_id,
            "last_ip_address": ip_address,
            "transaction_count_30d": 5
        }

        # 3. El payload final que une todo según el contrato de tu API
        payload = {
            "transaction_id": transaction_id,
            "raw_context": raw_context,
            "mock_history": mock_history
        }

        try:
            with st.spinner("🧠 AI Orchestrator analizando riesgos y reglas..."):
                # Llamamos al endpoint que realmente toma las decisiones
                response = requests.post(f"{API}/orchestrate", json=payload)
                
                if response.status_code == 200:
                    decision_data = response.json()
                    
                    # Guardamos en el store local para que los otros tabs (AI Decision, Risk) 
                    # puedan leer y mostrar los resultados
                    add_transaction_record(transaction_id, decision_data)
                    
                    st.success(f"✅ Orquestación completada para {transaction_id}")
                    st.balloons()
                else:
                    st.error(f"Error en el Orchestrator: Código {response.status_code} - {response.text}")
                    
        except Exception as e:
            st.error(f"Error de conexión con el backend: {e}. ¿Está corriendo uvicorn?")
            