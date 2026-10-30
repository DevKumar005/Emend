# Proof Loop Agent Architecture & Specification

Emend's Proof Loop is an autonomous self-healing software repair agent powered by NVIDIA Nemotron via the Nebius Token Factory API.

## Core Principles
1. **Deterministic Verification Over LLM Self-Assessment**: An LLM is never asked if its code "looks right". Process return codes, pytest JSON reports, and unified git diffs are the sole determinants of repair success.
2. **Three-Tier Verification Cascade**:
   - **Tier 1 (Target Test)**: Ensures the targeted failing assertion or error is resolved.
   - **Tier 2 (Blast Radius Engine)**: Executes impacted dependent tests to detect regressions before expanding scope.
   - **Tier 3 (Full Test Suite)**: Runs the baseline suite to diff against pre-repair passing states.
3. **Strict Code Guardrails**:
   - **No Test Tampering**: Regex filters disallow modifications to files matching `tests/`, `test_*.py`, `conftest.py`, or test configurations.
   - **Path Traversal Protection**: Ensures patched paths resolve strictly inside repository root.
   - **Exact Context Matching**: `SEARCH/REPLACE` blocks must match uniquely within source files.
   - **AST Syntax Checking**: Python files are compiled into ASTs before any write operation; broken syntax immediately invalidates the patch without wasting test runs.
4. **Git Revert Policy**: Every failed attempt triggers a clean git working tree checkout. Patches never accidentally stack on top of prior failed edits.

## Operational Workflow

```
[Target Test Failure]
         |
         v
[Baseline Suite Run & Recording]
         |
         v
[AST Blast Radius Impact Prediction]
         |
         v
+----> [Attempt n (Max 3)]
|        |
|        v
|      [Nemotron Root-Cause Analysis & Patch Proposal]
|        |
|        v
|      [Code-Enforced Guardrails Validation]
|      (Reject test tampering, verify AST syntax, scope check)
|        |
|        v
|      [Tier 1: Execute Target Failing Test]
|        |-> Target Fails -> Record output, REVERT repo state -> Retry
|        |
|        v
|      [Tier 2: Execute Impact-Ranked Tests]
|        |-> Downstream Test Fails (Ripple Catch!) -> Record regression, REVERT -> Retry
|        |
|        v
|      [Tier 3: Full Suite Baseline Diff]
|        |-> New Failures Found -> Record regression, REVERT -> Retry
|        |
|        v
+----- [All 3 Tiers Pass -> VERIFIED_FIXED]
```
