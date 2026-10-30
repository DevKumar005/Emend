from typing import Dict, List, Set
from contracts.schemas import RankedTest
from emend.core.impact.parser import CodeSymbol

def rank_impacted_tests(
    all_symbols: Dict[str, CodeSymbol],
    impacted_symbols: Set[str]
) -> List[RankedTest]:
    """Ranks test functions that directly or transitively call any impacted symbol."""
    ranked: List[RankedTest] = []
    
    for sym_name, sym in all_symbols.items():
        if "test" not in sym.file_path.lower():
            continue
            
        score = 0.0
        reasons = []

        for call in sym.calls:
            for impacted in impacted_symbols:
                if impacted.endswith(f".{call}") or impacted == call:
                    score += 1.0
                    reasons.append(f"Calls impacted symbol {impacted}")

        if score > 0:
            test_id = f"{sym.file_path}::{sym_name.split('.')[-1]}"
            ranked.append(RankedTest(
                id=test_id,
                score=min(score, 1.0),
                reason="; ".join(reasons),
                label="static-predicted"
            ))

    ranked.sort(key=lambda t: t.score, reverse=True)
    return ranked