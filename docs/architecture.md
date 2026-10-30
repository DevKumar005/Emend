# Emend System Architecture

Emend is a modular monolith designed for deterministic automated code repair and blast-radius verification.

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

## Key Components

1. **Blast Radius Engine (`backend/emend/core/impact/`)**
   - AST Parser: Walks Python code, builds qualified symbol tables and import mapping.
   - NetworkX Dependency Graph: Maps functions, classes, and calls; computes reverse reachability (ancestors).
   - Test Mapper: Connects impacted symbols to pytest test cases with graph distance scoring.
   - Risk Analyzer: Evaluates heuristics and explicitly flags untested downstream code as **residual risk**.

2. **Proof Loop Agent (`backend/emend/core/agent/`)**
   - Nemotron Model Routing: Large 120B Super for reasoning/repair; 30B Nano for classification/summarization.
   - Guardrails: Path traversal rejection, AST syntax checking, and absolute prohibition against modifying test files.
   - 3-Tier Verification: Tier 1 Target Test -> Tier 2 Impact-Ranked Tests -> Tier 3 Full Suite Diff against baseline.
   - Revert Policy: Reverts dirty modifications between failed attempts so errors do not silently compound.

3. **Proof Runner (`backend/emend/core/runner/`)**
   - Isolated subprocess or local Docker with `--network none`.
   - Secret scrubbing: Child environment contains no API keys or parent process tokens.

4. **FastAPI & Event Stream (`backend/emend/api/`)**
   - SQLite backed persistence for jobs, test runs, events, and reports.
   - Server-Sent Events (SSE) streaming real-time diagnostic rationale and verification state.
