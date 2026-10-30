import json
import asyncio
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from contracts.schemas import Job
from ..store import DatabaseStore
from ..events import broadcaster

router = APIRouter(prefix="/api/jobs", tags=["jobs"])
store = DatabaseStore()

@router.get("/{id}", response_model=Job)
async def get_job_status(id: str):
    job = store.get_job(id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    return job

@router.get("/{id}/events")
async def stream_job_events(id: str, request: Request):
    """Server-Sent Events (SSE) stream for real-time AgentTimeline driving."""
    # First, get existing historical events
    past_events = store.get_events(id)
    queue = broadcaster.subscribe(id)

    async def event_generator():
        try:
            # 1. Send all past events first
            for evt in past_events:
                data = json.dumps(evt.model_dump())
                yield f"data: {data}\n\n"

            # 2. Stream new live events
            while True:
                if await request.is_disconnected():
                    break
                try:
                    # Timeout periodically to send keepalive
                    evt = await asyncio.wait_for(queue.get(), timeout=15.0)
                    data = json.dumps(evt.model_dump())
                    yield f"data: {data}\n\n"
                except asyncio.TimeoutError:
                    # Send SSE comment keepalive
                    yield ": keepalive\n\n"
        finally:
            broadcaster.unsubscribe(id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
