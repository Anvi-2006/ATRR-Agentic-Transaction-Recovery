from fastapi import FastAPI

from backend.app.api.recovery import router as recovery_router


app = FastAPI(
    title="ATRR",
    description="Agentic Transaction Recovery & Replanning",
    version="0.1.0"
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ATRR",
        "message": "ATRR backend is running"
    }


app.include_router(recovery_router)