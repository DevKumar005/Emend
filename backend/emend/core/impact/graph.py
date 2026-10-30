import networkx as nx
from typing import Dict, List, Set, Tuple
from contracts.schemas import NodeInfo, EdgeInfo
from emend.core.impact.parser import CodeSymbol, parse_repository_symbols

class DependencyGraph:
    def __init__(self, symbols: Dict[str, CodeSymbol]):
        self.symbols = symbols
        self.graph = nx.DiGraph()
        self._build_graph()

    def _build_graph(self):
        for name, sym in self.symbols.items():
            self.graph.add_node(name, symbol=sym)

        # Connect callers and callees
        for caller_name, caller_sym in self.symbols.items():
            for callee_target in caller_sym.calls:
                for target_name, target_sym in self.symbols.items():
                    if target_name.endswith(f".{callee_target}") or target_name == callee_target:
                        self.graph.add_edge(caller_name, target_name, kind="calls")

    def get_reverse_reachability(self, symbol_name: str) -> Set[str]:
        """Finds all symbols directly or transitively dependent on the changed symbol."""
        if symbol_name not in self.graph:
            matches = [n for n in self.graph.nodes if n.endswith(symbol_name)]
            if matches:
                symbol_name = matches[0]
            else:
                return set()

        rev_graph = self.graph.reverse(copy=False)
        try:
            return set(nx.descendants(rev_graph, symbol_name)) | {symbol_name}
        except Exception:
            return {symbol_name}

    def export_contract_views(self, impacted_symbols: Set[str]) -> Tuple[List[NodeInfo], List[EdgeInfo]]:
        nodes: List[NodeInfo] = []
        edges: List[EdgeInfo] = []

        for node_id in self.graph.nodes:
            sym: CodeSymbol = self.graph.nodes[node_id].get("symbol")
            if not sym:
                continue
            is_impacted = node_id in impacted_symbols
            nodes.append(NodeInfo(
                id=node_id,
                kind=sym.kind if sym.kind in ("module", "function", "class") else "function",  # type: ignore
                file=sym.file_path,
                lines=sym.lines,
                risk="high" if is_impacted else "low",
                label="predicted risk, unverified" if is_impacted else "not affected (predicted)"
            ))

        for u, v, data in self.graph.edges(data=True):
            edges.append(EdgeInfo(
                source=u,
                target=v,
                kind=data.get("kind", "calls")
            ))

        return nodes, edges

class DependencyGraphBuilder:
    """Class wrapper for backward compatibility."""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.symbols = parse_repository_symbols(repo_path)
        self.dep_graph = DependencyGraph(self.symbols)
        self.graph = self.dep_graph.graph

    def get_reverse_dependents(self, symbol_qname: str) -> Set[str]:
        return self.dep_graph.get_reverse_reachability(symbol_qname)

    def get_direct_callers(self, symbol_qname: str) -> List[str]:
        if symbol_qname not in self.graph:
            matches = [n for n in self.graph.nodes if n.endswith(symbol_qname)]
            if matches:
                symbol_qname = matches[0]
            else:
                return []
        return list(self.graph.predecessors(symbol_qname))

    def get_direct_callees(self, symbol_qname: str) -> List[str]:
        if symbol_qname not in self.graph:
            matches = [n for n in self.graph.nodes if n.endswith(symbol_qname)]
            if matches:
                symbol_qname = matches[0]
            else:
                return []
        return list(self.graph.successors(symbol_qname))
