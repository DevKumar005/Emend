import os
import subprocess
import time
from typing import List, Optional
from contracts.schemas import TestRun
from emend.core.runner.base import BaseRunner
from emend.core.runner.pytest_parser import parse_pytest_json_report

class DockerRunner(BaseRunner):
    """
    Runs pytest inside an isolated Docker container with zero network access
    and strict memory/CPU caps for local repository execution.
    """
    def __init__(self, image_tag: str = "emend-sandbox:latest"):
        self.image_tag = image_tag

    def run(
        self,
        repo_path: str,
        scope: str = "target",
        test_ids: Optional[List[str]] = None,
        timeout: int = 60
    ) -> TestRun:
        abs_repo = os.path.abspath(repo_path)
        report_file = os.path.join(abs_repo, ".report.json")
        
        # Command executed inside container
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
            "-v", f"{abs_repo}:/repo",
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
            return TestRun(
                scope=scope,  # type: ignore
                command=" ".join(docker_cmd),
                exit_code=1,
                duration_s=round(duration, 3),
                tests=[],
                output_tail=f"DockerRunner execution failed: {str(e)}"
            )
        finally:
            if os.path.exists(report_file):
                try:
                    os.remove(report_file)
                except OSError:
                    pass