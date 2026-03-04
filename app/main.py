from fastapi import FastAPI

from app.routers.ingest import router as ingest_router
from app.routers.orchestrate import router as orchestrate_router
from app.routers.status import router as status_router
from app.routers.explain import router as explain_router
from app.routers.mock_bank import router as mock_bank_router
from app.routers.operational_context import router as operational_context_router

app = FastAPI(title="AI-Native Money Movement Orchestrator MVP")

app.include_router(ingest_router)
app.include_router(orchestrate_router)
app.include_router(status_router)
app.include_router(explain_router)
app.include_router(mock_bank_router)
app.include_router(operational_context_router)


@app.get("/health")
def health():
    return {"status": "ok"}
