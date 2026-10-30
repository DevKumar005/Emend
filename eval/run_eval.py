import os
import sys
import json
import time

# Ensure backend and repo root are importable
sys.path.insert(0, os.path.abspath("backend"))
sys.path.insert(0, os.path.abspath("."))

from emend.core.pipeline_api import baseline, analyze_impact, repair

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

    # Save to eval/results/metrics.json
    os.makedirs("eval/results", exist_ok=True)
    metrics_path = "eval/results/metrics.json"
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
    
    with open("eval/results/summary.md", "w", encoding="utf-8") as f:
        f.write(md_content)

    print("\n" + md_content)
    print(f"\nSaved metrics to {metrics_path} and eval/results/summary.md")

if __name__ == "__main__":
    run_evaluation()