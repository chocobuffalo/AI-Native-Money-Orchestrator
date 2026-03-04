📘 API Contracts — AI‑Native Money Movement Orchestrator

> Todos los endpoints son parte de un backend FastAPI.
> 

> Formato de datos: JSON.
> 

> Autenticación: omitida en el MVP (simulado).
> 

---

## 1. POST /ingest

**Descripción:**

Recibe los datos de la transacción y genera un contextbundleid que se usará en el resto del flujo.

**Request body:**
{
  "user_id": "string",
  "amount": 120.50,
  "currency": "CAD",
  "destination": "externalbankaccount",
  "timestamp": "2026-02-24T12:00:00Z",
  "device_id": "device-123",
  "ip_address": "192.168.0.1",
  "channel": "mobile_app"
}

Response 200:
{
  "contextbundleid": "c0c3f0c2-1234-4567-89ab-abcdef012345",
  "normalized_context": {
    "user_id": "string",
    "amount": 120.5,
    "currency": "CAD",
    "destination": "externalbankaccount",
    "risk_region": "CA",
    "channel": "mobile_app",
    "ip_address": "192.168.0.1"
  }
}
## 2. POST /score

**Descripción:**

Ejecuta Hard Rules + Cognitive Risk Engine (LLM) sobre un contextbundleid.

**Request body:**
{
  "contextbundleid": "c0c3f0c2-1234-4567-89ab-abcdef012345"
}
Response 200:
{
  "contextbundleid": "c0c3f0c2-1234-4567-89ab-abcdef012345",
  "hard_rules": {
    "hardrulespass": true,
    "violations": []
  },
  "cognitive_risk": {
    "risk_score": 37,
    "reasoning_log": "User usually sends 20-50 CAD, this is 120.50 but still within normal range.",
    "anomaly_flags": []
  },
  "source": "llm|fallback"
}
## 3. POST /orchestrate

**Descripción:**

Combina resultados de reglas y riesgo para producir una decisión final (Green / Yellow / Red).

**Request body:**
{
  "contextbundleid": "c0c3f0c2-1234-4567-89ab-abcdef012345",
  "hard_rules": {
    "hardrulespass": true,
    "violations": []
  },
  "cognitive_risk": {
    "risk_score": 37,
    "reasoning_log": "User usually sends 20-50 CAD, this is 120.50 but still within normal range.",
    "anomaly_flags": []
  }
}
Response 200:
{
  "contextbundleid": "c0c3f0c2-1234-4567-89ab-abcdef012345",
  "decision": "green",
  "next_step": "approve",
  "decision_reason": "Low risk score and no hard rule violations."
}
## 4. POST /status

**Descripción:**

Consulta o actualiza el estado de una transacción en el orquestador.

**Request body (consulta):**
{
  "transaction_id": "txn-12345"
}
Response 200 (ejemplo):
{
  "transaction_id": "txn-12345",
  "status": "Held",
  "updated_at": "2026-02-24T12:05:00Z",
  "decision": "yellow",
  "risk_score": 68,
  "reasoning_log": "First time sending 1,000 CAD to a new external account.",
  "requireshumanreview": true
}
Request body (actualización desde HITL):
{
  "transaction_id": "txn-12345",
  "status": "Approved",
  "updated_by": "analyst-001",
  "comment": "Reviewed and approved. Destination verified."
}
Response 200 (actualización):
{
  "transaction_id": "txn-12345",
  "status": "Approved",
  "updated_at": "2026-02-24T12:10:00Z",
  "updated_by": "analyst-001"
}
## 5. POST /explain

**Descripción:**

Genera una explicación humana y empática para el usuario basada en la decisión técnica.

**Request body:**
{
  "transaction_id": "txn-12345",
  "decision": "yellow",
  "risk_score": 68,
  "reasoning_log": "First time sending 1,000 CAD to a new external account.",
  "status": "Held"
}
Response 200:
{
  "transaction_id": "txn-12345",
  "user_message": "Estamos revisando tu transferencia de 1,000 CAD por seguridad, ya que es la primera vez que envías fondos a esta cuenta externa. Estarán disponibles en un máximo de 24 horas.",
  "eta": "24h",
  "support_hint": "Si no reconoces esta operación, contáctanos de inmediato desde la app."
}
## 6. POST /mock-bank

**Descripción:**

Simula la respuesta de un banco para efectos de demo.

**Request body:**
{
  "transaction_id": "txn-12345",
  "mode": "normal|slow|fail"
}
Response 200 (ejemplo normal):
{
  "transaction_id": "txn-12345",
  "bank_status": "approved",
  "latency_ms": 180
}
Response 200 (ejemplo fallo):
{
  "transaction_id": "txn-12345",
  "bank_status": "failed",
  "latency_ms": 1200,
  "errorcode": "BANKTIMEOUT"
}
## 7. POST /hitl/queue

**Descripción:**

Lista las transacciones que requieren revisión humana (Yellow/Red).

**Request body:**
{
  "filter": "pending_only"
}
Response 200:
{
  "items": [
    {
      "transaction_id": "txn-12345",
      "user_id": "user-001",
      "amount": 1000,
      "currency": "CAD",
      "status": "Held",
      "decision": "yellow",
      "risk_score": 68,
      "reasoning_log": "First time sending 1,000 CAD to a new external account.",
      "created_at": "2026-02-24T12:03:00Z"
    }
  ]
}
## 8. POST /hitl/decision

**Descripción:**

Permite que un analista tome una decisión final sobre una transacción en cola.

**Request body:**
{
  "transaction_id": "txn-12345",
  "action": "approve|reject|requestmoreinfo",
  "analyst_id": "analyst-001",
  "comment": "Reviewed documents, looks legitimate."
}
Response 200:
{
  "transaction_id": "txn-12345",
  "final_status": "Approved",
  "updated_at": "2026-02-24T12:15:00Z",
  "analyst_id": "analyst-001"
}
