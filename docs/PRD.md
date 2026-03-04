📘 1. PRD Técnico — AI‑Native Money Movement Orchestrator

### 1.1 Resumen Ejecutivo

El AI‑Native Money Movement Orchestrator es un sistema de decisión inteligente que vive entre la UI y los rieles bancarios. Combina:

- Reglas determinísticas (Hard Rules)
- Razonamiento cognitivo (LLM)
- Orquestación inteligente
- Explicabilidad humana
- Supervisión humana (HITL)
- Fallback resiliente
- Trazabilidad completa

Su propósito es resolver los problemas reales que los usuarios de Wealthsimple reportan:

retenciones sin explicación, decisiones inconsistentes, soporte lento, falta de transparencia y errores silenciosos.

Este MVP no mueve dinero real.

Demuestra cómo Wealthsimple podría modernizar su sistema de riesgo y retenciones con IA.

---

### 1.2 Problem Statement

Basado en evidencia real de usuarios:

- Retenciones sin explicación
- Errores silenciosos
- Falta de transparencia
- Falta de estados claros
- Soporte lento
- Decisiones inconsistentes
- Falta de trazabilidad

El sistema actual carece de:

- Explicabilidad
- Razonamiento contextual
- Fallback robusto
- Supervisión humana integrada
- Estados claros
- Logs estructurados

---

### 1.3 Objetivos del MVP

**Objetivos funcionales**

- Evaluar transacciones con IA + reglas duras
- Explicar decisiones en lenguaje humano
- Reducir falsos positivos
- Mantener estados claros
- Permitir intervención humana en casos críticos
- Registrar todas las decisiones

**Objetivos técnicos**

- Arquitectura AI‑native
- Orquestación modular
- Guardrails para LLM
- Fallback determinístico
- Logging estructurado
- API Contracts claros
- UI simple pero demostrativa

**Objetivos de demo**

- Mostrar que el sistema “piensa”
- Mostrar explicabilidad
- Mostrar resiliencia
- Mostrar HITL
- Mostrar trazabilidad

---

### 1.4 Non‑Goals

- No mover dinero real
- No reemplazar rieles bancarios
- No realizar KYC real
- No integrar proveedores externos reales
- No construir un sistema de producción

---

## 🛠 2. Arquitectura del MVP (Stack Sugerido)

### 2.1 Frontend

- Streamlit (rápido para MVP)
- Dos vistas:
    - User View (transferencia + explicación)
    - Analyst View (HITL)

### 2.2 Backend

- FastAPI (Python)
- Pydantic para contratos
- Uvicorn para ejecución

### 2.3 IA

- GPT‑4o mini (rápido y barato)
- GPT‑4o (para explicabilidad si se requiere)
- Orquestación directa o con LangChain / Vercel AI SDK

### 2.4 Sidecars

- Policy Store
- Audit Trail
- Logging JSON
- Mock Banking Layer

### 2.5 Infra

- Backend: Render / Railway
- Frontend: Vercel

---

## 🧠 3. Mapa de Flujo y Lógica de Datos

| Etapa | Componente | Acción |
| --- | --- | --- |
| Ingesta | API / UI | Recibe user_id, amount, destination, IP |
| Normalización | Context Normalizer | Limpia y enriquece señales |
| Reglas | Hard Rules Engine | Validaciones determinísticas |
| Scoring | Cognitive Risk Engine | Detecta anomalías y genera risk_score |
| Guardrails | LLM Guardrail Layer | Valida JSON y activa fallback |
| Fallback | Fallback Engine | Decisión determinística |
| Orquestación | Decision Orchestrator | Green / Yellow / Red |
| Estado | Status Engine | Approved / Held / Blocked / Needs Info |
| Explicación | Transparency Layer | Mensaje humano |
| HITL | Analyst Panel | Aprobación / Rechazo / Más info |
| Auditoría | Audit Trail | Registra todo |

---

## 🧩 4. Especificaciones de Funcionalidades

### 4.1 Hard Rules Engine

- Límites regulatorios
- Caps diarios/mensuales
- AML/KYC flags
- Cuentas bloqueadas
- Restricciones horarias
- Output: pass/fail + razones

### 4.2 Cognitive Risk Engine (LLM)

- Input: JSON con contexto
- Detecta anomalías y cambios de comportamiento
- Output:
    - risk_score (0–100)
    - reasoning_log
    - anomaly_flags

### 4.3 LLM Guardrail Layer

- Validación de JSON
- Rango seguro
- Campos obligatorios
- Activación de fallback

### 4.4 Fallback Engine

- Decisiones determinísticas cuando:
    - LLM falla
    - JSON inválido
    - Latencia > threshold

### 4.5 Decision Orchestrator

- Green (<10) → auto‑approve
- Yellow (10–70) → hold + explain + HITL
- Red (>70) → block + escalate

### 4.6 Status Engine

- Approved
- Held
- Blocked
- Needs Info

### 4.7 Transparency Layer

Traduce decisiones técnicas a mensajes humanos empáticos.

Ejemplo:

> “Estamos revisando tu transferencia de $1,000 porque es la primera vez que envías fondos a esta cuenta externa. Estarán disponibles en 24h.”
> 

### 4.8 Human‑in‑the‑Loop Panel

- Recomendación IA
- Factores de riesgo
- Reasoning log
- Botones:
    - Aprobar
    - Rechazar
    - Pedir más info

### 4.9 Mock Banking Layer

- Simula latencia
- Simula fallos
- Simula respuestas bancarias

---

## 🧪 5. Escenarios de Prueba (Mock Data)

**Happy Path**

- $20 a contacto frecuente
- Green → Approved inmediato

**Friction Point**

- $1,000 a cuenta nueva
- Yellow → Hold + explicación + HITL

**Security Guard**

- Retiro masivo tras cambio de contraseña
- Red → Block + alerta

---

## 📊 6. RICE Analysis

| Componente | Reach | Impact | Confidence | Effort | RICE |
| --- | --- | --- | --- | --- | --- |
| --- | ---: | ---: | ---: | ---: | ---: |
| Hard Rules Engine | 10 | 9 | 8 | 3 | 240 |
| Cognitive Scorer | 10 | 9 | 8 | 4 | 180 |
| Guardrails | 9 | 8 | 8 | 2 | 288 |
| Fallback Engine | 9 | 8 | 8 | 2 | 288 |
| Orchestrator | 10 | 9 | 8 | 3 | 240 |
| Status Engine | 10 | 8 | 9 | 2 | 360 |

---

## 🗺 7. Roadmap MVP (3 días)

**Día 1 — Definición de la Verdad**

- Dataset mock (VIP, Nuevo, Fraude)
- Hard Rules vs AI Decisions
- Policy Store inicial

**Día 2 — Motor de Orquestación**

- Cognitive Scorer
- Guardrails
- Fallback
- Decision Orchestrator
- Status Engine

**Día 3 — Interfaz de Claridad**

- User View
- Analyst View
- Explicabilidad

---

## ⚠ 8. Tareas Críticas Antes de Programar

- Definir decisiones humanas obligatorias
- Mapear fail states
- Preparar dataset mock
- Establecer telemetría mínima
- Crear prompts iniciales
- Definir thresholds en Policy Store

## 🗺 9. Diagrama de Arquitectura (ASCII)

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
     