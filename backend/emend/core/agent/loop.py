import os
import time
from typing import Callable, List, Dict, Any, Optional
from contracts.schemas import (
    ImpactReport,
    RepairAttempt,
    FinalReport,
    AgentEvent,
    TestRun,
    ResidualRisk
)
from emend.core.nebius_client import NebiusClient
from emend.core.runner.subprocess_runner import SubprocessRunner
from emend.core.runner.base import BaseRunner
from emend.core.agent.patching import (
    extract_patch_blocks,
    apply_patch_blocks,
    get_git_diff,
    reset_working_tree
)
from emend.core.agent.prompts.repair_prompts import SYSTEM_PROMPT, build_repair_prompt

Emit = Callable[[AgentEvent], None]

class ProofLoopAgent:
    """The Proof Loop repair agent.
    Performs iterative repair with up to 3 attempts, 3-tier deterministic verification cascade,
    strict guardrails, regression recovery via git revert, and event streaming.
    """

    def __init__(
        self,
        repo_path: str,
        emit: Optional[Emit] = None,
        failing_test: Optional[str] = None,
        impact: Optional[ImpactReport] = None,
        runner: Optional[BaseRunner] = None,
        max_attempts: int = 3,
        client: Optional[NebiusClient] = None,
    ):
        self.repo_path = os.path.abspath(repo_path)
        self.emit = emit or (lambda ev: None)
        self.failing_test = failing_test or ""
        self.impact = impact or ImpactReport()
        self.runner = runner or SubprocessRunner(self.repo_path)
        self.max_attempts = max_attempts
        self.client = client or NebiusClient()
        self.model_repair = os.getenv("MODEL_REPAIR", "nvidia/nemotron-3-super-120b-a12b")

    def _read_source_files(self, file_paths: List[str]) -> Dict[str, str]:
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
        self.failing_test = failing_test
        self.impact = impact
        self.max_attempts = max_attempts
        return self.run(baseline_run)

    def run(self, baseline_run: TestRun) -> FinalReport:
        start_time = time.time()
        attempts: List[RepairAttempt] = []
        feedback = ""
        successful_patch = ""

        baseline_passing = {t.id for t in baseline_run.tests if t.outcome == "passed"}
        source_rel_files = list({node.file for node in self.impact.nodes if "test" not in node.file.lower() and node.file})
        source_files = self._read_source_files(source_rel_files)

        impact_summary = (
            f"Impacted symbols: {', '.join(self.impact.changed_symbols)}\n"
            f"Ranked dependent tests: {', '.join([t.id for t in self.impact.ranked_tests[:5]])}"
        )

        target_failure_output = ""
        for t in baseline_run.tests:
            if t.id == self.failing_test or self.failing_test.endswith(t.id) or t.id.endswith(self.failing_test):
                target_failure_output = t.message or ""

        for attempt_n in range(1, self.max_attempts + 1):
            self.emit(AgentEvent(
                ts=time.time(),
                type="stage",
                title=f"Starting Repair Attempt {attempt_n}/{self.max_attempts}",
                payload={"attempt": attempt_n, "model": self.model_repair}
            ))

            prompt = build_repair_prompt(
                failing_test=self.failing_test,
                failure_output=target_failure_output,
                impact_summary=impact_summary,
                source_files=source_files,
                history_feedback=feedback
            )

            raw_reply = self.client.chat_completion(
                model=self.model_repair,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                attempt=attempt_n
            )

            blocks = extract_patch_blocks(raw_reply)
            rationale_lines = [
                line for line in raw_reply.splitlines()
                if not line.startswith("FILE:") and not line.startswith("<<<<<<<") and not line.startswith(">>>>>>>")
            ]
            rationale = "\n".join(rationale_lines).strip()

            current_attempt = RepairAttempt(
                n=attempt_n,
                model=self.model_repair,
                rationale=rationale,
                patch_blocks=blocks,
                diff="",
                status="applied"
            )

            if not blocks:
                current_attempt.status = "invalid_patch"
                attempts.append(current_attempt)
                feedback = f"Attempt {attempt_n} failed: No valid SEARCH/REPLACE blocks found in output."
                self.emit(AgentEvent(
                    ts=time.time(),
                    type="model_message",
                    title=f"Attempt {attempt_n}: No valid patch blocks found.",
                    payload={"status": "invalid_patch"}
                ))
                continue

            applied, msg = apply_patch_blocks(self.repo_path, blocks)
            if not applied:
                current_attempt.status = "invalid_patch"
                attempts.append(current_attempt)
                feedback = f"Attempt {attempt_n} rejected by guardrail: {msg}"
                self.emit(AgentEvent(
                    ts=time.time(),
                    type="model_message",
                    title=f"Attempt {attempt_n} Guardrail Violation: {msg}",
                    payload={"error": msg}
                ))
                reset_working_tree(self.repo_path)
                continue

            diff = get_git_diff(self.repo_path)
            current_attempt.diff = diff

            self.emit(AgentEvent(
                ts=time.time(),
                type="model_message",
                title=f"Patch Applied for Attempt {attempt_n}",
                payload={"diff": diff[:300]}
            ))

            # Tier 1: Target Test Verification
            t1_run = self.runner.run(self.repo_path, scope="target", test_ids=[self.failing_test])
            current_attempt.target_run = t1_run
            t1_failed = any(t.outcome != "passed" for t in t1_run.tests) or t1_run.exit_code != 0

            self.emit(AgentEvent(
                ts=time.time(),
                type="test_result",
                title=f"Tier 1 (Target Test): {'FAILED' if t1_failed else 'PASSED'}",
                payload={"exit_code": t1_run.exit_code, "passed": not t1_failed}
            ))

            if t1_failed:
                feedback = f"Target test '{self.failing_test}' still failed after patch:\n{t1_run.output_tail[-500:]}"
                current_attempt.status = "reverted"
                reset_working_tree(self.repo_path)
                attempts.append(current_attempt)
                continue

            # Tier 2: Blast Radius Impact-Ranked Tests
            impacted_test_ids = [t.id for t in self.impact.ranked_tests if t.id != self.failing_test]
            if impacted_test_ids:
                t2_run = self.runner.run(self.repo_path, scope="impacted", test_ids=impacted_test_ids)
                current_attempt.impacted_run = t2_run

                t2_regressions = [t.id for t in t2_run.tests if t.id in baseline_passing and t.outcome != "passed"]
                if t2_regressions:
                    self.emit(AgentEvent(
                        ts=time.time(),
                        type="test_result",
                        title=f"Tier 2 Regression Caught! ({len(t2_regressions)} tests broken)",
                        payload={"regressions": t2_regressions}
                    ))
                    feedback = f"Tier 2 regression caught in downstream tests: {', '.join(t2_regressions)}"
                    current_attempt.status = "reverted"
                    current_attempt.regressions = t2_regressions
                    reset_working_tree(self.repo_path)
                    attempts.append(current_attempt)
                    continue

            # Tier 3: Full Test Suite Baseline Diff
            t3_run = self.runner.run(self.repo_path, scope="full")
            current_attempt.full_run = t3_run

            full_regressions = [t.id for t in t3_run.tests if t.id in baseline_passing and t.outcome != "passed"]
            if full_regressions:
                self.emit(AgentEvent(
                    ts=time.time(),
                    type="test_result",
                    title=f"Tier 3 Regression Detected! ({len(full_regressions)} tests broken)",
                    payload={"regressions": full_regressions}
                ))
                feedback = f"Full suite regressions: {', '.join(full_regressions)}"
                current_attempt.status = "reverted"
                current_attempt.regressions = full_regressions
                reset_working_tree(self.repo_path)
                attempts.append(current_attempt)
                continue

            # All 3 tiers passed!
            current_attempt.status = "accepted"
            attempts.append(current_attempt)
            successful_patch = diff

            self.emit(AgentEvent(
                ts=time.time(),
                type="verdict",
                title="Verdict: VERIFIED_FIXED! Target and all regression suites passed.",
                payload={"attempt": attempt_n, "verdict": "VERIFIED_FIXED"}
            ))
            break

        verdict = "VERIFIED_FIXED" if successful_patch else "UNFIXED"
        if not successful_patch and any(a.regressions for a in attempts):
            verdict = "FIXED_WITH_REGRESSIONS"

        reset_working_tree(self.repo_path)

        # Residual risks format
        residual_risks: List[ResidualRisk] = []
        for n in self.impact.nodes:
            if n.risk == "high" or n.label == "predicted risk, unverified":
                residual_risks.append(ResidualRisk(
                    symbol=n.id,
                    file=n.file,
                    reason=f"Downstream dependency {n.id} in {n.file} was not exercised by any registered test.",
                    callers_count=len(n.lines)
                ))

        return FinalReport(
            verdict=verdict,
            patch=successful_patch,
            attempts=attempts,
            baseline_summary={"passed": len(baseline_passing)},
            residual_risk=residual_risks,
            metrics={
                "time_s": round(time.time() - start_time, 2),
                "tokens_total": self.client.get_token_usage()["tokens_total"],
                "attempts": len(attempts)
            }
        )
