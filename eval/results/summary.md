
### Automated Evaluation Results

| Bug ID | Description | Expected | Actual | Attempts | Time (s) | Status |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| `shopcalc_simple` | One-line percentage fix; isolated impact | `VERIFIED_FIXED` | `VERIFIED_FIXED` | 1 | 0.85s | ✅ PASS |
| `billing_ripple` | Banker's rounding fix; regression caught on refunds.py before success | `VERIFIED_FIXED` | `FIXED_WITH_REGRESSIONS` | 3 | 0.7s | ❌ FAIL |
| `scheduler_hard` | Missing business rule; honest UNFIXED after 3 attempts | `UNFIXED` | `UNFIXED` | 3 | 0.34s | ✅ PASS |