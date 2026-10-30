import os
from typing import Dict, Any, List, Optional
from contracts.schemas import ImpactReport, TestRun
from .patching import PatchApplier
from ..impact.graph import DependencyGraphBuilder
from ..runner.base import BaseRunner
from ..research.tavily import TavilyResearcher

class AgentToolDispatcher:
    """Dispatches tool calls from the Proof Loop agent."""

    def __init__(
        self,
        repo_path: str,
        graph_builder: DependencyGraphBuilder,
        impact_report: ImpactReport,
        runner: BaseRunner
    ):
        self.repo_path = repo_path
        self.graph_builder = graph_builder
        self.impact_report = impact_report
        self.runner = runner
        self.researcher = TavilyResearcher()

    def read_file(self, path: str, line_start: Optional[int] = None, line_end: Optional[int] = None) -> str:
        """Reads file content from repository (size-capped)."""
        full_path = os.path.normpath(os.path.join(self.repo_path, path))
        if not os.path.exists(full_path):
            return f"Error: File '{path}' does not exist."
        try:
            with open(full_path, "r", encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            if line_start is not None and line_end is not None:
                selected = lines[max(0, line_start - 1):line_end]
                return "".join(selected)
            return "".join(lines[:300]) # Cap at 300 lines
        except Exception as e:
            return f"Error reading file: {e}"

    def get_callers(self, symbol_name: str) -> Dict[str, Any]:
        """Returns direct callers and callees from the dependency graph."""
        callers = self.graph_builder.get_direct_callers(symbol_name)
        callees = self.graph_builder.get_direct_callees(symbol_name)
        return {
            "symbol": symbol_name,
            "callers": callers,
            "callees": callees,
            "total_callers": len(callers)
        }

    def get_impacted_tests(self) -> List[Dict[str, Any]]:
        """Returns the ranked test list with computed scores and reasons."""
        return [
            {"id": t.id, "score": t.score, "reason": t.reason, "label": t.label}
            for t in self.impact_report.ranked_tests
        ]

    def propose_patch(self, raw_patch_text: str) -> Dict[str, Any]:
        """Attempts to apply SEARCH/REPLACE blocks with strict guardrails."""
        blocks = PatchApplier.parse_blocks(raw_patch_text)
        success, message, diff = PatchApplier.apply_blocks(self.runner.workdir, blocks)
        return {
            "success": success,
            "message": message,
            "diff": diff
        }

    def run_tests(self, scope: str = "target", test_ids: Optional[List[str]] = None) -> TestRun:
        """Executes tests in the isolated runner."""
        return self.runner.run(scope=scope, test_ids=test_ids)

    def research(self, query: str) -> str:
        """Queries documentation/migration notes via Tavily (if configured)."""
        res = self.researcher.search(query)
        return res or "No external documentation notes found."
