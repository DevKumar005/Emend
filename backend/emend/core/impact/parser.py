import os
import ast
from typing import Dict, List, Any

class CodeSymbol:
    def __init__(self, qualified_name: str, kind: str, file_path: str, start_line: int, end_line: int):
        self.qualified_name = qualified_name
        self.kind = kind
        self.file_path = file_path
        self.lines = [start_line, end_line]
        self.calls: List[str] = []

def parse_repository_symbols(repo_path: str) -> Dict[str, CodeSymbol]:
    """Scans all Python files in repo_path and extracts module, class, and function symbols."""
    symbols: Dict[str, CodeSymbol] = {}
    
    for root, dirs, files in os.walk(repo_path):
        # Ignore virtualenvs, hidden files, and cache dirs
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("venv", ".venv", "__pycache__", "site-packages")]
        for file in files:
            if not file.endswith(".py"):
                continue
                
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, repo_path).replace("\\", "/")
            mod_name = rel_path.replace(".py", "").replace("/", ".")
            if mod_name.endswith(".__init__"):
                mod_name = mod_name[:-9]

            try:
                with open(abs_path, "r", encoding="utf-8") as f:
                    source = f.read()
                tree = ast.parse(source, filename=rel_path)
            except Exception:
                continue

            symbols[mod_name] = CodeSymbol(
                qualified_name=mod_name,
                kind="module",
                file_path=rel_path,
                start_line=1,
                end_line=len(source.splitlines()) or 1
            )

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    fn_name = f"{mod_name}.{node.name}"
                    sym = CodeSymbol(
                        qualified_name=fn_name,
                        kind="function",
                        file_path=rel_path,
                        start_line=node.lineno,
                        end_line=getattr(node, "end_lineno", node.lineno)
                    )
                    # Extract internal function call targets
                    for child in ast.walk(node):
                        if isinstance(child, ast.Call):
                            if isinstance(child.func, ast.Name):
                                sym.calls.append(child.func.id)
                            elif isinstance(child.func, ast.Attribute):
                                sym.calls.append(child.func.attr)
                    symbols[fn_name] = sym

    return symbols