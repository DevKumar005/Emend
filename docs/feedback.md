# Nebius Token Factory & NVIDIA Nemotron Feedback

Feedback compiled during the development and evaluation of Emend.

### 1. NVIDIA Nemotron Model Routing Observations
- **`nvidia/nemotron-3-super-120b-a12b`**:
  - *Strengths*: Exceptionally capable at extracting mathematical root causes (such as identifying banker's rounding edge-cases with negative numbers in financial calculations) and adhering to strict `SEARCH/REPLACE` indentation structures.
  - *Observation*: Reasoning tokens can be verbose. Having a dedicated delimiter separating internal chain-of-thought tokens from the final generation block improves parser determinism and reduces the need for custom client-side regex splitting.
- **`nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` / `Nemotron-3_5-Lightning`**:
  - *Strengths*: Very low time-to-first-token (TTFT). Ideal for summarizing pytest error tails and failure classification without burning token credits.

### 2. Nebius Token Factory API & Developer Experience
- **OpenAI SDK Compatibility**: The OpenAI drop-in compatibility via `https://api.tokenfactory.nebius.com/v1/` allowed zero-overhead client integration.
- **Model Catalog Discoverability**: Having `GET /v1/models` return verbose metadata is useful, but having model capabilities (e.g. context window limits, tool-calling support flags) returned directly in the endpoint response would speed up automated model routing.
- **Rate Limit & Error Clarity**: Providing token replenishment rates directly in HTTP response headers (`X-RateLimit-Reset-Tokens`) helps agentic loops dynamically calibrate backoff delays during iterative repair cycles.