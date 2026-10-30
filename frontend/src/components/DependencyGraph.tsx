import React, { useState } from 'react';
import { ImpactReport, ImpactNode } from '../types';
import { GitFork, Info } from 'lucide-react';

interface DependencyGraphProps {
  impact: ImpactReport;
}

export const DependencyGraph: React.FC<DependencyGraphProps> = ({ impact }) => {
  const [selectedNode, setSelectedNode] = useState<ImpactNode | null>(
    impact.nodes?.length ? impact.nodes[0] : null
  );

  const getNodeBadge = (label: string) => {
    switch (label) {
      case 'verified pass':
        return {
          border: 'border-emerald-300 bg-emerald-50/70 text-emerald-800',
          dot: 'bg-emerald-500',
          text: 'Verified Pass'
        };
      case 'verified fail':
        return {
          border: 'border-rose-300 bg-rose-50/70 text-rose-800',
          dot: 'bg-rose-500',
          text: 'Verified Fail'
        };
      case 'predicted risk, unverified':
        return {
          border: 'border-amber-300 bg-amber-50/70 text-amber-800',
          dot: 'bg-amber-500',
          text: 'Untested Risk'
        };
      case 'not affected (predicted)':
      default:
        return {
          border: 'border-slate-200 bg-slate-50 text-slate-700',
          dot: 'bg-slate-400',
          text: 'Unaffected'
        };
    }
  };

  const callers = selectedNode
    ? impact.edges.filter(e => e.target === selectedNode.id).map(e => e.source)
    : [];

  const callees = selectedNode
    ? impact.edges.filter(e => e.source === selectedNode.id).map(e => e.target)
    : [];

  return (
    <div className="bg-white rounded-xl border border-slate-200 flex flex-col h-[520px] shadow-sm">
      
      {/* Header & Graph Legend */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-3.5 border-b border-slate-200 bg-slate-50/70 text-xs rounded-t-xl">
        <div className="flex items-center space-x-2">
          <GitFork className="w-3.5 h-3.5 text-blue-600" />
          <span className="font-mono font-bold uppercase text-slate-800">
            Blast Radius Call Graph
          </span>
          <span className="font-mono text-[10px] text-slate-500 px-1.5 py-0.5 rounded bg-white border border-slate-200">
            {impact.nodes?.length || 0} nodes
          </span>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap items-center gap-1.5 font-mono text-[10px]">
          <span className="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
            <span>Pass</span>
          </span>
          <span className="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded-full bg-rose-50 border border-rose-200 text-rose-800 font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-rose-500" />
            <span>Fail</span>
          </span>
          <span className="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded-full bg-amber-50 border border-amber-200 text-amber-800 font-semibold">
            <span className="w-1.5 h-1.5 rounded-full bg-amber-500" />
            <span>Untested Risk</span>
          </span>
          <span className="inline-flex items-center space-x-1 px-1.5 py-0.5 rounded-full bg-slate-100 border border-slate-200 text-slate-600">
            <span className="w-1.5 h-1.5 rounded-full bg-slate-400" />
            <span>Unaffected</span>
          </span>
        </div>
      </div>

      {/* Main Workspace */}
      <div className="flex-1 flex flex-col md:flex-row overflow-hidden">
        
        {/* Node Grid View */}
        <div className="flex-1 overflow-y-auto p-3 space-y-2 border-b md:border-b-0 md:border-r border-slate-200 font-mono text-xs">
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {(impact.nodes || []).map((node) => {
              const cfg = getNodeBadge(node.label);
              const isSelected = selectedNode?.id === node.id;
              const isRootDefect = (impact.changed_symbols || []).includes(node.id);

              return (
                <div
                  key={node.id}
                  onClick={() => setSelectedNode(node)}
                  className={`cursor-pointer p-3 rounded-lg border text-left transition-all ${
                    isSelected
                      ? 'bg-blue-50/50 border-blue-500 shadow-xs ring-1 ring-blue-500'
                      : 'bg-white hover:bg-slate-50 border-slate-200'
                  }`}
                >
                  <div className="flex items-start justify-between gap-1 mb-1.5">
                    <div className="flex items-center space-x-1.5 min-w-0">
                      <span className={`w-2 h-2 rounded-full flex-shrink-0 ${cfg.dot}`} />
                      <span className="font-bold text-slate-900 truncate text-[11px]" title={node.id}>
                        {node.id.split('.').pop()}
                      </span>
                    </div>

                    {isRootDefect && (
                      <span className="text-[9px] px-1.5 py-0.2 rounded-full bg-slate-100 text-slate-700 border border-slate-300 uppercase font-bold flex-shrink-0">
                        Root
                      </span>
                    )}
                  </div>

                  <div className="text-[11px] text-slate-500 truncate mb-2">
                    {node.file}
                  </div>

                  <div className="flex items-center justify-between text-[10px] pt-1.5 border-t border-slate-100">
                    <span className={`px-1.5 py-0.5 rounded border uppercase font-bold ${cfg.border}`}>
                      {cfg.text}
                    </span>
                    <span className="text-slate-500 capitalize">Risk: {node.risk}</span>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="p-2.5 rounded-lg bg-slate-50 border border-slate-200 text-[11px] text-slate-600 flex items-start space-x-2 mt-2 font-sans">
            <Info className="w-3.5 h-3.5 text-blue-600 flex-shrink-0 mt-0.5" />
            <p className="leading-relaxed">
              Static AST reachability maps cross-module callers. Nodes with <strong className="text-amber-700">Untested Risk</strong> lack test coverage in this repo.
            </p>
          </div>
        </div>

        {/* Selected Node Inspector Sidebar */}
        <div className="w-full md:w-72 bg-slate-50/60 p-4 flex flex-col justify-between overflow-y-auto font-mono text-xs space-y-3">
          {selectedNode ? (
            <div className="space-y-3">
              <div>
                <span className="text-[10px] uppercase text-slate-500 font-bold">Selected Symbol</span>
                <h4 className="font-bold text-slate-900 text-xs break-all mt-0.5">
                  {selectedNode.id}
                </h4>
              </div>

              <div className="space-y-1.5 text-xs bg-white p-2.5 rounded-lg border border-slate-200">
                <div className="flex justify-between py-0.5 border-b border-slate-100 text-slate-600">
                  <span>File:</span>
                  <span className="text-slate-900 truncate max-w-[140px]" title={selectedNode.file}>
                    {selectedNode.file}
                  </span>
                </div>
                <div className="flex justify-between py-0.5 border-b border-slate-100 text-slate-600">
                  <span>Kind:</span>
                  <span className="text-slate-900 capitalize">{selectedNode.kind}</span>
                </div>
                <div className="flex justify-between py-0.5 border-b border-slate-100 text-slate-600">
                  <span>Risk:</span>
                  <span className="text-slate-900 uppercase font-semibold">{selectedNode.risk}</span>
                </div>
                <div className="flex justify-between py-0.5 text-slate-600">
                  <span>Proof:</span>
                  <span className="text-slate-900 uppercase font-semibold">{selectedNode.label}</span>
                </div>
              </div>

              {/* Callers */}
              <div>
                <span className="text-[10px] uppercase text-slate-500 font-bold block mb-1">
                  Downstream Callers ({callers.length})
                </span>
                {callers.length === 0 ? (
                  <span className="text-slate-400 text-[11px] italic">No callers in AST</span>
                ) : (
                  <div className="space-y-1">
                    {callers.map((c, i) => (
                      <div key={i} className="p-1.5 rounded bg-white border border-slate-200 text-[11px] text-slate-800 truncate" title={c}>
                        {c}
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Callees */}
              <div>
                <span className="text-[10px] uppercase text-slate-500 font-bold block mb-1">
                  Calls ({callees.length})
                </span>
                {callees.length === 0 ? (
                  <span className="text-slate-400 text-[11px] italic">No outward calls</span>
                ) : (
                  <div className="space-y-1">
                    {callees.map((c, i) => (
                      <div key={i} className="p-1.5 rounded bg-white border border-slate-200 text-[11px] text-slate-800 truncate" title={c}>
                        {c}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ) : (
            <div className="text-slate-400 text-xs italic">
              Click a node to inspect dependencies
            </div>
          )}

          <div className="pt-2 border-t border-slate-200 text-[10px] text-slate-400">
            <span>AST Reachability Engine</span>
          </div>
        </div>

      </div>

    </div>
  );
};
