import os
import pytest
from emend.core.impact.parser import ASTIndexer
from emend.core.impact.graph import DependencyGraphBuilder

def test_ast_indexer_and_graph():
    repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../demo_repos/billing_ripple"))
    assert os.path.exists(repo_path), f"Demo repo not found at {repo_path}"

    builder = DependencyGraphBuilder(repo_path)
    symbols = builder.symbols

    round_sym = [s for s in symbols if s.endswith("round_price")]
    assert len(round_sym) > 0, "round_price symbol not found in AST index"

    dependents = builder.get_reverse_dependents(round_sym[0])
    assert len(dependents) >= 3, f"Expected multiple dependents, got {dependents}"

