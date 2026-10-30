"""
tavily.py - Optional third-party research tool for library-change failures.
Feature-flagged: only active if TAVILY_API_KEY is configured in the environment.
"""
import os
import urllib.request
import json
from typing import Optional

def query_library_migration(query: str, max_results: int = 2) -> Optional[str]:
    """Searches developer documentation and migration notes using Tavily API."""
    api_key = os.getenv("TAVILY_API_KEY", "").strip()
    if not api_key:
        return None

    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": query,
        "search_depth": "basic",
        "include_answer": True,
        "max_results": max_results
    }

    try:
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                data = json.loads(response.read().decode("utf-8"))
                if data.get("answer"):
                    return f"Tavily Migration Note: {data['answer']}"
                results = data.get("results", [])
                if results:
                    snippets = [f"- {r.get('title')}: {r.get('content')}" for r in results[:2]]
                    return "Tavily Migration Documentation:\n" + "\n".join(snippets)
    except Exception:
        return None

    return None

class TavilyResearcher:
    """Class wrapper for backward compatibility."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("TAVILY_API_KEY", "").strip()

    def search(self, query: str) -> Optional[str]:
        return query_library_migration(query)
