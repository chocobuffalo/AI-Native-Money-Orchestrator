📑 TECHNICAL SPEC — AI‑Native Money Movement Orchestrator

(Versión final, completa y lista para Notion)

---

## 1. Arquitectura General del Sistema

El AI‑Native Money Movement Orchestrator es un sistema modular que combina:

- Reglas determinísticas (Hard Rules Engine)
- Razonamiento cognitivo (Cognitive Risk Engine con LLM)
- Validación y seguridad (LLM Guardrails)
- Resiliencia (Fallback Engine)
- Orquestación de decisiones (Decision Orchestrator)
- Estados claros (Status Engine)
- Explicabilidad humana (Transparency Layer)
- Supervisión humana (HITL Dashboard)
- Simulación bancaria (Mock Banking Layer)
- Trazabilidad completa (Logging + Audit Trail)

El sistema es AI‑native, no un chatbot: la IA participa en la toma de decisiones, no solo en la interfaz.

---

## 2. Componentes del Sistema (Especificación Técnica)

A continuación se describen todos los módulos del MVP, sus responsabilidades, entradas, salidas y dependencias.

---

### 2.1 Ingestion Layer

**Responsabilidad:**

Recibir, validar y normalizar señales de entrada.

**Inputs:**

- user_id
- amount
- currency
- destination
- timestamp
- device_id
- ip_address
- historical context (mock)

**Outputs:**

```json
{
  "contextbundleid": "uuid",
  "normalized_context": { ... }
}
```

**Dependencias:**

- Ninguna

---

### 2.2 Hard Rules Engine

**Responsabilidad:**

Aplicar reglas determinísticas que nunca dependen del LLM.

**Reglas incluidas:**

- Límites regulatorios
- Caps diarios/mensuales
- AML/KYC flags
- Cuentas bloqueadas
- Restricciones horarias
- Destinos prohibidos

**Inputs:**

- normalized_context
- policy_store

**Outputs:**

```json
{
  "hardrulespass": true,
  "violations": []
}
```

**Dependencias:**

- Policy Store
- Logging Utility

---

### 2.3 Cognitive Risk Engine (LLM)

**Responsabilidad:**

Detectar anomalías y generar un puntaje de riesgo basado en razonamiento.

**Inputs:**

- normalized_context
- historical behavior
- transaction metadata

**Outputs:**

```json
{
  "risk_score": 0-100,
  "reasoning_log": "string",
  "anomalyflags": ["behavioral", "amountspike"]
}
```

**Dependencias:**

- LLM API
- Guardrails
- Logging Utility

---

### 2.4 LLM Guardrail Layer

**Responsabilidad:**

Validar la salida del LLM para evitar errores, alucinaciones o formatos inválidos.

**Validaciones:**

- JSON válido
- Campos obligatorios
- Rangos seguros
- Tipos correctos
- Semántica coherente

**Outputs:**

- LLM output validado
- O activación del fallback

**Dependencias:**

- Cognitive Scorer
- Logging Utility

---

### 2.5 Fallback Engine

**Responsabilidad:**

Garantizar resiliencia cuando el LLM falla.

**Activación:**

- JSON inválido
- Campos faltantes
- Latencia excesiva
- Valores fuera de rango
- Errores de API

**Outputs:**

```json
{
  "risk_score": 50,
  "reasoning_log": "Fallback activated due to invalid LLM output.",
  "anomaly_flags": ["fallback"]
}
```

**Dependencias:**

- Guardrails
- Logging Utility

---

### 2.6 Decision Orchestrator

**Responsabilidad:**

Combinar Hard Rules + Cognitive Score + Fallback para tomar una decisión final.

**Lógica:**

- Green (<10): aprobar
- Yellow (10–70): retener + explicar + HITL
- Red (>70): bloquear + escalar

**Outputs:**

```json
{
  "decision": "green | yellow | red",
  "next_step": "approve | hold | escalate"
}
```

**Dependencias:**

- Hard Rules Engine
- Cognitive Scorer
- Fallback Engine
- Logging Utility

---

### 2.7 Status Engine

**Responsabilidad:**

Mantener estados claros y trazables.

**Estados:**

- Approved
- Held
- Blocked
- Needs Info

**Outputs:**

```json
{
  "status": "Held",
  "updated_at": "timestamp"
}
```

**Dependencias:**

- Decision Orchestrator
- Logging Utility

---

### 2.8 Transparency Layer

**Responsabilidad:**

Convertir decisiones técnicas en explicaciones humanas.

**Inputs:**

- decision
- risk_score
- reasoning_log

**Outputs:**

```json
{
  "message": "Explicación humana y empática"
}
```

**Dependencias:**

- LLM (opcional)
- Logging Utility

---

### 2.9 Human‑in‑the‑Loop Dashboard

**Responsabilidad:**

Permitir intervención humana en casos Yellow/Red.

**UI muestra:**

- Recomendación IA
- Factores de riesgo
- Reasoning log
- Botones:
    - Aprobar
    - Rechazar
    - Pedir más info

**Dependencias:**

- Status Engine
- Transparency Layer
- Logging Utility

---

### 2.10 Mock Banking Layer

**Responsabilidad:**

Simular respuestas bancarias para demo.

**Simula:**

- Latencia
- Fallos
- Respuestas aprobadas/rechazadas

**Outputs:**

```json
{
  "bank_status": "approved",
  "latency_ms": 120
}
```

---

### 2.11 Logging Utility

**Responsabilidad:**

Registrar todo en formato JSON estructurado.

**Logs incluyen:**

- Inputs
- Outputs
- Decisiones
- Activación de fallback
- Activación de guardrails
- Latencias
- Overrides humanos

---

## 3. API Contracts (resumen técnico)

POST /ingest

Recibe metadata → devuelve contextbundleid.

POST /score

Ejecuta Hard Rules + Cognitive Scorer.

POST /orchestrate

Devuelve decisión final.

POST /status

Actualiza o consulta estado.

POST /explain

Genera explicación humana.

POST /mock-bank

Simula respuesta bancaria.

(Los JSON completos ya están en el Documentation Hub.)

---

## 4. Data Structures

Transaction

- user_id
- amount
- currency
- destination
- timestamp
- device_id
- ip_address

RiskResult

- risk_score
- reasoning_log
- anomaly_flags

DecisionResult

- decision
- next_step

Status

- status
- updated_at

Explanation

- message

---

## 5. Requisitos No Funcionales

**Performance**

- Latencia objetivo: < 1.5s
- LLM timeout: 1s

**Resiliencia**

- Fallback obligatorio
- Guardrails estrictos

**Seguridad**

- No almacenar datos sensibles
- Logging sin PII

**Explicabilidad**

- Cada decisión debe tener reasoning_log
- Cada estado debe tener explicación humana

**Trazabilidad**

- Audit Trail completo
- Logs estructurados

---

## 6. Definition of Done (para todos los módulos)

- Cumple con el spec técnico
- Maneja edge cases
- Maneja errores del LLM
- Tiene logs en puntos críticos
- Tiene unit tests (happy + edge + fallback)
- Integrado con el orquestador
- Documentado en README
- Probado manualmente

---

## 7. Unit Test Requirements

- Happy path
- Invalid input
- Missing fields
- Boundary values
- LLM failure → fallback
- Policy Store override
- Logging triggered

---

## 8. Logging Requirements

- Input recibido
- Output generado
- Decisiones tomadas
- Activación de fallback
- Activación de guardrails
- Tiempos de ejecución

9. Diagrama de Arquitectura (ASCII)

┌────────────────────┐
│      USER APP      │
│ (Transfer Request) │
└────────┬───────────┘
         │
         ▼
┌───────────────────────┐
│    Ingestion Layer    │
│   (API / Backend)     │
└────────┬──────────────┘
         │
         ▼
┌──────────────────────────┐
│    Hard Rules Engine     │
│ (limits, AML, schedule)  │
└────────┬─────────────────┘
         │
         ▼
┌───────────────────────────────┐
│     Cognitive Risk Engine     │
│   (LLM + heuristics, scoring) │
└───────────┬──────────────────┘
            │
            ▼
┌────────────────────────┐
│   Decision Orchestrator│
└───────┬─────────┬─────┘
        │         │
 Low    │         │  Med/High
 Risk   │         │
        ▼         ▼
┌──────────────┐ ┌─────────────────────────┐
│ Mock Banking │ │ Human-in-the-Loop Panel │
│   Layer      │ │  (Security / Ops UI)    │
└────┬─────────┘ └──────────┬──────────────┘
     │                       │
     └──────────┬────────────┘
                ▼
     ┌────────────────────────┐
     │   Transparency Layer   │
     │ (LLM: user explanation)│
     └────────┬───────────────┘
              │
              ▼
     ┌───────────────────────┐
     │      USER APP         │
     │ (Status + Explanation)│
     └───────────────────────┘

     ┌────────────────────┐
     │ Logging & Audit    │
     │ (all decisions)    │
     └────────────────────┘
     