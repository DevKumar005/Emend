import os
import json
from fastapi import APIRouter
from typing import List
from contracts.schemas import DemoRepoInfo

router = APIRouter(prefix="/api/demo-repos", tags=["demo"])

DEMO_REPOS: List[DemoRepoInfo] = [
    DemoRepoInfo(
        id="billing_ripple",
        name="billing_ripple (Ripple Catch Demo)",
        description="Naive fix passes target test but silently causes regressions in downstream refunds.py. Emend catches the regression, rolls back, and verifies a symmetric Decimal repair.",
        purpose="Demonstrate Blast Radius Engine & proof verification loop with regression recovery.",
        failing_test="tests/test_pricing.py::test_round_half_up_positive",
        expected_verdict="VERIFIED_FIXED"
    ),
    DemoRepoInfo(
        id="shopcalc",
        name="shopcalc (Simple Bug)",
        description="Discount logic subtracts percent directly instead of percentage computation. One-line repairable bug.",
        purpose="Fast demonstration of single-attempt diagnosis, patch generation, and deterministic verification.",
        failing_test="tests/test_shop.py::test_apply_discount_fifty_percent",
        expected_verdict="VERIFIED_FIXED"
    ),
    DemoRepoInfo(
        id="scheduler_hard",
        name="scheduler_hard (Honest Failure)",
        description="Business logic relies on an external holiday calendar not derivable from code. Emend tries 3 times, honestly declares UNFIXED, and documents residual risks.",
        purpose="Demonstrate agent honesty: never claiming more than it can deterministically verify.",
        failing_test="tests/test_scheduler.py::test_corporate_founding_day_holiday",
        expected_verdict="UNFIXED"
    )
]

@router.get("", response_model=List[DemoRepoInfo])
async def list_demo_repos():
    return DEMO_REPOS

@router.get("/recorded-run/{demo_id}")
async def get_recorded_run(demo_id: str):
    """Safety-net pre-recorded high-fidelity run for live demo guarantees (Section 14)."""
    fixtures_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../contracts/fixtures"))
    if not os.path.exists(fixtures_dir):
        fixtures_dir = os.path.abspath("contracts/fixtures")

    if demo_id == "shopcalc":
        return {
            "demo_id": "shopcalc",
            "events": [
                {
                    "ts": 1730300100.0,
                    "type": "stage",
                    "title": "Stage 1: Intake & Validation",
                    "payload": {"repo": "demo_repos/shopcalc", "failing_test": "tests/test_shop.py::test_apply_discount_fifty_percent", "mode": "hosted"}
                },
                {
                    "ts": 1730300100.5,
                    "type": "stage",
                    "title": "Stage 2: Baseline Execution (Pytest)",
                    "payload": {"status": "reproduced_target_failure", "passed": 2, "failed": 1}
                },
                {
                    "ts": 1730300101.1,
                    "type": "stage",
                    "title": "Stage 3: Blast Radius AST & Call Graph Analysis",
                    "payload": {"nodes_count": 2, "ranked_tests": ["tests/test_shop.py::test_apply_discount_fifty_percent"]}
                },
                {
                    "ts": 1730300101.8,
                    "type": "tool_call",
                    "title": "Nemotron Super 120B Generated Search/Replace Block",
                    "payload": {"model": "nvidia/nemotron-3-super-120b-a12b", "attempt": 1}
                },
                {
                    "ts": 1730300102.4,
                    "type": "test_result",
                    "title": "Deterministic Verification: Target & Impacted Suites Passed (0 Regressions)",
                    "payload": {"passed": 3, "failed": 0, "status": "accepted"}
                },
                {
                    "ts": 1730300102.7,
                    "type": "verdict",
                    "title": "Verdict: VERIFIED_FIXED on Attempt 1",
                    "payload": {"verdict": "VERIFIED_FIXED", "attempts": 1}
                }
            ],
            "impact": {
                "changed_symbols": ["shop.utils.apply_discount"],
                "nodes": [
                    {
                        "id": "shop.utils.apply_discount",
                        "kind": "function",
                        "file": "shop/utils.py",
                        "lines": [1, 5],
                        "risk": "low",
                        "label": "verified pass"
                    },
                    {
                        "id": "shopcalc.calculator.calculate_total",
                        "kind": "function",
                        "file": "shopcalc/calculator.py",
                        "lines": [4, 9],
                        "risk": "low",
                        "label": "verified pass"
                    }
                ],
                "edges": [
                    {
                        "source": "shopcalc.calculator.calculate_total",
                        "target": "shop.utils.apply_discount",
                        "kind": "calls"
                    }
                ],
                "ranked_tests": [
                    {
                        "id": "tests/test_shop.py::test_apply_discount_fifty_percent",
                        "score": 1.0,
                        "reason": "Direct caller of apply_discount",
                        "label": "static-predicted"
                    },
                    {
                        "id": "tests/test_calculator.py::test_calculate_total_with_discount",
                        "score": 0.8,
                        "reason": "Calls calculate_total which calls apply_discount",
                        "label": "static-predicted"
                    }
                ],
                "caveats": ["Dynamic dispatch and monkeypatching are not statically resolved."]
            },
            "report": {
                "verdict": "VERIFIED_FIXED",
                "patch": "--- shop/utils.py\n+++ shop/utils.py\n@@ -2,1 +2,1 @@\n-    return price - percent\n+    return price * (1.0 - percent / 100.0)",
                "attempts": [
                    {
                        "n": 1,
                        "model": "nvidia/nemotron-3-super-120b-a12b",
                        "rationale": "Bug identified: apply_discount subtracts percent directly from price rather than calculating price * (1 - percent/100).",
                        "patch_blocks": [],
                        "diff": "--- shop/utils.py\n+++ shop/utils.py\n@@ -2,1 +2,1 @@\n- return price - percent\n+ return price * (1.0 - percent / 100.0)",
                        "status": "accepted",
                        "regressions": [],
                        "tokens_in": 320,
                        "tokens_out": 80
                    }
                ],
                "baseline_summary": {"passed": 2},
                "residual_risk": [],
                "metrics": {
                    "time_s": 0.62,
                    "tokens_total": 400,
                    "attempts": 1
                }
            },
            "test_runs": [
                {
                    "scope": "target",
                    "command": "pytest tests/test_shop.py::test_apply_discount_fifty_percent --json-report",
                    "exit_code": 0,
                    "duration_s": 0.12,
                    "tests": [
                        {"id": "tests/test_shop.py::test_apply_discount_fifty_percent", "outcome": "passed", "duration": 0.04, "message": None}
                    ],
                    "output_tail": "1 passed in 0.12s"
                },
                {
                    "scope": "impacted",
                    "command": "pytest tests/test_shop.py tests/test_calculator.py --json-report",
                    "exit_code": 0,
                    "duration_s": 0.25,
                    "tests": [
                        {"id": "tests/test_shop.py::test_apply_discount_fifty_percent", "outcome": "passed", "duration": 0.04, "message": None},
                        {"id": "tests/test_calculator.py::test_calculate_total_with_discount", "outcome": "passed", "duration": 0.05, "message": None}
                    ],
                    "output_tail": "2 passed in 0.25s"
                },
                {
                    "scope": "full",
                    "command": "pytest tests/ --json-report",
                    "exit_code": 0,
                    "duration_s": 0.38,
                    "tests": [
                        {"id": "tests/test_shop.py::test_apply_discount_fifty_percent", "outcome": "passed", "duration": 0.04, "message": None},
                        {"id": "tests/test_calculator.py::test_calculate_total_with_discount", "outcome": "passed", "duration": 0.05, "message": None},
                        {"id": "tests/test_calculator.py::test_calculate_total_without_discount", "outcome": "passed", "duration": 0.03, "message": None}
                    ],
                    "output_tail": "3 passed in 0.38s"
                }
            ]
        }

    elif demo_id == "scheduler_hard":
        return {
            "demo_id": "scheduler_hard",
            "events": [
                {
                    "ts": 1730300200.0,
                    "type": "stage",
                    "title": "Stage 1: Intake & Validation",
                    "payload": {"repo": "demo_repos/scheduler_hard", "failing_test": "tests/test_scheduler.py::test_corporate_founding_day_holiday", "mode": "hosted"}
                },
                {
                    "ts": 1730300200.6,
                    "type": "stage",
                    "title": "Stage 2: Baseline Execution (Pytest)",
                    "payload": {"status": "reproduced_target_failure", "passed": 3, "failed": 1}
                },
                {
                    "ts": 1730300201.2,
                    "type": "stage",
                    "title": "Stage 3: Blast Radius AST & Call Graph Analysis",
                    "payload": {"nodes_count": 2, "ranked_tests": ["tests/test_scheduler.py::test_corporate_founding_day_holiday"]}
                },
                {
                    "ts": 1730300201.9,
                    "type": "tool_call",
                    "title": "Attempt 1: Attempted heuristic holiday resolution",
                    "payload": {"model": "nvidia/nemotron-3-super-120b-a12b", "status": "failed"}
                },
                {
                    "ts": 1730300202.8,
                    "type": "tool_call",
                    "title": "Attempt 2: Attempted secondary calendar inference",
                    "payload": {"model": "nvidia/nemotron-3-super-120b-a12b", "status": "failed"}
                },
                {
                    "ts": 1730300203.6,
                    "type": "tool_call",
                    "title": "Attempt 3: External business rule not derivable from code; halted gracefully",
                    "payload": {"model": "nvidia/nemotron-3-super-120b-a12b", "status": "failed"}
                },
                {
                    "ts": 1730300204.0,
                    "type": "verdict",
                    "title": "Verdict: UNFIXED (Honest Failure Declaration)",
                    "payload": {"verdict": "UNFIXED", "attempts": 3, "residual_risks": 1}
                }
            ],
            "impact": {
                "changed_symbols": ["scheduler.core.is_workday"],
                "nodes": [
                    {
                        "id": "scheduler.core.is_workday",
                        "kind": "function",
                        "file": "scheduler/core.py",
                        "lines": [1, 10],
                        "risk": "high",
                        "label": "verified fail"
                    },
                    {
                        "id": "scheduler.job_scheduler.schedule_job",
                        "kind": "function",
                        "file": "scheduler/job_scheduler.py",
                        "lines": [4, 12],
                        "risk": "high",
                        "label": "predicted risk, unverified"
                    }
                ],
                "edges": [
                    {
                        "source": "scheduler.job_scheduler.schedule_job",
                        "target": "scheduler.core.is_workday",
                        "kind": "calls"
                    }
                ],
                "ranked_tests": [
                    {
                        "id": "tests/test_scheduler.py::test_corporate_founding_day_holiday",
                        "score": 1.0,
                        "reason": "Direct caller of is_workday",
                        "label": "static-predicted"
                    }
                ],
                "caveats": [
                    "Dynamic dispatch and reflection are not statically resolved.",
                    "Corporate holiday calendar data is missing and cannot be derived statically from code alone."
                ]
            },
            "report": {
                "verdict": "UNFIXED",
                "patch": "",
                "attempts": [
                    {
                        "n": 1,
                        "model": "nvidia/nemotron-3-super-120b-a12b",
                        "rationale": "Attempt 1: Attempted heuristic holiday lookup based on standard calendar libraries. Target test still failed.",
                        "patch_blocks": [],
                        "diff": "",
                        "status": "failed",
                        "regressions": [],
                        "tokens_in": 450,
                        "tokens_out": 90
                    },
                    {
                        "n": 2,
                        "model": "nvidia/nemotron-3-super-120b-a12b",
                        "rationale": "Attempt 2: Checked for environment or config variables for founding day calendar. None found in codebase.",
                        "patch_blocks": [],
                        "diff": "",
                        "status": "failed",
                        "regressions": [],
                        "tokens_in": 480,
                        "tokens_out": 105
                    },
                    {
                        "n": 3,
                        "model": "nvidia/nemotron-3-super-120b-a12b",
                        "rationale": "Attempt 3: Corporate holiday rules require external company schedule not present in source code. Refusing to hallucinate corporate policy.",
                        "patch_blocks": [],
                        "diff": "",
                        "status": "failed",
                        "regressions": [],
                        "tokens_in": 510,
                        "tokens_out": 110
                    }
                ],
                "baseline_summary": {"passed": 3},
                "residual_risk": [
                    {
                        "symbol": "scheduler.job_scheduler.schedule_job",
                        "file": "scheduler/job_scheduler.py",
                        "reason": "Downstream job scheduler relies on is_workday(), which fails on company-specific holidays. External schedule source required.",
                        "callers_count": 2
                    }
                ],
                "metrics": {
                    "time_s": 1.84,
                    "tokens_total": 1745,
                    "attempts": 3
                }
            },
            "test_runs": [
                {
                    "scope": "target",
                    "command": "pytest tests/test_scheduler.py::test_corporate_founding_day_holiday --json-report",
                    "exit_code": 1,
                    "duration_s": 0.15,
                    "tests": [
                        {"id": "tests/test_scheduler.py::test_corporate_founding_day_holiday", "outcome": "failed", "duration": 0.05, "message": "AssertionError: Expected False for founding day holiday, got True"}
                    ],
                    "output_tail": "1 failed in 0.15s"
                },
                {
                    "scope": "full",
                    "command": "pytest tests/ --json-report",
                    "exit_code": 1,
                    "duration_s": 0.42,
                    "tests": [
                        {"id": "tests/test_scheduler.py::test_regular_weekday", "outcome": "passed", "duration": 0.04, "message": None},
                        {"id": "tests/test_scheduler.py::test_weekend_saturday", "outcome": "passed", "duration": 0.03, "message": None},
                        {"id": "tests/test_scheduler.py::test_weekend_sunday", "outcome": "passed", "duration": 0.03, "message": None},
                        {"id": "tests/test_scheduler.py::test_corporate_founding_day_holiday", "outcome": "failed", "duration": 0.05, "message": "AssertionError: Expected False for founding day holiday"}
                    ],
                    "output_tail": "1 failed, 3 passed in 0.42s"
                }
            ]
        }

    # Default: billing_ripple
    try:
        with open(os.path.join(fixtures_dir, "events.json"), "r") as f:
            events = json.load(f)
        with open(os.path.join(fixtures_dir, "impact.json"), "r") as f:
            impact = json.load(f)
        with open(os.path.join(fixtures_dir, "report.json"), "r") as f:
            report = json.load(f)
        
        test_runs = []
        if os.path.exists(os.path.join(fixtures_dir, "run.json")):
            with open(os.path.join(fixtures_dir, "run.json"), "r") as f:
                test_runs.append(json.load(f))

        return {
            "demo_id": demo_id,
            "events": events,
            "impact": impact,
            "report": report,
            "test_runs": test_runs
        }
    except Exception as e:
        return {"error": f"Failed reading fixtures: {e}"}
