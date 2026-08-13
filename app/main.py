import logging

from fastapi import FastAPI

from app.api import chat, documents, receipt, speech
from app.config import get_settings

logging.basicConfig(level=logging.INFO)

settings = get_settings()
app = FastAPI(title=settings.app_name)

app.include_router(chat.router, prefix="/api", tags=["chat"])
app.include_router(speech.router, prefix="/api", tags=["speech"])
app.include_router(receipt.router, prefix="/api/receipt", tags=["receipt"])
app.include_router(documents.router, prefix="/api/documents", tags=["documents"])


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "app": settings.app_name}
