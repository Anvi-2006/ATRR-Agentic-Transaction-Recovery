from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.recovery import router as recovery_router


app = FastAPI(
    title="ATRR",
    description="Agentic Transaction Recovery & Replanning",
    version="0.1.0"
)


# Allow the React frontend to communicate with the FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "ATRR",
        "message": "ATRR backend is running"
    }


app.include_router(recovery_router)
