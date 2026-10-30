# Blast Radius Engine Architecture

The Blast Radius Engine predicts which parts of a codebase could break before full test suites are run.

## Core Principle: Predicted vs Verified

A passing test suite does not prove no regressions exist. Emend therefore strictly separates static predictions from deterministic test evidence:

| Label | Meaning | Color in UI |
|---|---|---|
| **Verified pass** | A test that exercises this code ran and passed after the patch | Green |
| **Verified fail** | A test ran and failed (a real regression or original defect) | Red |
| **Predicted risk, unverified** | Static AST analysis shows this code depends on the change, but no test exercised it | Amber |
| **Not affected (predicted)** | No dependency path from the changed code found in AST | Grey |

## Analysis Pipeline
1. **AST Parsing & Symbol Table (`parser.py`)**:
   - Uses Python's built-in `ast` module to scan modules, classes, functions, line boundaries, and call invocations across the repository.
   - Builds fully-qualified symbol mappings (e.g., `billing.utils.round_price`).
2. **Reverse Reachability Graph (`graph.py`)**:
   - Builds a directed graph with `networkx` where nodes represent symbols and edges represent call/import relationships.
   - Inverts graph traversal to compute reverse reachability: determining all upstream callers transitively dependent on a target node.
3. **Static Test Ranking (`test_mapper.py`)**:
   - Scores test suites by proximity to the affected symbols in the dependency graph.
   - Ranks the most relevant tests so that regressions are discovered in Tier 2 within seconds.
4. **Residual Risk Calculation (`risk.py`)**:
   - Identifies functions that are reachable from the change surface but lack associated automated tests.
   - Transparently flags untested components as unverified residual risk rather than claiming false safety.
