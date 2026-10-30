import os
import re
import ast
import subprocess
from typing import List, Tuple
from contracts.schemas import PatchBlock

FORBIDDEN_PATTERNS = [
    r"^tests/",
    r"^test_.*\.py$",
    r".*_test\.py$",
    r"conftest\.py$",
    r"pytest\.ini$",
    r"tox\.ini$",
    r"setup\.cfg$",
    r"pyproject\.toml$"
]

def extract_patch_blocks(raw_text: str) -> List[PatchBlock]:
    """Extracts FILE / SEARCH / REPLACE blocks from model response."""
    pattern = re.compile(
        r"FILE:\s*(?P<file>[^\n]+)\s*"
        r"<<<<<<<\s*SEARCH\s*\n(?P<search>.*?)\n"
        r"=======\s*\n(?P<replace>.*?)\n"
        r">>>>>>>\s*REPLACE",
        re.DOTALL
    )
    blocks: List[PatchBlock] = []
    for match in pattern.finditer(raw_text):
        blocks.append(PatchBlock(
            file_path=match.group("file").strip(),
            search=match.group("search"),
            replace=match.group("replace")
        ))
    return blocks

def apply_patch_blocks(repo_path: str, blocks: List[PatchBlock]) -> Tuple[bool, str]:
    """Applies patch blocks deterministically, validating syntax and integrity guardrails."""
    if not blocks:
        return False, "No valid SEARCH/REPLACE blocks found in model output."

    # Guardrail 1: Disallow modifications to test files or configs
    for block in blocks:
        norm_path = os.path.normpath(block.file_path).replace("\\", "/")
        for pattern in FORBIDDEN_PATTERNS:
            if re.search(pattern, norm_path):
                return False, f"Guardrail violation: Patches may not edit test or config file '{norm_path}'."

    # Apply blocks in memory and verify syntax before writing to disk
    staged_files = {}
    for block in blocks:
        target_path = os.path.abspath(os.path.join(repo_path, block.file_path))
        
        # Guardrail 2: Path traversal check
        if not target_path.startswith(os.path.abspath(repo_path)):
            return False, f"Guardrail violation: Path traversal outside repo '{block.file_path}'."

        if not os.path.isfile(target_path):
            return False, f"Target file '{block.file_path}' does not exist in repo."

        content = staged_files.get(target_path)
        if content is None:
            with open(target_path, "r", encoding="utf-8") as f:
                content = f.read()

        # Guardrail 3: Search block match check
        if block.search not in content:
            return False, f"SEARCH block was not found in '{block.file_path}'."
        if content.count(block.search) > 1:
            return False, f"SEARCH block matches multiple locations in '{block.file_path}'. Provide more surrounding context."

        content = content.replace(block.search, block.replace, 1)
        staged_files[target_path] = content

    # Guardrail 4: AST syntax verification
    for target_path, content in staged_files.items():
        if target_path.endswith(".py"):
            try:
                ast.parse(content, filename=target_path)
            except SyntaxError as e:
                return False, f"SyntaxError in '{os.path.relpath(target_path, repo_path)}': {e.msg} at line {e.lineno}."

    # Commit verified changes to disk
    for target_path, content in staged_files.items():
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content)

    return True, "All patches applied successfully."

def get_git_diff(repo_path: str) -> str:
    """Returns the unified diff of unstaged changes."""
    try:
        res = subprocess.run(
            ["git", "diff"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        return res.stdout
    except Exception:
        return ""

def reset_working_tree(repo_path: str) -> None:
    """Discards working tree modifications safely."""
    subprocess.run(["git", "checkout", "--", "."], cwd=repo_path, capture_output=True)