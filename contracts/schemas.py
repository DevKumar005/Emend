"""
Shared data contracts for Emend (Pydantic v2).
Ensures zero schema drift between Core, API/Orchestrator, and Frontend.
"""
from __future__ import annotations
import time
from typing import List, Optional, Literal, Dict, Any, Union
from pydantic import BaseModel, Field

# ----------------- Intake & Job Schemas -----------------
class AnalysisRequest(BaseModel):
    repo_source: str = Field(..., description="Demo repo ID (e.g. shopcalc, billing_ripple) or git URL")
    branch: Optional[str] = Field("main", description="Target git branch")
    failing_test: str = Field(..., description="Target failing test identifier, e.g. tests/test_pricing.py::test_round_half_up_positive")
    mode: Literal["hosted", "local"] = Field("hosted", description="Execution mode: hosted or local Docker")

class Job(BaseModel):
    id: str
    status: Literal["queued", "baseline", "impact", "repair", "verify", "done", "error"] = "queued"
    created_at: str
    updated_at: str
    attempts_used: int = 0
    error_message: Optional[str] = None

# ----------------- Runner Schemas -----------------
class TestCaseResult(BaseModel):
    id: str
    outcome: Literal["passed", "failed", "skipped", "error"]
    duration: float = 0.0
    message: Optional[str] = None

# Backward compatibility alias
TestItem = TestCaseResult

class TestRun(BaseModel):
    scope: Literal["target", "impacted", "full"]
    command: str = ""
    exit_code: int = 0
    duration_s: float = 0.0
    tests: List[TestCaseResult] = Field(default_factory=list)
    output_tail: str = ""

# ----------------- Blast Radius Schemas -----------------
class NodeInfo(BaseModel):
    id: str
    kind: Literal["module", "function", "class", "test"] = "function"
    file: str = ""
    lines: List[int] = Field(default_factory=list)
    risk: Literal["low", "medium", "high", "none"] = "low"
    label: Literal["verified pass", "verified fail", "predicted risk, unverified", "not affected (predicted)"] = "predicted risk, unverified"

# Backward compatibility alias
ImpactNode = NodeInfo

class EdgeInfo(BaseModel):
    source: str
    target: str
    kind: Literal["imports", "calls", "tests"] = "calls"

# Backward compatibility alias
ImpactEdge = EdgeInfo

class RankedTest(BaseModel):
    id: str
    score: float
    reason: str
    label: Literal["static-predicted", "coverage-backed"] = "static-predicted"

# Backward compatibility alias
Rankedtest = RankedTest

class ImpactReport(BaseModel):
    changed_symbols: List[str] = Field(default_factory=list)
    nodes: List[NodeInfo] = Field(default_factory=list)
    edges: List[EdgeInfo] = Field(default_factory=list)
    ranked_tests: List[RankedTest] = Field(default_factory=list)
    caveats: List[str] = Field(default_factory=list)

# ----------------- Agent & Repair Schemas -----------------
class PatchBlock(BaseModel):
    file_path: str
    search: str = ""
    replace: str = ""

    def __init__(
        self,
        file_path: str = "",
        search: str = "",
        replace: str = "",
        search_content: str = "",
        replace_content: str = "",
        **data
    ):
        s = search or search_content
        r = replace or replace_content
        super().__init__(file_path=file_path.strip().replace("\\", "/"), search=s, replace=r, **data)

    @property
    def search_content(self) -> str:
        return self.search

    @property
    def replace_content(self) -> str:
        return self.replace

class RepairAttempt(BaseModel):
    n: int
    model: str
    rationale: str = ""
    patch_blocks: List[Any] = Field(default_factory=list)
    diff: str = ""
    status: Literal["applied", "invalid_patch", "reverted", "accepted", "rejected", "verified", "regression", "failed"] = "applied"
    target_run: Optional[TestRun] = None
    impacted_run: Optional[TestRun] = None
    full_run: Optional[TestRun] = None
    regressions: List[str] = Field(default_factory=list)
    tokens_in: int = 0
    tokens_out: int = 0

class AgentEvent(BaseModel):
    ts: Union[float, str] = Field(default_factory=time.time)
    type: Literal["stage", "tool_call", "model_message", "test_result", "verdict", "error"]
    title: str
    payload: Dict[str, Any] = Field(default_factory=dict)

class ResidualRisk(BaseModel):
    symbol: str
    file: str
    reason: str
    callers_count: int = 0

# ----------------- Final Report Schema -----------------
class FinalReport(BaseModel):
    verdict: Literal["VERIFIED_FIXED", "FIXED_WITH_REGRESSIONS", "UNFIXED", "INVALID_PATCH"]
    patch: str = Field("", description="Final unified diff patch")
    attempts: List[RepairAttempt] = Field(default_factory=list)
    baseline_summary: Dict[str, Any] = Field(default_factory=dict)
    residual_risk: List[Any] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(
        default_factory=lambda: {"time_s": 0.0, "tokens_total": 0, "attempts": 0}
    )

class DemoRepoInfo(BaseModel):
    id: str
    name: str
    description: str
    purpose: str
    failing_test: str
    expected_verdict: str
