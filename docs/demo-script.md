# FinSight Voice Demo Script

Use this as a 5-10 minute interview walkthrough.

## Setup

1. Start backend: `uvicorn app.main:app --reload`
2. Start UI: `streamlit run frontend/streamlit_app.py`
3. Confirm `/health` returns `{"status": "ok"}`.

## Demo 1: Factual RAG

Ask:

```text
What was Apple's revenue in 2024?
```

Show:

```text
Agent -> search_financial_documents
Retriever -> relevant chunks
LLM -> grounded answer
Sources -> Apple 2024 10-K citation
```

Explain that the answer is grounded in retrieved SEC filing chunks.

## Demo 2: RAG + Calculator

Ask:

```text
What was Apple's revenue growth between 2023 and 2024?
```

Show:

```text
Agent -> RAG
Agent trace notes calculation intent
Calculator -> deterministic arithmetic for extracted numbers
Answer -> cited explanation
```

Explain that arithmetic should be deterministic instead of left entirely to an LLM.

## Demo 3: Microphone Voice

Click the microphone in Streamlit and say:

```text
What is free cash flow?
```

Show:

```text
Browser microphone -> Whisper -> editable transcription
User clicks Send to Search
Agent -> explain_finance_concept
Text answer appears first
User clicks Speak Answer -> playable WAV answer
```

Explain that Whisper converts speech to text and TTS converts the response back to audio.

## Demo 3b: Voice RAG With Confirmation

Click the microphone and say:

```text
Compare Apple's revenue in 2023 and 2024.
```

Show:

```text
Microphone -> STT -> transcription appears
Edit or confirm text -> Send to Search
Agent -> financial_search
Retriever -> Apple 10-K chunks
LLM -> text answer with sources
Speak Answer -> TTS reads the displayed answer
```

## Demo 4: Receipt

Upload a receipt image.

Show:

```text
YOLO/localization attempt -> OpenCV preprocessing -> OCR -> structured expense
```

Explain that YOLO localizes the receipt/document area, OpenCV improves image quality, and OCR extracts text.
