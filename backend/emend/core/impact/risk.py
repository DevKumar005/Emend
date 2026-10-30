from typing import List, Set
from contracts.schemas import NodeInfo, RankedTest

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