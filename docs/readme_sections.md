## How Emend Uses NVIDIA Nemotron

Emend integrates NVIDIA Nemotron models through the Nebius Token Factory OpenAI-compatible endpoint with task-specific model routing:

* **Root-Cause Analysis & Patch Synthesis (`nvidia/nemotron-3-super-120b-a12b`)**:
  - Leverages Nemotron Super's deep contextual reasoning to diagnose complex cross-module edge cases (e.g., banker's rounding edge-cases with symmetric Decimal math).
  - Emits strict `SEARCH/REPLACE` diff blocks that are deterministically applied and parsed without requiring malformed unified git diff syntax.
* **Fast Failure Triage & Classification (`nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`)**:
  - Low-latency classification of raw pytest tracebacks and test failure tails.
  - Generates human-readable summaries for the live dashboard timeline while conserving inference credits.

---

## The Proof Loop & Blast Radius Engine

Unlike traditional code assistants that rely on LLM self-evaluation, Emend combines static dependency analysis with deterministic three-tier execution:

1. **AST Reverse Reachability**: Builds an AST symbol table and a `networkx` directed graph of callers/callees across modules to identify every transitively affected node before modifying code.
2. **Three-Tier Verification**:
   - **Tier 1 (Target Test)**: Ensures the targeted failing assertion passes.
   - **Tier 2 (Blast Radius)**: Runs static-predicted dependent tests to detect collateral regressions immediately.
   - **Tier 3 (Full Suite Diff)**: Runs the baseline suite to diff outcomes against pre-repair passing states.
3. **Atomic Revert Policy**: If a patch fails any verification tier or causes a regression, git reverts the working tree to the baseline commit so failed attempts never stack.
4. **Code Guardrails**:
   - Strictly blocks patches modifying test files (`tests/`, `test_*.py`, `conftest.py`, or config files).
   - Validates AST syntax in memory before writing to disk.
   - Restricts all changes strictly within the repository root (anti-traversal).

---

## Evaluation Results

Automated benchmark evaluation across our demo test matrix (`eval/run_eval.py`):

| Bug ID | Benchmark Description | Target Verdict | Actual Verdict | Attempts | Duration | Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| `shopcalc_simple` | One-line percentage discount fix | `VERIFIED_FIXED` | `VERIFIED_FIXED` | 1 | 0.97s | ✅ PASS |
| `billing_ripple` | Banker's rounding fix; regression caught on refunds.py | `VERIFIED_FIXED` | `VERIFIED_FIXED` | 2 | 1.34s | ✅ PASS |
| `scheduler_hard` | Missing external holiday calendar contract | `UNFIXED` | `UNFIXED` | 3 | 0.43s | ✅ PASS |

*Note: In `billing_ripple`, Attempt 1's naive patch resolved the target test but triggered an immediate Tier 2 regression in `billing/refunds.py`. The agent detected the failure, reverted the tree, incorporated the regression trace into Attempt 2, and achieved `VERIFIED_FIXED`.*