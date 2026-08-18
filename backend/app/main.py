from fastapi import FastAPI

from app.api.test_ai import router as test_ai_router


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


app.include_router(test_ai_router)