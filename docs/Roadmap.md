# 🗺 Roadmap — AI‑Native Money Movement Orchestrator (MVP)

Este roadmap está diseñado para construir un MVP funcional en 3 días, siguiendo una arquitectura AI‑native modular y altamente trazable.

---

## 🚀 Día 1 — Fundaciones y “Fuente de la Verdad”

### 🎯 Objetivo del día
Establecer la base técnica y documental para que el sistema pueda generar código de forma consistente.

### 🔧 Entregables
- `/docs` completo (PRD, TechnicalSpec, Architecture, APIContracts, ValueProp)
- `/prompts` completo (todos los prompts por módulo)
- Estructura del repo creada en `/app`
- Policy Store inicial (thresholds mock)
- Dataset mock:
  - usuario frecuente
  - usuario nuevo
  - caso sospechoso
- Logging Utility (primer módulo a generar)
- Normalizador de contexto (Context Normalizer)

### 🔗 Dependencias
Ninguna (día de setup).

---

## ⚙️ Día 2 — Motores de Decisión (Core del MVP)

### 🎯 Objetivo del día
Construir el “cerebro híbrido”: reglas duras + IA + fallback + orquestación.

### 🔧 Entregables
- Hard Rules Engine
- Cognitive Risk Engine (LLM)
- LLM Guardrail Layer
- Fallback Engine
- Decision Orchestrator
- Status Engine
- Mock Banking Layer

### 🔗 Dependencias
- Policy Store
- Logging Utility
- Context Normalizer

---

## 🧠 Día 3 — Transparencia, UI y HITL

### 🎯 Objetivo del día
Construir la capa de claridad y demostración del sistema.

### 🔧 Entregables
- Transparency Layer (explicabilidad)
- User View (Streamlit)
- Analyst View (HITL)
- Integración completa de punta a punta
- Auditoría y trazabilidad mínima

### 🔗 Dependencias
- Todos los módulos del Día 2

---

## 🧪 Escenarios de prueba del MVP

### 1. Happy Path
- $20 → contacto frecuente  
- Hard Rules: pass  
- Cognitive Score: <10  
- Decision: Green  
- Status: Approved  
- Explicación: inmediata  

### 2. Friction Point
- $1,000 → cuenta nueva  
- Hard Rules: pass  
- Cognitive Score: 40  
- Decision: Yellow  
- Status: Held  
- Explicación: “primera vez enviando a esta cuenta”  
- HITL: approve  

### 3. Security Guard
- Retiro grande + cambio reciente de contraseña  
- Hard Rules: pass  
- Cognitive Score: >80  
- Decision: Red  
- Status: Blocked  
- HITL: escalate  

---

## 📌 Prioridades (RICE)

| Componente | RICE | Prioridad |
|-----------|------|-----------|
| Status Engine | 360 | Alta |
| Guardrails | 288 | Alta |
| Fallback Engine | 288 | Alta |
| Hard Rules Engine | 240 | Alta |
| Decision Orchestrator | 240 | Alta |
| Cognitive Scorer | 180 | Media |

---

## 🧩 Dependencias entre módulos

- Hard Rules → Cognitive Scorer → Guardrails → Fallback → Orchestrator → Status → Transparency
- Policy Store alimenta Hard Rules y Orchestrator
- Logging Utility es transversal
- Mock Banking Layer depende del Orchestrator
- UI depende de Transparency + Status

---

## 🏁 Resultado esperado del MVP

Un sistema que:

- recibe una transacción  
- normaliza contexto  
- aplica reglas duras  
- evalúa riesgo con IA  
- valida con guardrails  
- decide (green/yellow/red)  
- actualiza estado  
- explica en lenguaje humano  
- permite intervención humana  
- registra todo en audit trail  

