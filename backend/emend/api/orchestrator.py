import os
import asyncio
from typing import Optional
from contracts.schemas import AgentEvent, ImpactReport, FinalReport, TestRun
from .store import DatabaseStore
from .events import broadcaster
from ..core import pipeline_api

class AnalysisOrchestrator:
    def __init__(self, store: Optional[DatabaseStore] = None):
        self.store = store or DatabaseStore()

    def _resolve_repo_path(self, repo_source: str) -> str:
        # Check bundled demo repos
        # We search relative to workspace or backend
        candidate_paths = [
            os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../demo_repos", repo_source)),
            os.path.abspath(os.path.join("demo_repos", repo_source)),
            os.path.abspath(repo_source)
        ]
        for p in candidate_paths:
            if os.path.exists(p):
                return p
        raise ValueError(f"Repository source '{repo_source}' could not be resolved.")

    async def run_pipeline(
        self,
        job_id: str,
        repo_source: str,
        failing_test: str,
        mode: str = "hosted",
        auto_repair: bool = True
    ):
        loop = asyncio.get_running_loop()

        def emit_event(event: AgentEvent):
            self.store.add_event(job_id, event)
            # Schedule async broadcast on event loop
            asyncio.run_coroutine_threadsafe(broadcaster.broadcast(job_id, event), loop)

        try:
            # 1. Intake
            self.store.update_job_status(job_id, "baseline")
            emit_event(AgentEvent(
                type="stage",
                title="Stage 1: Intake & Validation",
                payload={"repo": repo_source, "failing_test": failing_test, "mode": mode}
            ))

            repo_path = self._resolve_repo_path(repo_source)

            # 2. Baseline run
            emit_event(AgentEvent(
                type="stage",
                title="Stage 2: Baseline Execution",
                payload={"status": "executing_full_test_suite"}
            ))
            baseline_run: TestRun = await loop.run_in_executor(
                None, pipeline_api.baseline, repo_path, failing_test, emit_event
            )
            self.store.save_test_run(job_id, baseline_run)

            # 3. Impact analysis (Blast Radius Engine)
            self.store.update_job_status(job_id, "impact")
            emit_event(AgentEvent(
                type="stage",
                title="Stage 3: Blast Radius AST & Call Graph Analysis",
                payload={"status": "parsing_ast_and_mapping_tests"}
            ))
            impact_report: ImpactReport = await loop.run_in_executor(
                None, pipeline_api.analyze_impact, repo_path, failing_test
            )
            self.store.save_impact_report(job_id, impact_report)

            emit_event(AgentEvent(
                type="test_result",
                title=f"Impact Graph Generated: {len(impact_report.nodes)} nodes, {len(impact_report.ranked_tests)} tests ranked",
                payload={
                    "nodes_count": len(impact_report.nodes),
                    "ranked_tests": [t.id for t in impact_report.ranked_tests[:3]]
                }
            ))

            if auto_repair:
                # 4. Repair Loop (Proof Loop Agent)
                self.store.update_job_status(job_id, "repair")
                emit_event(AgentEvent(
                    type="stage",
                    title="Stage 4: Proof Loop Repair (up to 3 attempts with 3-tier verification)",
                    payload={"max_attempts": 3}
                ))

                final_report: FinalReport = await loop.run_in_executor(
                    None, pipeline_api.repair, repo_path, failing_test, impact_report, emit_event
                )
                self.store.save_final_report(job_id, final_report)
                for att in final_report.attempts:
                    if att.target_run:
                        self.store.save_test_run(job_id, att.target_run)
                    if att.impacted_run:
                        self.store.save_test_run(job_id, att.impacted_run)
                    if att.full_run:
                        self.store.save_test_run(job_id, att.full_run)
                self.store.update_job_status(job_id, "done", attempts=len(final_report.attempts))

                emit_event(AgentEvent(
                    type="verdict",
                    title=f"Repair Complete: {final_report.verdict}",
                    payload={
                        "verdict": final_report.verdict,
                        "attempts_used": len(final_report.attempts),
                        "residual_risks_count": len(final_report.residual_risk),
                        "tokens_total": final_report.metrics.get("tokens_total", 0)
                    }
                ))
            else:
                self.store.update_job_status(job_id, "done")

        except Exception as e:
            err_msg = str(e)
            print(f"[AnalysisOrchestrator] Job {job_id} encountered error: {err_msg}")
            self.store.update_job_status(job_id, "error", error_msg=err_msg)
            emit_event(AgentEvent(
                type="error",
                title=f"Pipeline Error: {err_msg}",
                payload={"error": err_msg}
            ))

orchestrator = AnalysisOrchestrator()
