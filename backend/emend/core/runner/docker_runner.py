import os
import subprocess
import time
from typing import List, Optional
from contracts.schemas import TestRun
from emend.core.runner.base import BaseRunner
from emend.core.runner.pytest_parser import parse_pytest_json_report
from emend.core.runner.subprocess_runner import SubprocessRunner

class DockerRunner(BaseRunner):
    """Runs pytest inside an isolated Docker container with zero network access
    and strict memory/CPU caps for local repository execution.
    """

    def __init__(self, image_tag: str = "emend-sandbox:latest", repo_path: Optional[str] = None):
        self.image_tag = image_tag
        self.repo_path = os.path.abspath(repo_path) if repo_path else None
        self.fallback = SubprocessRunner(self.repo_path)

    def is_docker_available(self) -> bool:
        try:
            res = subprocess.run(["docker", "info"], capture_output=True, timeout=3)
            return res.returncode == 0
        except Exception:
            return False

    def run(
        self,
        repo_path: Optional[str] = None,
        scope: str = "target",
        test_ids: Optional[List[str]] = None,
        timeout: int = 60
    ) -> TestRun:
        target_repo = os.path.abspath(repo_path or self.repo_path or ".")
        
        if not self.is_docker_available():
            return self.fallback.run(target_repo, scope=scope, test_ids=test_ids, timeout=timeout)

        report_file = os.path.join(target_repo, ".report.json")

        container_cmd = [
            "pytest",
            "--json-report",
            "--json-report-file=/repo/.report.json",
            f"--timeout={timeout}"
        ]
        if test_ids:
            container_cmd.extend(test_ids)

        docker_cmd = [
            "docker", "run", "--rm",
            "--network", "none",
            "--memory", "1500m",
            "--cpus", "2.0",
            "--pids-limit", "64",
            "-v", f"{target_repo}:/repo",
            "-w", "/repo",
            self.image_tag
        ] + container_cmd

        start_time = time.time()
        try:
            proc = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=timeout + 10
            )
            duration = time.time() - start_time
            return parse_pytest_json_report(
                report_path=report_file,
                command=" ".join(docker_cmd),
                exit_code=proc.returncode,
                duration_s=duration,
                raw_stdout=proc.stdout + "\n" + proc.stderr
            )
        except Exception as e:
            duration = time.time() - start_time
            return self.fallback.run(target_repo, scope=scope, test_ids=test_ids, timeout=timeout)
        finally:
            if os.path.exists(report_file):
                try:
                    os.remove(report_file)
                except OSError:
                    pass

    def reset_repo(self) -> None:
        self.fallback.reset_repo()
