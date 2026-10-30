import React, { useState } from 'react';
import { TestRun } from '../types';
import { CheckCircle2, XCircle, Terminal, ChevronDown, ChevronRight, Layers } from 'lucide-react';

interface TestResultsProps {
  runs: TestRun[];
}

export const TestResults: React.FC<TestResultsProps> = ({ runs }) => {
  const [expandedIndices, setExpandedIndices] = useState<Record<number, boolean>>({});
  const [activeScope, setActiveScope] = useState<'all' | 'target' | 'impacted' | 'full'>('all');

  const filteredRuns = (runs || []).filter(r => activeScope === 'all' || r.scope === activeScope);

  const toggleExpand = (idx: number) => {
    setExpandedIndices(prev => ({ ...prev, [idx]: !prev[idx] }));
  };

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-4 font-mono space-y-3.5">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2.5 pb-3 border-b border-slate-100 text-xs">
        <div className="flex items-center space-x-2">
          <Layers className="w-3.5 h-3.5 text-blue-600" />
          <span className="font-bold uppercase text-slate-800">
            Deterministic Verification Suites
          </span>
          <span className="text-slate-500 text-[11px]">
            ({runs?.length || 0} runs)
          </span>
        </div>

        <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded border border-slate-200 text-xs">
          {(['all', 'target', 'impacted', 'full'] as const).map(scope => (
            <button
              key={scope}
              onClick={() => setActiveScope(scope)}
              className={`px-2.5 py-1 rounded capitalize transition-colors ${
                activeScope === scope
                  ? 'bg-white text-slate-900 font-bold border border-slate-200 shadow-xs'
                  : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              {scope === 'all' ? 'All Tiers' : `${scope} Tier`}
            </button>
          ))}
        </div>
      </div>

      <div className="space-y-2">
        {filteredRuns.length === 0 ? (
          <div className="p-8 text-center text-slate-400 text-xs">
            No test runs recorded for the selected tier.
          </div>
        ) : (
          filteredRuns.map((run, idx) => {
            const isExpanded = !!expandedIndices[idx];
            const tests = run.tests || [];
            const passedCount = tests.filter(t => t.outcome === 'passed').length;
            const failedCount = tests.filter(t => t.outcome !== 'passed').length;
            const isSuccess = run.exit_code === 0 && failedCount === 0;

            return (
              <div
                key={idx}
                className="p-3 rounded bg-slate-50 border border-slate-200 hover:border-slate-300 transition-colors text-xs"
              >
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center space-x-2.5">
                    {isSuccess ? (
                      <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                    ) : (
                      <XCircle className="w-4 h-4 text-rose-600 flex-shrink-0" />
                    )}
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="font-bold text-slate-900 uppercase">
                          {run.scope} Scope
                        </span>
                        <span className={`px-1.5 py-0.5 rounded-full text-[10px] uppercase font-bold border ${
                          isSuccess
                            ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                            : 'bg-rose-50 text-rose-800 border-rose-300'
                        }`}>
                          {isSuccess ? 'PASS (0 REGRESSIONS)' : `${failedCount} FAILURES`}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-500 mt-0.5">
                        {passedCount} passed, {failedCount} failed · {run.duration_s || 0}s duration
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => toggleExpand(idx)}
                    className="flex items-center space-x-1 px-2 py-1 rounded bg-white hover:bg-slate-100 text-slate-700 text-[11px] border border-slate-200 transition-colors"
                  >
                    <Terminal className="w-3 h-3 text-slate-500" />
                    <span>{isExpanded ? 'Hide Output' : 'View Output'}</span>
                    {isExpanded ? <ChevronDown className="w-3 h-3" /> : <ChevronRight className="w-3 h-3" />}
                  </button>
                </div>

                {tests.length > 0 && (
                  <div className="mt-2.5 pt-2 border-t border-slate-200/80 space-y-1">
                    {tests.map((t, tIdx) => (
                      <div
                        key={tIdx}
                        className="flex flex-col sm:flex-row sm:items-center justify-between gap-1 px-2 py-1.5 rounded bg-white border border-slate-200 text-[10px] sm:text-[11px]"
                      >
                        <span className="break-all sm:truncate max-w-full sm:max-w-xl text-slate-700 font-mono" title={t.id}>
                          {t.id}
                        </span>
                        <span className={`self-start sm:self-auto px-1.5 py-0.5 rounded text-[9px] sm:text-[10px] uppercase font-bold flex-shrink-0 ${
                          t.outcome === 'passed' ? 'text-emerald-700 bg-emerald-50' : 'text-rose-700 bg-rose-50'
                        }`}>
                          {t.outcome}
                        </span>
                      </div>
                    ))}
                  </div>
                )}

                {isExpanded && (
                  <div className="mt-2.5 p-3 rounded bg-slate-900 text-slate-100 text-[11px] overflow-x-auto space-y-1 font-mono">
                    {run.command && (
                      <div className="text-slate-400">
                        <span className="text-slate-500 select-none">$ </span>
                        <span className="text-slate-200">{run.command}</span>
                      </div>
                    )}
                    <pre className="text-slate-300 whitespace-pre-wrap">
                      {run.output_tail || 'No output recorded.'}
                    </pre>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
