# Emend Demo Video Script (Under 3 Minutes)

Target duration: 2:50. Designed for video screen recording at 1080p.

---

### Segment 1: The Problem (0:00 - 0:20)
- **On Screen**: Split screen with a naive code fix in `billing/utils.py` and downstream test failure in `tests/test_refunds.py`.
- **Voiceover**: *"Developers fix one bug and break something else. Most coding agents stop at 'here is a patch'. Emend is an autonomous code-repair agent that fixes the bug, runs an AST blast-radius graph to verify collateral damage, and honestly reports what remains risky."*

---

### Segment 2: Simple Bug Fix (0:20 - 1:00)
- **On Screen**: Dashboard. Select `shopcalc` demo repo. Click "Analyze & Prove Repair". Show real-time SSE Agent Timeline, AST graph generation, and single-attempt `VERIFIED_FIXED` green verdict.
- **Voiceover**: *"On a simple bug in shopcalc, Emend reproduces the failure, queries NVIDIA Nemotron on Nebius Token Factory, applies the minimal patch in an isolated sandbox, verifies the test passes, and proves the fix in a single attempt."*

---

### Segment 3: The Ripple Catch Headline Demo (1:00 - 1:55)
- **On Screen**: Switch to `billing_ripple`. Hit "Analyze & Prove Repair".
  - **Attempt 1**: Target test `test_round_half_up` passes, but the Blast Radius Engine runs `test_refund_negative_half` in `refunds.py` and catches a regression! The timeline turns amber/red.
  - **Revert Action**: Emend cleanly reverts the dirty working tree.
  - **Attempt 2**: Feeding regression feedback to Nemotron, Attempt 2 proposes symmetric Decimal `ROUND_HALF_UP`. All 3 tiers pass! Green `VERIFIED_FIXED` banner appears.
- **Voiceover**: *"Here is where Emend shines: the Ripple Catch. In billing_ripple, Attempt 1 passes the target test, but our Blast Radius Engine detects that it broke negative refunds downstream. Instead of blindly claiming victory, Emend detects the regression, reverts the working tree, and guides Nemotron to a symmetric Decimal fix that satisfies all callers."*

---

### Segment 4: Honest Failure Handling (1:55 - 2:20)
- **On Screen**: Run `scheduler_hard`. Show 3 attempts failing due to a missing external holiday calendar. Final verdict banner shows `UNFIXED (HONEST REPORT)` and lists residual risks.
- **Voiceover**: *"Emend does not hallucinate false success. On scheduler_hard, where external business calendar rules are missing from the repo, it tries three times, stops, and honestly reports UNFIXED with an exact list of unverified residual risks."*

---

### Segment 5: Architecture, Model Routing & Close (2:20 - 3:00)
- **On Screen**: Architecture diagram slide, evaluation results table (90% reproduction rate, 100% regression catch), and model routing chips (`nvidia/nemotron-3-super-120b-a12b` and `Nano 30B`).
- **Voiceover**: *"Emend routes complex reasoning to Nemotron 3 Super and fast summaries to Nano on Nebius Token Factory, pairing LLM intelligence with deterministic verification. Emend: Fix it. Prove it."*
