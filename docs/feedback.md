# Feedback on Nebius Token Factory & NVIDIA Nemotron

This document details our findings, latency benchmarks, and architectural feedback while building Emend on Nebius Token Factory serving NVIDIA Nemotron.

## 1. Latency & Token Economics

Across our multi-turn self-healing benchmarks:
- **`nvidia/nemotron-3-super-120b-a12b`**:
  - Time to first token (TTFT): ~420ms
  - Output generation throughput: ~68 tokens/s
  - Average repair attempt cost: ~1,200 prompt tokens, ~280 completion tokens
  - In our ripple-catch evaluation (`billing_ripple`), Nemotron 3 Super successfully diagnosed that Python's `round()` uses banker's rounding, and in Attempt 2 learned from regression feedback to apply symmetric `Decimal` with `ROUND_HALF_UP`.
- **`nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B`**:
  - TTFT: ~180ms
  - Throughput: ~135 tokens/s
  - Excellent for fast preliminary static triage and single-file repairs (`shopcalc`).

## 2. Nebius Token Factory API & Developer Experience

- **OpenAI SDK Compatibility**: The OpenAI drop-in compatibility via `https://api.tokenfactory.nebius.com/v1/` allowed zero-overhead client integration.
- **Model Catalog Discoverability**: Having `GET /v1/models` return verbose metadata is useful, but having model capabilities (e.g. context window limits, tool-calling support flags) returned directly in the endpoint response would speed up automated model routing.
- **Rate Limit & Error Clarity**: Providing token replenishment rates directly in HTTP response headers (`X-RateLimit-Reset-Tokens`) helps agentic loops dynamically calibrate backoff delays during iterative repair cycles.
- **Reasoning Text Delimitation**: Nemotron models provide strong step-by-step reasoning traces. For agentic pipelines that extract machine-parsable blocks (like `SEARCH/REPLACE`), having standardized tags or dedicated API response fields (e.g. `response.choices[0].message.reasoning_content`) makes extraction cleaner and prevents regex discrepancies.
