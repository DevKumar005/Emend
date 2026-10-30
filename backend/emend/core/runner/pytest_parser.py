import json
import re
from typing import List, Dict, Any, Optional
from contracts.schemas import TestCaseResult, TestRun

def parse_pytest_json_report(
    report_path: str,
    command: str,
    exit_code: int,
    duration_s: float,
    raw_stdout: str = ""
) -> TestRun:
    """Parses a pytest-json-report file into a typed TestRun contract."""
    test_results: List[TestCaseResult] = []

    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)

        for test in data.get("tests", []):
            test_id = test.get("nodeid", "")
            outcome = test.get("outcome", "failed")
            duration = (
                float(test.get("setup", {}).get("duration", 0.0))
                + float(test.get("call", {}).get("duration", 0.0))
                + float(test.get("teardown", {}).get("duration", 0.0))
            )

            message = None
            if outcome in ("failed", "error"):
                call_info = test.get("call", {})
                message = call_info.get("crash", {}).get("message") or call_info.get("longrepr", "")

            valid_outcome = outcome if outcome in ("passed", "failed", "skipped") else "error"
            test_results.append(
                TestCaseResult(
                    id=test_id,
                    outcome=valid_outcome,
                    duration=round(duration, 4),
                    message=str(message)[:1000] if message else None,
                )
            )
    except Exception as e:
        # Fallback to regex stdout parsing if JSON report failed
        test_results = PytestOutputParser.parse_stdout_fallback(raw_stdout)
        output_tail = raw_stdout[-2000:] if raw_stdout else str(e)
        return TestRun(
            scope="target",
            command=command,
            exit_code=exit_code,
            duration_s=round(duration_s, 3),
            tests=test_results,
            output_tail=output_tail,
        )

    output_tail = raw_stdout[-2000:] if raw_stdout else ""
    return TestRun(
        scope="target",
        command=command,
        exit_code=exit_code,
        duration_s=round(duration_s, 3),
        tests=test_results,
        output_tail=output_tail,
    )

class PytestOutputParser:
    """Helper parser class for backward compatibility."""

    @staticmethod
    def parse_json_report(
        json_path: str,
        stdout: str,
        exit_code: int,
        duration: float,
        scope: str = "target",
        command: str = ""
    ) -> TestRun:
        run = parse_pytest_json_report(json_path, command, exit_code, duration, stdout)
        run.scope = scope  # type: ignore
        return run

    @staticmethod
    def parse_stdout_fallback(stdout: str) -> List[TestCaseResult]:
        items: List[TestCaseResult] = []
        for line in stdout.splitlines():
            match = re.search(r"([\w/\.-]+::[\w_]+)\s+(PASSED|FAILED|ERROR)", line, re.IGNORECASE)
            if match:
                test_id = match.group(1)
                status = match.group(2).lower()
                items.append(
                    TestCaseResult(
                        id=test_id,
                        outcome="passed" if status == "passed" else "failed",
                        duration=0.01,
                        message=None,
                    )
                )
        return items
