import os
import pytest
from emend.core.impact.parser import ASTIndexer
from emend.core.impact.graph import DependencyGraphBuilder
from emend.core.agent.patching import PatchApplier, PatchBlock

def test_ast_indexer_and_graph():
    repo_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../demo_repos/billing_ripple"))
    assert os.path.exists(repo_path), f"Demo repo not found at {repo_path}"

    builder = DependencyGraphBuilder(repo_path)
    symbols = builder.symbols

    # Verify key symbols exist
    round_sym = [s for s in symbols if s.endswith("round_price")]
    assert len(round_sym) > 0, "round_price symbol not found in AST index"

    # Verify reverse reachability finds callers
    dependents = builder.get_reverse_dependents(round_sym[0])
    assert len(dependents) >= 3, f"Expected multiple dependents, got {dependents}"

def test_guardrail_rejects_test_file_modification(tmp_path):
    block = PatchBlock(
        file_path="tests/test_billing.py",
        search_content="def test_something():",
        replace_content="def test_something(): pass"
    )
    valid, err = PatchApplier.check_guardrails(str(tmp_path), block)
    assert not valid
    assert "Modifying tests or test configs is forbidden" in err

def test_guardrail_rejects_path_traversal(tmp_path):
    block = PatchBlock(
        file_path="../../etc/passwd",
        search_content="root",
        replace_content="hacked"
    )
    valid, err = PatchApplier.check_guardrails(str(tmp_path), block)
    assert not valid
    assert "Path traversal" in err

def test_guardrail_rejects_large_patch(tmp_path):
    dummy_file = tmp_path / "app.py"
    dummy_file.write_text("x = 1\n")
    
    long_replacement = "\n".join([f"x = {i}" for i in range(70)])
    block = PatchBlock(
        file_path="app.py",
        search_content="x = 1",
        replace_content=long_replacement
    )
    valid, err = PatchApplier.check_guardrails(str(tmp_path), block)
    assert not valid
    assert "exceeds size limit" in err
