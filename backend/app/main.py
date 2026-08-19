from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.analytics import router as analytics_router
from app.api.chat import router as chat_router


app = FastAPI(
    title="Huvo AI Sales Agent",
    description="Conversational AI backend for the Huvo AI assignment.",
    version="1.0.0",
)


# Allow the local React frontend to communicate with the FastAPI backend.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health_check():
    """Confirm that the backend service is running."""
    return {
        "status": "ok",
        "service": "huvo-ai-sales-agent",
    }


app.include_router(chat_router)
app.include_router(analytics_router)