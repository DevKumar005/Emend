import asyncio
import json
from typing import Dict, List
from contracts.schemas import AgentEvent

class EventBroadcaster:
    """Manages active SSE subscriber queues per job ID."""

    def __init__(self):
        self._listeners: Dict[str, List[asyncio.Queue]] = {}

    def subscribe(self, job_id: str) -> asyncio.Queue:
        q: asyncio.Queue = asyncio.Queue()
        if job_id not in self._listeners:
            self._listeners[job_id] = []
        self._listeners[job_id].append(q)
        return q

    def unsubscribe(self, job_id: str, q: asyncio.Queue):
        if job_id in self._listeners and q in self._listeners[job_id]:
            self._listeners[job_id].remove(q)
            if not self._listeners[job_id]:
                del self._listeners[job_id]

    async def broadcast(self, job_id: str, event: AgentEvent):
        if job_id in self._listeners:
            for q in list(self._listeners[job_id]):
                try:
                    await q.put(event)
                except Exception:
                    pass

broadcaster = EventBroadcaster()
