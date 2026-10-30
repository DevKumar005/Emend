# Blast Radius Engine Architecture

The Blast Radius Engine predicts which parts of a codebase could break before full test suites are run.

## Analysis Pipeline
1. **AST Parsing & Symbol Table**:
   - Uses Python's built-in `ast` module to scan modules, classes, functions, line boundaries, and call invocations across the repository.
   - Builds fully-qualified symbol mappings (e.g., `billing.utils.round_price`).
2. **Reverse Reachability Graph**:
   - Builds a directed graph with `networkx` where nodes represent symbols and edges represent call/import relationships.
   - Inverts graph traversal to compute reverse reachability: determining all upstream callers transitively dependent on a target node.
3. **Static Test Ranking**:
   - Scores test suites by proximity to the affected symbols in the dependency graph.
   - Ranks the most relevant tests so that regressions are discovered in Tier 2 within seconds.
4. **Residual Risk Calculation**:
   - Identifies functions that are reachable from the change surface but lack associated automated tests.
   - Transparently flags untested components as unverified residual risk rather than claiming false safety.