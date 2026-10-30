import os
import time
from typing import Callable, List, Optional
from contracts.schemas import (
    ImpactReport,
    RepairAttempt,
    FinalReport,
    AgentEvent,
    TestRun
)
from emend.core.nebius_client import NebiusClient
from emend.core.runner.subprocess_runner import SubprocessRunner
from emend.core.agent.patching import (
    extract_patch_blocks,
    apply_patch_blocks,
    get_git_diff,
    reset_working_tree
)
from emend.core.agent.prompts.repair_prompts import SYSTEM_PROMPT, build_repair_prompt

Emit = Callable[[AgentEvent], None]

class ProofLoopAgent:
    def __init__(self, repo_path: str, emit: Emit):
        self.repo_path = repo_path
        self.emit = emit
        self.client = NebiusClient()
        self.runner = SubprocessRunner()
        self.model_repair = os.getenv("MODEL_REPAIR", "nvidia/nemotron-3-super-120b-a12b")

    def _read_source_files(self, file_paths: List[str]) -> dict:
        files = {}
        for rel_path in file_paths:
            full_path = os.path.join(self.repo_path, rel_path)
            if os.path.isfile(full_path):
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        files[rel_path] = f.read()
                except Exception:
                    pass
        return files

    def run_repair(
        self,
        failing_test: str,
        baseline_run: TestRun,
        impact: ImpactReport,
        max_attempts: int = 3
    ) -> FinalReport:
        start_time = time.time()
        attempts: List[RepairAttempt] = []
        feedback = ""
        successful_patch = ""

        # Identify baseline passing tests for regression diffing
        baseline_passing = {t.id for t in baseline_run.tests if t.outcome == "passed"}
        
        # Determine source files to feed into the prompt
        source_rel_files = list({node.file for node in impact.nodes if "test" not in node.file.lower()})
        source_files = self._read_source_files(source_rel_files)

        impact_summary = (
            f"Impacted symbols: {', '.join(impact.changed_symbols)}\n"
            f"Ranked dependent tests: {', '.join([t.id for t in impact.ranked_tests])}"
        )

        for attempt_no in range(1, max_attempts + 1):
            self.emit(AgentEvent(
                ts=time.time(),
                type="stage",
                title=f"Repair Attempt {attempt_no} Started",
                payload={"attempt": attempt_no, "model": self.model_repair}
            ))

            # 1. Generate patch with Nemotron
            prompt = build_repair_prompt(
                failing_test=failing_test,
                failure_output=baseline_run.output_tail,
                impact_summary=impact_summary,
                source_files=source_files,
                history_feedback=feedback
            )

            # In offline mock mode, produce deterministic behavior for the billing_ripple demo
            if not self.client.client and "round_price" in str(impact.changed_symbols):
                if attempt_no == 1:
                    raw_reply = (
                        "FILE: billing/utils.py\n"
                        "<<<<<<< SEARCH\n"
                        "    return round(x, 2)\n"
                        "=======\n"
                        "    return int(x * 100 + 0.5) / 100.0\n"
                        ">>>>>>> REPLACE"
                    )
                else:
                    raw_reply = (
                        "FILE: billing/utils.py\n"
                        "<<<<<<< SEARCH\n"
                        "    return round(x, 2)\n"
                        "=======\n"
                        "    from decimal import Decimal, ROUND_HALF_UP\n"
                        "    return float(Decimal(str(x)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP))\n"
                        ">>>>>>> REPLACE"
                    )
            else:
                raw_reply = self.client.chat_completion(
                    model=self.model_repair,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ]
                )

            blocks = extract_patch_blocks(raw_reply)
            reset_working_tree(self.repo_path)
            applied, apply_err = apply_patch_blocks(self.repo_path, blocks)
            diff = get_git_diff(self.repo_path) if applied else ""

            current_attempt = RepairAttempt(
                n=attempt_no,
                model=self.model_repair,
                rationale="Nemotron patch evaluation",
                patch_blocks=blocks,
                diff=diff,
                status="applied" if applied else "invalid_patch",
                tokens_in=120,
                tokens_out=60
            )

            if not applied:
                self.emit(AgentEvent(
                    ts=time.time(),
                    type="tool_call",
                    title=f"Attempt {attempt_no} Rejected by Guardrails",
                    payload={"error": apply_err}
                ))
                feedback = f"Patch rejected by guardrails: {apply_err}"
                attempts.append(current_attempt)
                continue

            # 2. Tier 1 Verification: Target Failing Test
            self.emit(AgentEvent(
                ts=time.time(),
                type="stage",
                title=f"Attempt {attempt_no}: Running Tier 1 (Target Test)",
                payload={"target": failing_test}
            ))
            t1_run = self.runner.run(self.repo_path, scope="target", test_ids=[failing_test])
            current_attempt.target_run = t1_run

            t1_failed = any(t.outcome in ("failed", "error") for t in t1_run.tests)
            if t1_failed:
                feedback = f"Tier 1 target test still failed:\n{t1_run.output_tail[-1500:]}"
                current_attempt.status = "reverted"
                reset_working_tree(self.repo_path)
                attempts.append(current_attempt)
                continue

            # 3. Tier 2 Verification: Impact-Ranked Tests
            impact_ids = [t.id for t in impact.ranked_tests if t.id != failing_test]
            regressions = []
            if impact_ids:
                self.emit(AgentEvent(
                    ts=time.time(),
                    type="stage",
                    title=f"Attempt {attempt_no}: Running Tier 2 (Impact-Ranked Tests)",
                    payload={"impact_count": len(impact_ids)}
                ))
                t2_run = self.runner.run(self.repo_path, scope="impacted", test_ids=impact_ids)
                current_attempt.impacted_run = t2_run

                for t in t2_run.tests:
                    if t.outcome in ("failed", "error") and t.id in baseline_passing:
                        regressions.append(t.id)

            if regressions:
                self.emit(AgentEvent(
                    ts=time.time(),
                    type="test_result",
                    title=f"Attempt {attempt_no}: Regression Detected in Blast Radius!",
                    payload={"regressions": regressions}
                ))
                feedback = (
                    f"Regression caught by Blast Radius Engine! The following dependent tests passed previously but broke with your patch:\n"
                    f"{', '.join(regressions)}\n"
                    f"Ensure edge-cases and dependent modules are supported."
                )
                current_attempt.status = "reverted"
                current_attempt.regressions = regressions
                reset_working_tree(self.repo_path)
                attempts.append(current_attempt)
                continue

            # 4. Tier 3 Verification: Full Test Suite Baseline Diff
            self.emit(AgentEvent(
                ts=time.time(),
                type="stage",
                title=f"Attempt {attempt_no}: Running Tier 3 (Full Test Suite)",
                payload={}
            ))
            t3_run = self.runner.run(self.repo_path, scope="full")
            current_attempt.full_run = t3_run

            for t in t3_run.tests:
                if t.outcome in ("failed", "error") and t.id in baseline_passing:
                    regressions.append(t.id)

            if regressions:
                feedback = f"Full suite regressions: {', '.join(regressions)}"
                current_attempt.status = "reverted"
                current_attempt.regressions = regressions
                reset_working_tree(self.repo_path)
                attempts.append(current_attempt)
                continue

            # If all tiers pass without regression, fix is verified
            current_attempt.status = "accepted"
            attempts.append(current_attempt)
            successful_patch = diff
            break

        # Generate Final Verdict
        verdict = "VERIFIED_FIXED" if successful_patch else "UNFIXED"
        if not successful_patch and any(a.regressions for a in attempts):
            verdict = "FIXED_WITH_REGRESSIONS"

        return FinalReport(
            verdict=verdict,  # type: ignore
            patch=successful_patch,
            attempts=attempts,
            baseline_summary={"passed": len(baseline_passing)},
            residual_risk=[n.id for n in impact.nodes if n.risk == "high"],
            metrics={
                "time_s": round(time.time() - start_time, 2),
                "tokens_total": self.client.get_token_usage()["tokens_total"],
                "attempts": len(attempts)
            }
        )