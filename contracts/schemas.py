"""
Shared data contracts for Emend (Pydantic v2).
Frozen during M0/M1 to ensure zero schema drift between Core (A) and API/Frontend (B).
"""
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field

# ----------------- Intake & Job Schemas -----------------
class AnalysisRequest(BaseModel):
    repo_source: str = Field(..., description="Demo repo ID (e.g. shopcalc) or git URL")
    branch: Optional[str] = "main"
    failing_test: str = Field(..., description="Target failing test ID, e.g., tests/test_calc.py::test_discount")
    mode: Literal["hosted", "local"] = "hosted"

class Job(BaseModel):
    id: str
    status: Literal["queued", "baseline", "impact", "repair", "verify", "done", "error"]
    created_at: str
    updated_at: str
    attempts_used: int = 0
    error_message: Optional[str] = None

# ----------------- Runner Schemas -----------------
class TestCaseResult(BaseModel):
    id: str
    outcome: Literal["passed", "failed", "skipped", "error"]
    duration: float
    message: Optional[str] = None

class TestRun(BaseModel):
    scope: Literal["target", "impacted", "full"]
    command: str
    exit_code: int
    duration_s: float
    tests: List[TestCaseResult] = Field(default_factory=list)
    output_tail: str = ""

# ----------------- Blast Radius Schemas -----------------
class NodeInfo(BaseModel):
    id: str
    kind: Literal["module", "function", "class"]
    file: str
    lines: List[int]
    risk: Literal["low", "medium", "high"]
    label: Literal["verified pass", "verified fail", "predicted risk, unverified", "not affected (predicted)"]

class EdgeInfo(BaseModel):
    source: str
    target: str
    kind: Literal["imports", "calls"]

class RankedTest(BaseModel):
    id: str
    score: float
    reason: str
    label: Literal["static-predicted", "coverage-backed"]

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
    search: str
    replace: str

class RepairAttempt(BaseModel):
    n: int
    model: str
    rationale: str
    patch_blocks: List[PatchBlock] = Field(default_factory=list)
    diff: str = ""
    status: Literal["applied", "invalid_patch", "reverted", "accepted"]
    target_run: Optional[TestRun] = None
    impacted_run: Optional[TestRun] = None
    full_run: Optional[TestRun] = None
    regressions: List[str] = Field(default_factory=list)
    tokens_in: int = 0
    tokens_out: int = 0

class AgentEvent(BaseModel):
    ts: float
    type: Literal["stage", "tool_call", "model_message", "test_result", "verdict"]
    title: str
    payload: Dict[str, Any] = Field(default_factory=dict)

# ----------------- Final Report Schema -----------------
class FinalReport(BaseModel):
    verdict: Literal["VERIFIED_FIXED", "FIXED_WITH_REGRESSIONS", "UNFIXED", "INVALID_PATCH"]
    patch: str = Field(..., description="Final unified diff patch")
    attempts: List[RepairAttempt] = Field(default_factory=list)
    baseline_summary: Dict[str, int] = Field(default_factory=dict)
    residual_risk: List[str] = Field(default_factory=list)
    metrics: Dict[str, Any] = Field(
        default_factory=lambda: {"time_s": 0.0, "tokens_total": 0, "attempts": 0}
    )