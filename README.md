# Emend

> **Fix it. Prove it.**  
> An autonomous code-repair agent that verifies its own work and tells you honestly what remains risky.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Track: Coding and Agentic Engineering](https://img.shields.io/badge/Track-Coding%20%26%20Agentic%20Engineering-indigo.svg)](#)
[![Nebius Token Factory](https://img.shields.io/badge/Inference-Nebius%20Token%20Factory-purple.svg)](https://api.tokenfactory.nebius.com/v1/)
[![NVIDIA Nemotron](https://img.shields.io/badge/Model-NVIDIA%20Nemotron-76B900.svg)](#)

---

## The Problem

When developers patch a bug in a shared utility or service, another module that quietly depends on it often breaks. Today's AI coding assistants proclaim "fixed" based solely on whether their generated patch compiles or passes a single targeted unit test. They rarely test for collateral damage across the codebase.

Developers are left manually reading stack traces, guessing which downstream suites to run, and hoping no silent regressions slipped into production.

---

## What Emend Does

Given a repository and a failing test, **Emend**:

1. **Reproduces** the baseline failure in an isolated test runner.
2. **Predicts** collateral damage using an AST call-and-import graph (**Blast Radius Engine**).
3. **Proposes** a minimal, syntax-verified `SEARCH/REPLACE` patch using **NVIDIA Nemotron** via **Nebius Token Factory**.
4. **Verifies** deterministically across three execution tiers:
   - **Tier 1**: Targeted failing test
   - **Tier 2**: Impact-ranked downstream tests
   - **Tier 3**: Full test suite diffed against the baseline
5. **Rolls back** automatically if a patch passes the target test but breaks downstream code (the **"Ripple Catch"**), learning from the regression trace and trying again (up to 3 attempts).
6. **Reports** an honest verdict (`VERIFIED_FIXED`, `FIXED_WITH_REGRESSIONS`, `UNFIXED`, `INVALID_PATCH`), a downloadable `.patch`, and an explicit audit of **unverified residual risks** for functions with no test coverage.

---

## System Architecture

```
 +------------------------+   HTTP + SSE   +---------------------------------+
 | React Dashboard (Vite) | <------------> | FastAPI Monolith (Uvicorn)      |
 | Timeline | Graph       |                | routes, SQLite/in-memory store  |
 | Diff     | Results     |                +----------------+----------------+
 +------------------------+                                 |
                                             calls only through
                                             core/pipeline_api.py
                                                            |
                 +------------------------------------------+------------------------------------------+
                 |                                          |                                          |
        +--------v-------+                         +--------v-------+                         +--------v-------+
        |  Blast Radius  |                         |   Proof Loop   |                         |  Proof Runner  |
        |     Engine     |                         |     Agent      |                         | Subprocess/    |
        | AST graph,     |                         | Nemotron tool- |                         | Docker         |
        | test mapping   |                         | calling        |                         | Isolation      |
        +----------------+                         +--------+-------+                         +----------------+
                                                            |
                                              Nebius Token Factory
                                              NVIDIA Nemotron Super 120B / Nano 30B
```

### Core Components

* **Blast Radius Engine (`emend.core.impact`)**:
  - Parses AST across modules to construct a `networkx` directed graph of callers and callees.
  - Computes transitive reverse reachability from modified or target functions.
  - Automatically identifies and ranks downstream test suites covering dependent symbols.
* **Proof Loop Agent (`emend.core.agent`)**:
  - Implements multi-turn iterative repair with hard loop limits (maximum 3 attempts).
  - Uses strictly delimited, deterministic `SEARCH/REPLACE` patch blocks to prevent malformed diffs.
  - Features an **Atomic Revert Policy**: If any verification tier fails or introduces regressions, the working tree is immediately reverted to baseline, and the regression traceback is fed to the next attempt.
* **Deterministic Verification Cascade (`emend.core.runner`)**:
  - **Tier 1 (Target Test)**: Confirms the reported bug is fixed.
  - **Tier 2 (Blast Radius)**: Executes statically predicted dependent tests to catch collateral regressions immediately.
  - **Tier 3 (Full Suite Baseline Diff)**: Differs pass/fail outcomes against the pre-repair state to ensure no unrelated tests broke.
* **Residual Risk Engine (`emend.core.impact.risk`)**:
  - Discovers code paths in the blast radius that have zero test coverage.
  - Generates explicit residual risk warnings so developers know where unit tests must be added.
* **React Dashboard (`frontend/`)**:
  - Real-time execution stream powered by Server-Sent Events (SSE).
  - Interactive AST dependency graph with caller/callee inspection.
  - Unified patch inspector with side-by-side attempt diffs and model hypotheses.
  - Interactive proof loop simulator demonstrating regression recovery.

---

## How We Use NVIDIA Nemotron

We implement **credit-conscious model routing** via Nebius Token Factory:

| Task | Model | Rationale |
|---|---|---|
| **Root-Cause Analysis & Patch Synthesis** | `nvidia/nemotron-3-super-120b-a12b` | High-parameter reasoning model capable of analyzing multi-file call stacks and synthesizing structured `SEARCH/REPLACE` blocks. |
| **Fast Classification & Log Summaries** | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` | Ultra-fast, lightweight inference keeping latency and credit consumption minimal. |
| **Verification & Test Execution** | *Deterministic Program (no LLM)* | Exit codes and parsed pytest JSON reports are the ground truth—never an LLM's opinion. |

---

## Where Nebius Token Factory Helped

* **OpenAI-Compatible Drop-In API**: Token Factory's base URL (`https://api.tokenfactory.nebius.com/v1/`) allowed standard client libraries with instant configuration.
* **Cost & Token Transparency**: Token usage metrics (`tokens_in`, `tokens_out`, `tokens_total`) are tracked per attempt and surfaced directly in the UI header and final reports.
* **High Concurrency & Low Latency**: Smooth streaming for iterative repair loops and fast failure classification.

---

## Security Model & Guardrails

Emend executes repository code and applies patches with defense-in-depth:

| Threat | Code-Enforced Mitigation |
|---|---|
| **Test Tampering** | Patches modifying `tests/`, `test_*.py`, `conftest.py`, or pytest configs are immediately rejected as `INVALID_PATCH`. |
| **Prompt Injection** | Untrusted repository text and test logs are wrapped in strict delimiters (`=== BEGIN UNTRUSTED DATA ===`) and treated purely as data. |
| **Path Traversal** | Patched paths must resolve strictly within the repo root; symlinks and `../` escapes are blocked. |
| **Secret Leakage** | API keys live solely in backend environment variables. Test subprocesses execute in scrubbed environments with no leaked secrets. |
| **Runaway Loops** | Hard limits: 3 attempts maximum, per-job token budgets, and per-test execution timeouts. |

---

## Evaluation Results

Emend is benchmarked across bundled test suites representing one-line defects, multi-module regressions, and unresolvable business constraints (`eval/run_eval.py`):

| Benchmark Bug | Scenario Type | Baseline Repro | Initial Patch Result | Regression Caught? | Final Verdict | Attempts |
|---|---|:---:|:---:|:---:|:---:|:---:|
| `shopcalc` | Simple percentage defect | 100% | Target Passes | N/A (isolated) | `VERIFIED_FIXED` | 1 |
| `billing_ripple` | Ripple Catch (Rounding) | 100% | Target Passes, Refunds Fail | **Yes (Caught)** | `VERIFIED_FIXED` | 2 |
| `scheduler_hard` | Missing business calendar | 100% | Target Fails | N/A | `UNFIXED (Honest)` | 3 |

*In `billing_ripple`, Attempt 1's naive patch resolved the target pricing test but triggered an immediate Tier 2 regression in downstream `billing/refunds.py`. The agent detected the failure, reverted the working tree, incorporated the regression trace into Attempt 2, and verified a symmetric Decimal fix across all three tiers.*

---

## Repository Structure

```
Emend/
├── backend/
│   ├── emend/
│   │   ├── api/             # FastAPI routes, orchestrator, SSE events, store
│   │   │   ├── routes/      # analysis, demo, jobs, health
│   │   │   └── main.py      # App entry point & static SPA mounting
│   │   └── core/            # Intelligence engine & verification
│   │       ├── agent/       # Proof Loop agent, patching, model router, prompts
│   │       ├── impact/      # AST call-graph parser, risk analyzer, test mapper
│   │       ├── runner/      # Subprocess & Docker isolated pytest execution
│   │       ├── nebius_client.py # Nebius Token Factory client & simulation fallback
│   │       └── pipeline_api.py  # Public API interface
│   └── tests/               # Backend unit and API tests
├── contracts/               # Pydantic schemas & JSON fixture contracts
├── demo_repos/              # Bundled benchmark test suites
│   ├── billing_ripple/      # Ripple catch rounding regression demo
│   ├── scheduler_hard/      # Honest failure / missing contract demo
│   └── shopcalc/            # Simple single-attempt discount bug demo
├── eval/                    # Automated evaluation harness
│   ├── run_eval.py          # Benchmark test suite runner
│   └── results/             # Evaluation metrics and summaries
├── frontend/                # React 18 + TypeScript + Vite + Tailwind CSS dashboard
│   ├── src/
│   │   ├── components/      # UI components (Diff, Graph, Timeline, Simulator, etc.)
│   │   ├── pages/           # Dashboard & AnalysisDetails pages
│   │   ├── services/        # Backend API & SSE event stream client
│   │   └── types/           # Shared TypeScript interfaces
│   └── package.json
├── sandbox/                 # Dockerfile for isolated runner containers
├── Dockerfile               # Production multi-stage Docker build (Port 7860)
├── docker-compose.yml       # Local containerized orchestration
├── Makefile                 # Common developer commands
└── vercel.json              # Vercel deployment configuration
```

---

## Quickstart

### Prerequisites
- Python 3.11+
- Node.js 18+

### 1. Environment Setup

```bash
# Copy environment configuration
cp .env.example .env
```

> **Note on API Keys**: You do **not** need an API key to test Emend! If `NEBIUS_API_KEY` is not set, Emend runs in a high-fidelity intelligent simulation mode that lets you test all three demo scenarios immediately. When you add a valid `NEBIUS_API_KEY`, it routes live calls to Nebius Token Factory.

### 2. Backend Setup

```bash
# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install requirements
pip install -r backend/requirements.txt

# Run backend API server
PYTHONPATH=backend:. uvicorn emend.api.main:app --reload --port 8000
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173 (proxies /api to port 8000)
```

### 4. Running Benchmarks & Evaluations

```bash
# Run automated benchmark evaluation harness
PYTHONPATH=backend:. python eval/run_eval.py
```

### 5. Production Docker Deployment (Port 7860)

Emend includes a multi-stage `Dockerfile` that builds the React frontend and serves both the dashboard and API from a single container on port 7860 (Hugging Face Docker Space compliant):

```bash
docker build -t emend .
docker run --rm -p 7860:7860 --env-file .env emend
```

### 6. Deploy to Vercel

Emend includes native `vercel.json` configuration for one-click deployment:

1. Import the repository in [Vercel](https://vercel.com/new).
2. The root `vercel.json` automatically detects the Vite frontend, builds `frontend/dist`, and configures SPA rewrites.
3. Configure `VITE_API_URL` under Project Environment Variables to connect to your live backend.

---

## API Specification

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | `GET` | Health check and engine configuration status |
| `/api/demo-repos` | `GET` | List available demo repositories and scenarios |
| `/api/demo-repos/recorded-run/{id}` | `GET` | Retrieve pre-recorded benchmark run for instant replay |
| `/api/analysis` | `POST` | Launch an autonomous repair analysis on a target test |
| `/api/jobs/{id}` | `GET` | Query job status and metadata |
| `/api/jobs/{id}/events` | `GET` | Server-Sent Events (SSE) live execution stream |
| `/api/analysis/{id}/impact` | `GET` | Retrieve Blast Radius AST call graph and reachability |
| `/api/analysis/{id}/report` | `GET` | Retrieve final report, verdict, and residual risk audit |
| `/api/analysis/{id}/tests` | `GET` | Retrieve structured test run results across all tiers |

---

## Authors & Credits

Emend was created and engineered for the **Nebius x NVIDIA Global AI Hackathon** by:
* **Anurag Kumar** — [@anuragkumar80](https://github.com/anuragkumar80) (Platform Architecture, FastAPI Backend, Orchestrator & React Frontend)
* **Dev Kumar** — [@DevKumar005](https://github.com/DevKumar005) (Core Intelligence, Blast Radius Engine, Verification Loop & Benchmark Matrix)

---

## License

MIT License — Copyright (c) 2026 Anurag Kumar & Dev Kumar Sharma. See [LICENSE](LICENSE) for details.
