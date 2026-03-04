from fastapi import APIRouter
from pydantic import BaseModel
from app.services.continuity_engine import continuity_engine

router = APIRouter(prefix="/continuity", tags=["Continuity & Failure Modes"])

class ContinuityEventModel(BaseModel):
    timestamp: str
    event_type: str
    source: str
    description: str
    metadata: dict

class ContinuityStatus(BaseModel):
    system_health: str
    recent_events: list[ContinuityEventModel]

@router.get("/status", response_model=ContinuityStatus)
def get_continuity_status():
    events = continuity_engine.list_events()
    return ContinuityStatus(
        system_health=continuity_engine.get_system_health(),
        recent_events=[
            ContinuityEventModel(
                timestamp=e.timestamp,
                event_type=e.event_type,
                source=e.source,
                description=e.description,
                metadata=e.metadata
            )
            for e in events
        ]
    )
