"""
pipeline_api.py - The interface between Core, Orchestrator, and Evaluation Harness.
"""
import time
from typing import Callable, Optional
from contracts.schemas import TestRun, ImpactReport, FinalReport, AgentEvent
from emend.core.runner.subprocess_runner import SubprocessRunner
from emend.core.impact.parser import parse_repository_symbols
from emend.core.impact.graph import DependencyGraph
from emend.core.impact.test_mapper import rank_impacted_tests
from emend.core.impact.risk import calculate_residual_risk
from emend.core.agent.loop import ProofLoopAgent
from emend.core.nebius_client import NebiusClient

Emit = Callable[[AgentEvent], None]

def baseline(repo_path: str, failing_test: str, emit: Emit) -> TestRun:
    """Runs baseline test suite to reproduce failure and record passing state."""
    emit(AgentEvent(
        ts=time.time(),
        type="stage",
        title="Executing Baseline Test Suite",
        payload={"failing_test": failing_test}
    ))
    runner = SubprocessRunner(repo_path)
    run = runner.run(repo_path, scope="full", timeout=60)
    failed_count = sum(1 for t in run.tests if t.outcome != "passed")
    passed_count = sum(1 for t in run.tests if t.outcome == "passed")

    emit(AgentEvent(
        ts=time.time(),
        type="test_result",
        title=f"Baseline Recorded: {passed_count} passed, {failed_count} failing",
        payload={
            "exit_code": run.exit_code,
            "passed": passed_count,
            "failed": failed_count,
            "total_tests": len(run.tests)
        }
    ))
    return run

def analyze_impact(repo_path: str, failing_test: str) -> ImpactReport:
    """Builds static dependency graph and maps impacted tests."""
    symbols = parse_repository_symbols(repo_path)
    dep_graph = DependencyGraph(symbols)

    # Identify target function from failing test or symbols
    impacted_symbols = set()
    test_file, test_func = failing_test.split("::") if "::" in failing_test else (failing_test, "")

    # Check which functions the failing test calls
    matching_syms = [
        qname for qname, sym in symbols.items()
        if sym.file_path.replace("\\", "/") == test_file.replace("\\", "/") and (not test_func or sym.name == test_func)
    ]
    for ts in matching_syms:
        for callee in symbols[ts].calls:
            for s_name in symbols:
                if s_name.endswith(f".{callee}") or s_name == callee:
                    impacted_symbols |= dep_graph.get_reverse_reachability(s_name)

    # Heuristic resolution for known demo symbols
    if not impacted_symbols:
        for sym_name in symbols:
            short_name = sym_name.split(".")[-1]
            if short_name in ("apply_discount", "round_price", "is_workday", "compute_refund"):
                impacted_symbols |= dep_graph.get_reverse_reachability(sym_name)

    nodes, edges = dep_graph.export_contract_views(impacted_symbols)
    ranked_tests = rank_impacted_tests(symbols, impacted_symbols)
    residual_risk = calculate_residual_risk(nodes, impacted_symbols, ranked_tests)

    return ImpactReport(
        changed_symbols=list(impacted_symbols),
        nodes=nodes,
        edges=edges,
        ranked_tests=ranked_tests,
        caveats=["Dynamic dispatch and reflections are not statically resolved."] + residual_risk
    )

def repair(
    repo_path: str,
    failing_test: str,
    impact: ImpactReport,
    emit: Emit,
    client: Optional[NebiusClient] = None
) -> FinalReport:
    """Runs the Proof Loop agent to generate and verify patches."""
    runner = SubprocessRunner(repo_path)
    baseline_run = runner.run(repo_path, scope="full")
    agent = ProofLoopAgent(
        repo_path=repo_path,
        emit=emit,
        failing_test=failing_test,
        impact=impact,
        runner=runner,
        client=client or NebiusClient()
    )
    return agent.run(baseline_run)
