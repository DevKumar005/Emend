from typing import List, Set, Dict, Any, Optional
from contracts.schemas import NodeInfo, RankedTest, ImpactReport, ResidualRisk
from emend.core.impact.graph import DependencyGraphBuilder
from emend.core.impact.test_mapper import TestMapper

def calculate_residual_risk(
    nodes: List[NodeInfo],
    impacted_symbols: Set[str],
    ranked_tests: List[RankedTest]
) -> List[str]:
    """Identifies impacted functions that have zero corresponding test coverage."""
    tested_files = {t.id.split("::")[0] for t in ranked_tests}
    residual: List[str] = []

    for node in nodes:
        if node.id in impacted_symbols and node.kind == "function":
            if not any(node.file in tf for tf in tested_files):
                residual.append(f"{node.id} in {node.file} has no direct static test mapping.")

    return residual

class RiskAnalyzer:
    """Class wrapper for backward compatibility."""

    def __init__(self, repo_path: str, builder: DependencyGraphBuilder, mapper: TestMapper):
        self.repo_path = repo_path
        self.builder = builder
        self.mapper = mapper

    def analyze(
        self,
        suspected_symbol: str,
        failing_test_id: str,
        executed_tests: Optional[Set[str]] = None
    ) -> ImpactReport:
        impacted_symbols = self.builder.get_reverse_dependents(suspected_symbol)
        nodes, edges = self.builder.dep_graph.export_contract_views(impacted_symbols)
        ranked_tests = self.mapper.rank_tests_for_impact(suspected_symbol, impacted_symbols, failing_test_id)
        residual = calculate_residual_risk(nodes, impacted_symbols, ranked_tests)

        return ImpactReport(
            changed_symbols=list(impacted_symbols),
            nodes=nodes,
            edges=edges,
            ranked_tests=ranked_tests,
            caveats=["Dynamic dispatch and reflections are not statically resolved."] + residual
        )
