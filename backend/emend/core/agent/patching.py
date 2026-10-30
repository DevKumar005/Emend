import os
import re
import ast
import subprocess
from typing import List, Tuple, Optional
from contracts.schemas import PatchBlock

FORBIDDEN_PATTERNS = [
    r"^tests/",
    r"/tests/",
    r"^test_.*\.py$",
    r"/test_.*\.py$",
    r".*_test\.py$",
    r"conftest\.py$",
    r"pytest\.ini$",
    r"tox\.ini$",
    r"setup\.py$",
    r"setup\.cfg$",
    r"pyproject\.toml$"
]
FORBIDDEN_FILE_PATTERNS = FORBIDDEN_PATTERNS

def extract_patch_blocks(raw_text: str) -> List[PatchBlock]:
    """Extracts FILE / SEARCH / REPLACE blocks from model response, allowing indentation."""
    normalized_text = raw_text.replace("\r\n", "\n")
    pattern = re.compile(
        r"^[ \t]*FILE:\s*(?P<file>[^\n]+)\n"
        r"[ \t]*<{7}\s*SEARCH\s*\n"
        r"(?P<search>.*?)\n"
        r"[ \t]*={7}\s*\n"
        r"(?P<replace>.*?)\n"
        r"[ \t]*>{7}\s*REPLACE",
        re.DOTALL | re.MULTILINE
    )
    blocks: List[PatchBlock] = []
    for match in pattern.finditer(normalized_text):
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

    # Guardrails validation
    for block in blocks:
        valid, err = _validate_guardrail(repo_path, block)
        if not valid:
            return False, err or "Guardrail validation failed."

    staged_files = {}
    for block in blocks:
        target_path = os.path.abspath(os.path.join(repo_path, block.file_path))
        if not os.path.isfile(target_path):
            return False, f"Target file '{block.file_path}' does not exist in repo."

        content = staged_files.get(target_path)
        if content is None:
            with open(target_path, "r", encoding="utf-8") as f:
                content = f.read().replace("\r\n", "\n")

        search_str = block.search.replace("\r\n", "\n")
        replace_str = block.replace.replace("\r\n", "\n")

        # Guardrail: Search block match check
        if search_str not in content:
            if search_str.strip() in content and content.count(search_str.strip()) == 1:
                search_str = search_str.strip()
                replace_str = replace_str.strip()
            else:
                return False, f"SEARCH block was not found in '{block.file_path}'."

        if content.count(search_str) > 1:
            return False, f"SEARCH block matches multiple locations in '{block.file_path}'. Provide more context."

        content = content.replace(search_str, replace_str, 1)
        staged_files[target_path] = content

    # AST syntax verification
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

def _validate_guardrail(repo_path: str, block: PatchBlock) -> Tuple[bool, Optional[str]]:
    norm_path = os.path.normpath(block.file_path).replace("\\", "/")

    # 1. Reject test tampering
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, norm_path, re.IGNORECASE):
            return False, f"Guardrail violation: Patches may not edit test or config file '{norm_path}'. Modifying tests or test configs is forbidden."

    # 2. Path traversal check
    target_path = os.path.abspath(os.path.join(repo_path, block.file_path))
    if not target_path.startswith(os.path.abspath(repo_path)):
        return False, f"Guardrail violation: Path traversal outside repo '{block.file_path}'."

    # 3. Size limit: max 60 changed lines
    replace_lines = len(block.replace.splitlines())
    if replace_lines > 60:
        return False, f"Guardrail violation: Patch block exceeds size limit (60 lines). Proposed: {replace_lines} lines."

    return True, None

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
    """Discards working tree modifications safely without deleting untracked files."""
    try:
        abs_path = os.path.abspath(repo_path)
        subprocess.run(["git", "checkout", "--", "."], cwd=abs_path, capture_output=True)
    except Exception:
        pass

class PatchApplier:
    """Class wrapper for backward compatibility."""

    @staticmethod
    def parse_blocks(raw_text: str) -> List[PatchBlock]:
        return extract_patch_blocks(raw_text)

    @staticmethod
    def check_guardrails(repo_path: str, block: PatchBlock) -> Tuple[bool, Optional[str]]:
        return _validate_guardrail(repo_path, block)

    @classmethod
    def apply_blocks(cls, repo_path: str, blocks: List[PatchBlock]) -> Tuple[bool, str, str]:
        ok, msg = apply_patch_blocks(repo_path, blocks)
        diff = get_git_diff(repo_path) if ok else ""
        return ok, msg, diff

    @staticmethod
    def generate_diff(repo_path: str) -> str:
        return get_git_diff(repo_path)
