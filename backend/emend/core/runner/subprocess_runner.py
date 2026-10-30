import os
import sys
import time
import shutil
import tempfile
import resource
import subprocess
from typing import List, Optional
from contracts.schemas import TestRun
from emend.core.runner.base import BaseRunner
from emend.core.runner.pytest_parser import parse_pytest_json_report

def _set_resource_limits():
    """Sets CPU limit safely on Darwin/Linux and memory cap on Linux."""
    try:
        # 60 CPU seconds limit
        resource.setrlimit(resource.RLIMIT_CPU, (60, 60))
    except (ValueError, OSError):
        pass

    if sys.platform.startswith("linux"):
        try:
            # 1.5 GB memory limit
            resource.setrlimit(resource.RLIMIT_AS, (1_500_000_000, 1_500_000_000))
        except (ValueError, OSError):
            pass

class SubprocessRunner(BaseRunner):
    def run(
        self,
        repo_path: str,
        scope: str = "target",
        test_ids: Optional[List[str]] = None,
        timeout: int = 60
    ) -> TestRun:
        """Executes pytest in a sandbox copy of repo_path with scrubbed environment."""
        temp_dir = tempfile.mkdtemp(prefix="emend_run_")
        try:
            # Copy repo content to isolated temp working directory
            shutil.copytree(repo_path, temp_dir, dirs_exist_ok=True)
            report_file = os.path.join(temp_dir, ".report.json")

            args = [
                sys.executable,
                "-m",
                "pytest",
                f"--json-report-file={report_file}",
                "--json-report",
                f"--timeout={timeout}",
            ]

            if test_ids:
                args.extend(test_ids)

            # Scrubbed environment: prevent child process from accessing secrets
            clean_env = {
                "PATH": os.environ.get("PATH", ""),
                "HOME": temp_dir,
                "PYTHONPATH": f"{temp_dir}:{os.environ.get('PYTHONPATH', '')}",
                "PYTHONDONTWRITEBYTECODE": "1"
            }

            start_time = time.time()
            proc = subprocess.run(
                args,
                cwd=temp_dir,
                env=clean_env,
                preexec_fn=_set_resource_limits if os.name != "nt" else None,
                capture_output=True,
                text=True,
                timeout=timeout + 5
            )
            duration = time.time() - start_time

            test_run = parse_pytest_json_report(
                report_path=report_file,
                command=" ".join(args),
                exit_code=proc.returncode,
                duration_s=duration,
                raw_stdout=proc.stdout + "\n" + proc.stderr
            )
            test_run.scope = scope  # type: ignore
            return test_run

        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)