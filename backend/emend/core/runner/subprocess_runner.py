import os
import sys
import time
import shutil
import tempfile
import subprocess
from typing import List, Optional
from contracts.schemas import TestRun
from emend.core.runner.base import BaseRunner
from emend.core.runner.pytest_parser import parse_pytest_json_report, PytestOutputParser

try:
    import resource
except ImportError:
    resource = None

def _set_resource_limits():
    """Sets CPU limit safely on Darwin/Linux and memory cap on Linux."""
    if resource is None or os.name == "nt":
        return
    try:
        resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
    except (ValueError, OSError):
        pass

    if sys.platform.startswith("linux"):
        try:
            resource.setrlimit(resource.RLIMIT_AS, (1_500_000_000, 1_500_000_000))
        except (ValueError, OSError):
            pass

class SubprocessRunner(BaseRunner):
    """Executes pytest in a sandboxed subprocess with resource limits and scrubbed secrets."""

    def __init__(self, repo_path: Optional[str] = None, use_temp_copy: bool = False):
        self.repo_path = os.path.abspath(repo_path) if repo_path else None
        self.use_temp_copy = use_temp_copy

    def run(
        self,
        repo_path: Optional[str] = None,
        scope: str = "target",
        test_ids: Optional[List[str]] = None,
        timeout: int = 60
    ) -> TestRun:
        target_repo = os.path.abspath(repo_path or self.repo_path or ".")
        
        # Determine execution working directory
        if self.use_temp_copy:
            exec_dir = tempfile.mkdtemp(prefix="emend_run_")
            shutil.copytree(target_repo, exec_dir, dirs_exist_ok=True)
            report_file = os.path.join(exec_dir, ".report.json")
        else:
            exec_dir = target_repo
            report_file = os.path.join(exec_dir, f".report_{int(time.time() * 1000)}.json")

        try:
            args = [
                sys.executable,
                "-m",
                "pytest",
                f"--json-report-file={report_file}",
                "--json-report",
                "-o", "pythonpath=.",
                "-p", "no:cacheprovider",
                f"--timeout={timeout}",
            ]

            if test_ids:
                args.extend(test_ids)

            # Scrubbed environment: prevent child process from accessing secrets
            clean_env = {
                k: v for k, v in os.environ.items()
                if not any(secret in k.upper() for secret in ("KEY", "TOKEN", "SECRET", "PASSWORD", "AUTH", "CREDENTIAL"))
            }
            clean_env["HOME"] = exec_dir
            clean_env["PYTHONPATH"] = f"{exec_dir}{os.pathsep}{os.environ.get('PYTHONPATH', '')}"
            clean_env["PYTHONDONTWRITEBYTECODE"] = "1"

            start_time = time.time()
            try:
                proc = subprocess.run(
                    args,
                    cwd=exec_dir,
                    env=clean_env,
                    preexec_fn=_set_resource_limits if (os.name != "nt" and resource is not None) else None,
                    capture_output=True,
                    text=True,
                    timeout=timeout + 5
                )
                duration = time.time() - start_time
                exit_code = proc.returncode
                raw_stdout = proc.stdout + "\n" + proc.stderr
            except subprocess.TimeoutExpired:
                duration = timeout
                exit_code = 124
                raw_stdout = f"Test execution timed out after {timeout} seconds."
            except Exception as e:
                duration = time.time() - start_time
                exit_code = 1
                raw_stdout = f"Execution error: {e}"

            test_run = parse_pytest_json_report(
                report_path=report_file,
                command=" ".join(args),
                exit_code=exit_code,
                duration_s=duration,
                raw_stdout=raw_stdout
            )
            test_run.scope = scope  # type: ignore
            return test_run

        finally:
            if self.use_temp_copy and os.path.exists(exec_dir):
                shutil.rmtree(exec_dir, ignore_errors=True)
            elif os.path.exists(report_file):
                try:
                    os.remove(report_file)
                except Exception:
                    pass

    def reset_repo(self) -> None:
        target = self.repo_path or "."
        try:
            subprocess.run(["git", "checkout", "--", "."], cwd=target, capture_output=True)
        except Exception:
            pass

    def cleanup(self) -> None:
        pass
