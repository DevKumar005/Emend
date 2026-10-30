
### Automated Evaluation Results

| Bug ID | Description | Expected | Actual | Attempts | Time (s) | Status |
| :--- | :--- | :--- | :--- | :---: | :---: | :---: |
| `shopcalc_simple` | One-line percentage fix; isolated impact | `VERIFIED_FIXED` | `VERIFIED_FIXED` | 1 | 0.97s | ✅ PASS |
| `billing_ripple` | Banker's rounding fix; regression caught on refunds.py before success | `VERIFIED_FIXED` | `VERIFIED_FIXED` | 2 | 1.34s | ✅ PASS |
| `scheduler_hard` | Missing business rule; honest UNFIXED after 3 attempts | `UNFIXED` | `UNFIXED` | 3 | 0.43s | ✅ PASS |