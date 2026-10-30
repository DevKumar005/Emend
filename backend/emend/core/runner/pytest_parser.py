import json
from typing import Dict, Any, List
from contracts.schemas import TestCaseResult, TestRun

def parse_pytest_json_report(report_path: str, command: str, exit_code: int, duration_s: float, raw_stdout: str = "") -> TestRun:
    """Parses a pytest-json-report file into a typed TestRun contract."""
    test_results: List[TestCaseResult] = []
    
    try:
        with open(report_path, "r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)
            
        for test in data.get("tests", []):
            test_id = test.get("nodeid", "")
            outcome = test.get("outcome", "failed")
            duration = float(test.get("setup", {}).get("duration", 0.0)) + \
                       float(test.get("call", {}).get("duration", 0.0)) + \
                       float(test.get("teardown", {}).get("duration", 0.0))
            
            message = None
            if outcome in ("failed", "error"):
                call_info = test.get("call", {})
                message = call_info.get("crash", {}).get("message") or call_info.get("longrepr", "")
            
            # Map outcome string to schema literal
            valid_outcome = outcome if outcome in ("passed", "failed", "skipped") else "error"
            test_results.append(TestCaseResult(
                id=test_id,
                outcome=valid_outcome,
                duration=round(duration, 4),
                message=str(message)[:1000] if message else None
            ))
    except Exception as e:
        # Fallback if report failed to write or parse
        output_tail = raw_stdout[-2000:] if raw_stdout else str(e)
        return TestRun(
            scope="target",
            command=command,
            exit_code=exit_code,
            duration_s=round(duration_s, 3),
            tests=[],
            output_tail=output_tail
        )

    output_tail = raw_stdout[-2000:] if raw_stdout else ""
    return TestRun(
        scope="target",
        command=command,
        exit_code=exit_code,
        duration_s=round(duration_s, 3),
        tests=test_results,
        output_tail=output_tail
    )