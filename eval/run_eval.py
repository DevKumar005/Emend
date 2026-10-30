import os
import sys
import json
import time

# Ensure backend and repo root are importable
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(repo_root, "backend"))
sys.path.insert(0, repo_root)

from emend.core.pipeline_api import baseline, analyze_impact, repair
from emend.core.agent.patching import PatchApplier, PatchBlock

EVAL_CASES = [
    {
        "id": "shopcalc_simple",
        "repo": "demo_repos/shopcalc",
        "failing_test": "tests/test_shop.py::test_apply_discount_fifty_percent",
        "expected_verdict": "VERIFIED_FIXED",
        "description": "One-line percentage fix; isolated impact"
    },
    {
        "id": "billing_ripple",
        "repo": "demo_repos/billing_ripple",
        "failing_test": "tests/test_pricing.py::test_round_half_up_positive",
        "expected_verdict": "VERIFIED_FIXED",
        "description": "Banker's rounding fix; regression caught on refunds.py before success"
    },
    {
        "id": "scheduler_hard",
        "repo": "demo_repos/scheduler_hard",
        "failing_test": "tests/test_scheduler.py::test_corporate_founding_day_holiday",
        "expected_verdict": "UNFIXED",
        "description": "Missing business rule; honest UNFIXED after 3 attempts"
    }
]

def run_evaluation():
    print("=" * 65)
    print("EMEND EVALUATION HARNESS - RUNNING BUG MATRIX")
    print("=" * 65)

    results = []

    for case in EVAL_CASES:
        print(f"\n[EVAL] Running: {case['id']} ({case['description']})")
        logs = []
        def emit(ev):
            logs.append(ev)

        t_start = time.time()
        base_run = baseline(case["repo"], case["failing_test"], emit)
        impact = analyze_impact(case["repo"], case["failing_test"])
        report = repair(case["repo"], case["failing_test"], impact, emit)
        duration = round(time.time() - t_start, 2)

        verdict_match = (report.verdict == case["expected_verdict"])
        print(f" -> Verdict: {report.verdict} (Expected: {case['expected_verdict']}) | Match: {verdict_match}")
        print(f" -> Attempts used: {len(report.attempts)} | Time: {duration}s | Tokens: {report.metrics.get('tokens_total', 0)}")

        results.append({
            "id": case["id"],
            "repo": case["repo"],
            "description": case["description"],
            "expected_verdict": case["expected_verdict"],
            "actual_verdict": report.verdict,
            "passed": verdict_match,
            "attempts": len(report.attempts),
            "duration_s": duration,
            "tokens": report.metrics.get("tokens_total", 0),
            "residual_risks": len(report.residual_risk)
        })

    # Guardrail security test
    print("\n[EVAL] Testing Security Guardrail (Test File Tampering & Path Traversal)...")
    guardrail_caught = 0
    t1, _ = PatchApplier.check_guardrails(repo_root, PatchBlock("tests/test_foo.py", "a", "b"))
    if not t1:
        guardrail_caught += 1
    t2, _ = PatchApplier.check_guardrails(repo_root, PatchBlock("../../etc/shadow", "a", "b"))
    if not t2:
        guardrail_caught += 1
    print(f" -> Guardrail tests passed: {guardrail_caught}/2 attacks blocked.")

    # Save to eval/results/metrics.json
    os.makedirs(os.path.join(repo_root, "eval", "results"), exist_ok=True)
    metrics_path = os.path.join(repo_root, "eval", "results", "metrics.json")
    with open(metrics_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)

    # Generate Markdown Table for README
    md_table = [
        "\n### Automated Evaluation Results\n",
        "| Bug ID | Description | Expected | Actual | Attempts | Time (s) | Status |",
        "| :--- | :--- | :--- | :--- | :---: | :---: | :---: |"
    ]
    for r in results:
        status_icon = "✅ PASS" if r["passed"] else "❌ FAIL"
        md_table.append(
            f"| `{r['id']}` | {r['description']} | `{r['expected_verdict']}` | `{r['actual_verdict']}` | {r['attempts']} | {r['duration_s']}s | {status_icon} |"
        )
    md_content = "\n".join(md_table)

    summary_path = os.path.join(repo_root, "eval", "results", "summary.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print("\n" + md_content)
    print(f"\nSaved metrics to {metrics_path} and {summary_path}")

if __name__ == "__main__":
    run_evaluation()
