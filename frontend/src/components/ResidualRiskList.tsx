import React from 'react';
import { ResidualRisk } from '../types';
import { FileWarning, ShieldCheck } from 'lucide-react';

interface ResidualRiskListProps {
  risks: ResidualRisk[];
}

export const ResidualRiskList: React.FC<ResidualRiskListProps> = ({ risks }) => {
  return (
    <div className="bg-white rounded-lg border border-slate-200 p-4 font-mono space-y-3.5">
      <div className="flex items-center justify-between pb-2.5 border-b border-slate-100 text-xs">
        <div className="flex items-center space-x-2">
          <FileWarning className="w-3.5 h-3.5 text-amber-600" />
          <span className="font-bold uppercase text-slate-800">
            Residual Risk Audit
          </span>
        </div>
        <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-50 border border-amber-200 text-amber-800 font-bold">
          {risks?.length || 0} untested paths
        </span>
      </div>

      <p className="text-xs text-slate-600 font-sans leading-relaxed">
        Passing existing tests proves non-regression only within covered paths. Emend identifies downstream dependencies lacking unit tests to eliminate false confidence.
      </p>

      {(!risks || risks.length === 0) ? (
        <div className="p-3.5 rounded bg-emerald-50 border border-emerald-200 flex items-center space-x-2.5 text-emerald-800 text-xs">
          <ShieldCheck className="w-4 h-4 text-emerald-600 flex-shrink-0" />
          <span className="font-sans font-medium">
            Complete test coverage: Every function in the blast radius has unit tests in this repository.
          </span>
        </div>
      ) : (
        <div className="space-y-2">
          {risks.map((r, idx) => (
            <div
              key={idx}
              className="p-3 rounded bg-slate-50 border border-slate-200 text-xs space-y-1"
            >
              <div className="flex items-center justify-between gap-2">
                <span className="text-amber-800 font-bold">{r.symbol}</span>
                <span className="text-[10px] text-slate-500 px-1.5 py-0.5 rounded bg-white border border-slate-200">
                  {r.file}
                </span>
              </div>
              <p className="text-slate-700 font-sans text-xs">
                {r.reason}
              </p>
              <div className="text-[10px] text-slate-500 pt-0.5">
                <span>Callers affected: {r.callers_count || 1} · Action: Add regression test</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
