# Emend

> **Fix it. Prove it.**  
> An autonomous code-repair agent that verifies its own work and tells you honestly what remains risky.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Track: Coding and Agentic Engineering](https://img.shields.io/badge/Track-Coding%20%26%20Agentic%20Engineering-indigo.svg)](#)
[![Nebius Token Factory](https://img.shields.io/badge/Inference-Nebius%20Token%20Factory-purple.svg)](https://api.tokenfactory.nebius.com/v1/)
[![NVIDIA Nemotron](https://img.shields.io/badge/Model-NVIDIA%20Nemotron-76B900.svg)](#)

---

## The Problem
Developers fix a bug in a shared utility function, and another module that quietly depends on it breaks. Today's AI coding assistants say "fixed", but they rarely test collateral damage. Developers are left manually reading stack traces, guessing which tests to run, and hoping no regressions slipped through.

## What Emend Does
Given a repository and a failing test, **Emend**:
1. **Reproduces** the baseline failure in an isolated test runner.
2. **Predicts** collateral damage using an AST call-and-import graph (**Blast Radius Engine**).
3. **Proposes** a minimal `SEARCH/REPLACE` patch using **NVIDIA Nemotron** via **Nebius Token Factory**.
4. **Verifies** in three tiers:
   - **Tier 1**: Target failing test
   - **Tier 2**: Impact-ranked downstream tests
   - **Tier 3**: Full test suite diffed against the baseline
5. **Rolls back** automatically if a patch passes the target test but breaks downstream code (the **"Ripple Catch"**), learning from the regression and trying again (up to 3 attempts).
6. **Reports** an honest verdict (`VERIFIED_FIXED`, `FIXED_WITH_REGRESSIONS`, `UNFIXED`, `INVALID_PATCH`), a downloadable `.patch`, and an explicit list of **unverified residual risks** for functions with no test coverage.

---

## System Architecture

```
 +------------------------+   HTTP + SSE   +---------------------------------+
 | React Dashboard (Vite) | <------------> | FastAPI Monolith (Uvicorn)      |
 | Timeline | Graph       |                | routes, SQLite, orchestrator    |
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

---

## How We Use NVIDIA Nemotron

We implement **credit-conscious model routing**:

| Task | Model | Rationale |
|---|---|---|
| **Root-Cause Analysis & Patching** | `nvidia/nemotron-3-super-120b-a12b` | High-parameter reasoning model capable of analyzing multi-file call stacks and synthesizing structured `SEARCH/REPLACE` blocks. |
| **Classification, Log Summaries, Reports** | `nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B` | Ultra-fast, lightweight inference keeping latency and credit consumption minimal. |
| **Verification & Test Execution** | *Deterministic Program (no LLM)* | Exit codes and parsed pytest JSON reports are the ground truth—never an LLM's opinion. |

---

## Where Nebius Token Factory Helped

- **OpenAI-Compatible Drop-In API**: Token Factory's base URL (`https://api.tokenfactory.nebius.com/v1/`) allowed standard client libraries with instant configuration.
- **Cost & Token Transparency**: Token usage metrics are surfaced directly in the Emend UI header and reports for complete accounting.
- **High Concurrency & Low Latency**: Smooth streaming for iterative repair loops.

---

## Security Model & Guardrails

Emend executes repository code and applies patches with defense-in-depth:

| Threat | Code-Enforced Mitigation |
|---|---|
| **Test Tampering** | Patches modifying `tests/`, `test_*.py`, `conftest.py`, or pytest configs are immediately rejected as `INVALID_PATCH`. |
| **Prompt Injection** | Untrusted repository text and test logs are wrapped in strict delimiters (`=== BEGIN UNTRUSTED DATA ===`) and declared as data. |
| **Path Traversal** | Patched paths must resolve strictly within the repo root; symlinks and `../` escapes are blocked. |
| **Secret Leakage** | API keys live solely in backend environment variables. Test subprocesses execute in scrubbed environments with no leaked secrets. |
| **Runaway Loops** | Hard limits: 3 attempts maximum, per-job token budgets, and per-test execution timeouts. |

---

## Evaluation Results

Evaluated across bundled test suites representing one-line defects, multi-module regressions, and unresolvable business constraints:

| Benchmark Bug | Scenario Type | Baseline Repro | Initial Patch Result | Regression Caught? | Final Verdict | Attempts |
|---|---|:---:|:---:|:---:|:---:|:---:|
| `shopcalc` | Simple percentage defect | 100% | Target Passes | N/A (isolated) | `VERIFIED_FIXED` | 1 |
| `billing_ripple` | Ripple Catch (Rounding) | 100% | Target Passes, Refunds Fail | **Yes (Caught)** | `VERIFIED_FIXED` | 2 |
| `scheduler_hard` | Missing business calendar | 100% | Target Fails | N/A | `UNFIXED (Honest)` | 3 |

---

## Quickstart

### Prerequisites
- Python 3.11+
- Node.js 18+
- Git

### 1. Clone & Setup
```bash
git clone https://github.com/DevKumar005/Emend.git
cd Emend

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

### 4. Single-Container Production Run (Port 7860)
Emend includes a multi-stage Dockerfile that builds the React frontend and serves both the dashboard and API from a single container on port 7860 (Hugging Face Docker Space compliant):
```bash
docker build -t emend .
docker run --rm -p 7860:7860 --env-file .env emend
```

---

## Authors & Credits

Emend was created and engineered for the **Nebius x NVIDIA Global AI Hackathon** by:
* **Anurag Kumar** — [@anuragkumar80](https://github.com/anuragkumar80) (Platform Architecture, FastAPI Backend, Orchestrator & React Frontend)
* **Dev Kumar** — [@DevKumar005](https://github.com/DevKumar005) (Core Intelligence, Blast Radius Engine, Verification Loop & Benchmark Matrix)

---

## License
MIT License - Copyright (c) 2026 Anurag Kumar & Dev Kumar Sharma. See [LICENSE](LICENSE) for details.
