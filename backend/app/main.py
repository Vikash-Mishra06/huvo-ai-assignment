from fastapi import FastAPI

from app.api.chat import router as chat_router
from app.api.analytics import router as analytics_router

app = FastAPI(
    title="Huvo AI Sales Agent",
    description="Conversational AI backend for the Huvo AI assignment.",
    version="1.0.0",
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