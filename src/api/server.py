from __future__ import annotations

import json
import os
from queue import Queue
from threading import Thread

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from .chat_service import ChatService
from .schemas import (
    ChatRequest,
    ChatResponse,
    ConfigResponse,
    ConfigUpdateRequest,
    SessionResponse,
)

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
service = ChatService(project_root=project_root)

app = FastAPI(title="DocAdvisor API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}


@app.post("/api/v1/sessions", response_model=SessionResponse)
def create_session():
    return {"session_id": service.new_session()}


@app.get("/api/v1/sessions/{session_id}")
def get_session(session_id: str):
    sid, runtime = service.get_session(session_id)
    return {
        "session_id": sid,
        "round": runtime.state.current_round,
        "conversation_turns": runtime.state.conversation_turns,
        "last_trace": [t.model_dump() for t in runtime.last_trace],
        "last_sources": [s.model_dump() for s in runtime.last_sources],
    }


@app.get("/api/v1/config", response_model=ConfigResponse)
def get_config():
    return {
        "provider": service.processor.provider,
        "model": service.processor.model,
        "has_api_key": bool(service.processor.api_key),
    }


@app.put("/api/v1/config", response_model=ConfigResponse)
def update_config(payload: ConfigUpdateRequest):
    api_key = payload.api_key or service.processor.api_key
    provider = payload.provider or service.processor.provider
    model = payload.model or service.processor.model
    service.processor.update_api_config(api_key=api_key, model=model, provider=provider)
    return {"provider": provider, "model": model, "has_api_key": bool(api_key)}


@app.get("/api/v1/retrieval/latest")
def latest_retrieval(session_id: str):
    _, runtime = service.get_session(session_id)
    return {"sources": [s.model_dump() for s in runtime.last_sources]}


@app.post("/api/v1/chat", response_model=ChatResponse)
def chat(payload: ChatRequest):
    result = service.run_chat(payload.query, payload.session_id)
    return result


@app.post("/api/v1/chat/stream")
def chat_stream(payload: ChatRequest):
    q: Queue[str | None] = Queue()

    def emit(event: str, data: dict):
        q.put(f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n")

    def worker():
        try:
            result = service.run_chat(payload.query, payload.session_id, trace_cb=emit)
            q.put(f"event: done\ndata: {json.dumps(result, ensure_ascii=False)}\n\n")
        except Exception as e:
            q.put(f"event: error\ndata: {json.dumps({'message': str(e)}, ensure_ascii=False)}\n\n")
        finally:
            q.put(None)

    Thread(target=worker, daemon=True).start()

    def stream_gen():
        while True:
            item = q.get()
            if item is None:
                break
            yield item

    return StreamingResponse(stream_gen(), media_type="text/event-stream")
