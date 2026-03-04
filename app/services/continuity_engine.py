from datetime import datetime
from typing import Optional, Dict, Any

class ContinuityEvent:
    def __init__(
        self,
        event_type: str,
        source: str,
        description: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.timestamp = datetime.utcnow().isoformat() + "Z"
        self.event_type = event_type  # "fallback", "error", "latency", "warning"
        self.source = source          # "llm", "guardrails", "bank", "orchestrator"
        self.description = description
        self.metadata = metadata or {}

class ContinuityEngine:
    def __init__(self):
        self.events: list[ContinuityEvent] = []

    def record(self, event: ContinuityEvent):
        self.events.append(event)

    def list_events(self):
        return self.events[-20:]  # últimos 20 eventos

    def get_system_health(self):
        if any(e.event_type == "error" for e in self.events[-10:]):
            return "failed"
        if any(e.event_type == "fallback" for e in self.events[-10:]):
            return "degraded"
        return "healthy"

continuity_engine = ContinuityEngine()
