from fastapi import APIRouter, HTTPException

from app.rag.retriever import retrieve_documents
from app.rag.sources import SEC_DOCUMENTS
from scripts.ingest import ingest_local_pdfs

router = APIRouter()


@router.get("")
def list_documents() -> dict:
    return {"documents": SEC_DOCUMENTS}


@router.post("/ingest")
def ingest() -> dict[str, int]:
    try:
        count = ingest_local_pdfs()
        return {"chunks_indexed": count}
    except SystemExit as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/search")
def search(query: str, top_k: int = 4) -> dict:
    return {"results": retrieve_documents(query, top_k=top_k)}
