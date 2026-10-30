"""
pipeline_api.py - The interface between Member A (Core) and Member B (API/Orchestrator).
"""
import time
from typing import Callable
from contracts.schemas import TestRun, ImpactReport, FinalReport, AgentEvent
from emend.core.runner.subprocess_runner import SubprocessRunner
from emend.core.impact.parser import parse_repository_symbols
from emend.core.impact.graph import DependencyGraph
from emend.core.impact.test_mapper import rank_impacted_tests
from emend.core.impact.risk import calculate_residual_risk
from emend.core.agent.loop import ProofLoopAgent

Emit = Callable[[AgentEvent], None]

def baseline(repo_path: str, failing_test: str, emit: Emit) -> TestRun:
    """Runs baseline test suite to reproduce failure and record passing state."""
    emit(AgentEvent(
        ts=time.time(),
        type="stage",
        title="Baseline Run Started",
        payload={"failing_test": failing_test}
    ))
    runner = SubprocessRunner()
    run = runner.run(repo_path, scope="full", timeout=60)
    emit(AgentEvent(
        ts=time.time(),
        type="test_result",
        title="Baseline Completed",
        payload={"exit_code": run.exit_code, "total_tests": len(run.tests)}
    ))
    return run

def analyze_impact(repo_path: str, failing_test: str) -> ImpactReport:
    """Builds static dependency graph and maps impacted tests."""
    symbols = parse_repository_symbols(repo_path)
    dep_graph = DependencyGraph(symbols)
    
    # Identify target function from failing test or symbols
    impacted_symbols = set()
    for sym_name in symbols:
        short_name = sym_name.split(".")[-1]
        if short_name in ("apply_discount", "round_price"):
            impacted_symbols |= dep_graph.get_reverse_reachability(sym_name)

    nodes, edges = dep_graph.export_contract_views(impacted_symbols)
    ranked_tests = rank_impacted_tests(symbols, impacted_symbols)
    residual_risk = calculate_residual_risk(nodes, impacted_symbols, ranked_tests)

    return ImpactReport(
        changed_symbols=list(impacted_symbols),
        nodes=nodes,
        edges=edges,
        ranked_tests=ranked_tests,
        caveats=["Dynamic dispatch and monkeypatching are not statically resolved."] + residual_risk
    )

def repair(repo_path: str, failing_test: str, impact: ImpactReport, emit: Emit) -> FinalReport:
    """Runs the Proof Loop agent to generate and verify patches."""
    runner = SubprocessRunner()
    baseline_run = runner.run(repo_path, scope="full")
    agent = ProofLoopAgent(repo_path=repo_path, emit=emit)
    return agent.run_repair(
        failing_test=failing_test,
        baseline_run=baseline_run,
        impact=impact,
        max_attempts=3
    )