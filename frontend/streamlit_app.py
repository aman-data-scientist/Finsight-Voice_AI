import hashlib

import requests
import streamlit as st

st.set_page_config(page_title="FinSight Voice", layout="wide")

API_BASE = st.sidebar.text_input("Backend API", "http://localhost:8000")
st.sidebar.caption("Run FastAPI first: uvicorn app.main:app --reload")


def _init_state() -> None:
    defaults = {
        "transcript": "",
        "search_query": "",
        "pending_search_query": None,
        "last_audio_hash": "",
        "answer_data": None,
        "status": "Ready",
        "tts_audio": None,
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def _apply_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        .stApp {
            background:
                radial-gradient(circle at 18% 8%, rgba(126, 87, 194, 0.20), transparent 32%),
                radial-gradient(circle at 86% 88%, rgba(56, 189, 248, 0.11), transparent 32%),
                #07070a;
            color: #f4f4f7;
        }

        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #17151f 0%, #0f0e15 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        .block-container {
            max-width: 1380px;
            padding-top: 2rem;
            padding-bottom: 2rem;
        }

        .hero {
            background: linear-gradient(135deg, #050507 0%, #111018 55%, #171123 100%);
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: 22px;
            padding: 2rem;
            box-shadow: 0 22px 80px rgba(0, 0, 0, 0.42);
            margin-bottom: 1rem;
        }

        .hero h1 {
            font-size: 3rem;
            line-height: 1.05;
            margin: 0 0 0.65rem 0;
            letter-spacing: 0;
        }

        .hero p {
            color: #a8a7b3;
            font-size: 1.05rem;
            margin: 0;
        }

        .status-row {
            display: flex;
            gap: 0.75rem;
            flex-wrap: wrap;
            margin-top: 1.25rem;
        }

        .pill {
            border: 1px solid rgba(255, 255, 255, 0.11);
            background: rgba(255, 255, 255, 0.045);
            color: #dfdeea;
            border-radius: 999px;
            padding: 0.55rem 0.85rem;
            font-size: 0.88rem;
        }

        .panel {
            background: rgba(18, 17, 25, 0.92);
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: 18px;
            padding: 1.25rem;
            min-height: 100%;
            box-shadow: 0 18px 55px rgba(0, 0, 0, 0.28);
        }

        .panel-accent {
            border-color: rgba(139, 92, 246, 0.58);
            background:
                linear-gradient(135deg, rgba(139, 92, 246, 0.18), rgba(18, 17, 25, 0.95) 48%),
                rgba(18, 17, 25, 0.95);
        }

        .metric-title {
            color: #b9b8c5;
            font-size: 0.9rem;
            margin-bottom: 0.4rem;
        }

        .metric-value {
            color: #f7f7fb;
            font-size: 2rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
        }

        .metric-note {
            color: #28c78d;
            font-size: 0.88rem;
        }

        .section-title {
            color: #f4f4f7;
            font-size: 1.25rem;
            font-weight: 750;
            margin: 0 0 0.7rem 0;
        }

        .muted {
            color: #a8a7b3;
            font-size: 0.96rem;
            line-height: 1.55;
        }

        .answer-box {
            background: rgba(12, 12, 18, 0.96);
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: 18px;
            padding: 1.35rem;
            margin-top: 1rem;
        }

        .source-line {
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
            padding: 0.75rem 0.9rem;
            margin-bottom: 0.55rem;
            background: rgba(255, 255, 255, 0.035);
            color: #d8d6e5;
            font-size: 0.92rem;
        }

        div.stButton > button {
            border-radius: 999px;
            min-height: 2.8rem;
            font-weight: 700;
            border: 1px solid rgba(255, 255, 255, 0.12);
        }

        div.stButton > button[kind="primary"] {
            background: linear-gradient(135deg, #8b5cf6, #5b8cff);
            border: 0;
        }

        [data-testid="stTextInput"] input,
        [data-testid="stTextArea"] textarea {
            background: #15141d;
            border: 1px solid rgba(255, 255, 255, 0.10);
            border-radius: 14px;
            color: #f5f5f7;
        }

        [data-testid="stAudioInput"] {
            background: rgba(255, 255, 255, 0.035);
            border: 1px dashed rgba(255, 255, 255, 0.16);
            border-radius: 16px;
            padding: 1rem;
        }

        hr {
            border-color: rgba(255, 255, 255, 0.08);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _transcribe_recording(audio_file) -> None:
    audio_bytes = audio_file.getvalue()
    audio_hash = hashlib.sha256(audio_bytes).hexdigest()
    if audio_hash == st.session_state.last_audio_hash:
        return

    st.session_state.last_audio_hash = audio_hash
    st.session_state.status = "Converting speech to text"
    with st.spinner("Converting speech to text..."):
        try:
            files = {"file": (audio_file.name or "microphone.wav", audio_bytes, audio_file.type or "audio/wav")}
            response = requests.post(f"{API_BASE}/api/transcribe", files=files, timeout=180)
            response.raise_for_status()
            text = response.json().get("text", "").strip()
            if not text:
                st.warning("I could not understand the speech. Please try again.")
                st.session_state.status = "Ready"
                return
            st.session_state.transcript = text
            st.session_state.pending_search_query = text
            st.session_state.status = "Transcription ready"
            st.rerun()
        except requests.RequestException as exc:
            detail = _extract_error_detail(exc)
            st.error(f"Microphone audio could not be transcribed: {detail}")
            st.session_state.status = "Ready"


def _extract_error_detail(exc: requests.RequestException) -> str:
    response = getattr(exc, "response", None)
    if response is None:
        return str(exc)
    try:
        payload = response.json()
        return str(payload.get("detail", exc))
    except ValueError:
        return response.text or str(exc)


def _search_financial_documents(query: str) -> None:
    st.session_state.status = "Searching financial documents"
    st.session_state.tts_audio = None
    with st.spinner("Searching financial documents and generating answer..."):
        try:
            response = requests.post(f"{API_BASE}/api/search", json={"query": query}, timeout=180)
            response.raise_for_status()
            st.session_state.answer_data = response.json()
            st.session_state.status = "Ready"
        except requests.RequestException as exc:
            st.error(f"I could not retrieve financial information right now. Please try again. Details: {exc}")
            st.session_state.status = "Ready"


def _speak_answer(answer: str) -> None:
    st.session_state.status = "Speaking answer"
    with st.spinner("Speaking answer..."):
        try:
            response = requests.post(f"{API_BASE}/api/tts", json={"text": answer}, timeout=180)
            response.raise_for_status()
            st.session_state.tts_audio = response.content
            st.session_state.status = "Ready"
        except requests.RequestException:
            st.error("Unable to play the answer. The text response is still available.")
            st.session_state.status = "Ready"


def _render_sources(sources: list[dict]) -> None:
    for source in sources:
        meta = source["metadata"]
        st.markdown(
            f"""
            <div class="source-line">
                <strong>{meta.get('company')} {meta.get('year')} {meta.get('filing_type')}</strong><br>
                {meta.get('section')} · page {meta.get('page')} · score {source['score']:.2f}
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_answer(data: dict) -> None:
    st.markdown('<div class="answer-box">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">FinSight Answer</div>', unsafe_allow_html=True)
    st.write(data["answer"])

    if data.get("trace"):
        with st.expander("Agent Trace"):
            for step in data["trace"]:
                st.write(f"- {step}")

    speak_col, audio_col = st.columns([1, 3])
    with speak_col:
        if st.button("Speak Answer"):
            _speak_answer(data["answer"])
    with audio_col:
        if st.session_state.tts_audio:
            st.audio(st.session_state.tts_audio, format="audio/wav")
    st.markdown("</div>", unsafe_allow_html=True)


def _render_header() -> None:
    st.markdown(
        f"""
        <div class="hero">
            <h1>Welcome to FinSight Voice</h1>
            <p>Ask financial questions by typing or speaking. Review the query, search SEC filings, read the answer, then optionally hear it aloud.</p>
            <div class="status-row">
                <div class="pill">Status: {st.session_state.status}</div>
                <div class="pill">RAG: FAISS vector search</div>
                <div class="pill">Corpus: Apple · Microsoft · Tesla · Google</div>
                <div class="pill">Voice: Whisper STT + TTS</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_metric_cards() -> None:
    card1, card2, card3 = st.columns(3)
    with card1:
        st.markdown(
            """
            <div class="panel">
                <div class="metric-title">Indexed Companies</div>
                <div class="metric-value">4</div>
                <div class="metric-note">Apple, Microsoft, Tesla, Google</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with card2:
        st.markdown(
            """
            <div class="panel">
                <div class="metric-title">Target SEC Filings</div>
                <div class="metric-value">40</div>
                <div class="metric-note">10 annual 10-K filings each</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with card3:
        st.markdown(
            """
            <div class="panel panel-accent">
                <div class="metric-title">Agent Tools</div>
                <div class="metric-value">4</div>
                <div class="metric-note">RAG, calculator, concepts, receipt OCR</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _render_query_workspace() -> None:
    if st.session_state.pending_search_query is not None:
        st.session_state.search_query = st.session_state.pending_search_query
        st.session_state.transcript = st.session_state.pending_search_query
        st.session_state.pending_search_query = None

    left, right = st.columns([1.15, 0.85], gap="large")
    with left:
        st.markdown('<div class="section-title">Financial Research Workspace</div>', unsafe_allow_html=True)
        with st.form("typed_question_form", clear_on_submit=False):
            search_query = st.text_input(
                "Search by typing or use the microphone",
                placeholder="Example: Compare Apple's revenue in 2023 and 2024.",
                key="search_query",
            )
            typed_submitted = st.form_submit_button("Ask", type="primary")
        if typed_submitted and search_query.strip():
            st.session_state.transcript = search_query.strip()
            _search_financial_documents(search_query.strip())

        if st.button("Load Demo Question"):
            demo_question = "Compare Apple's revenue in 2023 and 2024."
            st.session_state.transcript = demo_question
            st.session_state.pending_search_query = demo_question
            st.session_state.answer_data = None
            st.session_state.tts_audio = None
            st.session_state.status = "Question ready"
            st.rerun()

        if st.session_state.transcript:
            st.caption("Latest microphone transcription is now in the search bar. Edit it there before asking.")

        if st.button("Clear Workspace"):
            st.session_state.transcript = ""
            st.session_state.pending_search_query = ""
            st.session_state.answer_data = None
            st.session_state.tts_audio = None
            st.session_state.status = "Ready"
            st.rerun()

    with right:
        st.markdown('<div class="section-title">Voice Query</div>', unsafe_allow_html=True)
        st.markdown(
            """
            <div class="panel panel-accent">
                <div class="metric-title">Microphone Flow</div>
                <div class="muted">
                    Click the recorder below, speak naturally, then edit the transcription in the same search bar before asking.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if hasattr(st, "audio_input"):
            audio = st.audio_input("Click to speak")
            if audio is not None:
                _transcribe_recording(audio)
        else:
            st.error("Microphone input requires a newer Streamlit version. Run: pip install --upgrade streamlit")


def _render_receipt_panel() -> None:
    st.markdown('<div class="section-title">Receipt Analysis</div>', unsafe_allow_html=True)
    receipt = st.file_uploader("Upload receipt", type=["jpg", "jpeg", "png", "webp"])
    if receipt and st.button("Analyze Receipt"):
        try:
            files = {"file": (receipt.name, receipt.getvalue(), receipt.type)}
            response = requests.post(f"{API_BASE}/api/receipt/analyze", files=files, timeout=120)
            response.raise_for_status()
            st.json(response.json()["expense"])
        except requests.RequestException as exc:
            st.error(f"Receipt analysis failed: {exc}")


_init_state()
_apply_styles()
_render_header()
_render_metric_cards()

st.markdown("<br>", unsafe_allow_html=True)
_render_query_workspace()

if st.session_state.answer_data:
    _render_answer(st.session_state.answer_data)

st.divider()
_render_receipt_panel()
