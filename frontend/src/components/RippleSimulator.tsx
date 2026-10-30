import React, { useState } from 'react';
import { Play, RotateCcw, CheckCircle2, AlertTriangle, GitFork, Check, FileCode } from 'lucide-react';

export const RippleSimulator: React.FC = () => {
  const [step, setStep] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);

  const steps = [
    {
      title: 'Baseline Failure',
      stageBadge: 'Failing Baseline',
      desc: 'Buggy banker rounding in utils.round_price() fails target pricing test.',
      pricingState: 'fail',
      refundsState: 'idle',
      pricingValue: 'round(2.675, 2) == 2.67 (Fail, expected 2.68)',
      refundsValue: 'Not evaluated yet',
      rootFormula: 'return round(x, 2)',
      action: 'Baseline Reproduced: Target test failing in isolated pytest runner.'
    },
    {
      title: 'Attempt 1: Naive Fix',
      stageBadge: 'Regression Caught',
      desc: 'Naive half-up int(x*100+0.5)/100 passes pricing, but causes downstream regression in refunds.py!',
      pricingState: 'pass',
      refundsState: 'fail',
      pricingValue: 'round(2.675, 2) == 2.68 (Target Passed)',
      refundsValue: 'compute_refund(-2.675) == -2.67 (Expected -2.68)',
      rootFormula: 'return int(x * 100 + 0.5) / 100.0',
      action: 'Blast Radius Engine catches regression in refunds.py tier.'
    },
    {
      title: 'Auto-Rollback',
      stageBadge: 'Git Revert',
      desc: 'Emend immediately executes Git rollback to restore clean baseline working tree.',
      pricingState: 'fail',
      refundsState: 'idle',
      pricingValue: 'Reverted to baseline',
      refundsValue: 'Working tree clean',
      rootFormula: 'git checkout -- . (Working tree restored)',
      action: 'Regression feedback recorded. Agent discards broken patch.'
    },
    {
      title: 'Attempt 2: Verified Fix',
      stageBadge: 'Verified Fixed',
      desc: 'Symmetric Decimal ROUND_HALF_UP passes target test AND preserves downstream refunds.',
      pricingState: 'pass',
      refundsState: 'pass',
      pricingValue: 'round(2.675, 2) == 2.68 (Pass)',
      refundsValue: 'compute_refund(-2.675) == -2.68 (Pass)',
      rootFormula: 'return float(Decimal(str(x)).quantize(..., ROUND_HALF_UP))',
      action: 'All 3 Tiers verified: Target test, blast radius, and full test suite.'
    }
  ];

  const handlePlaySimulation = () => {
    setIsPlaying(true);
    setStep(0);
    let s = 0;
    const interval = setInterval(() => {
      s += 1;
      if (s < steps.length) {
        setStep(s);
      } else {
        clearInterval(interval);
        setIsPlaying(false);
      }
    }, 2200);
  };

  const curr = steps[step];

  return (
    <div className="bg-white rounded-lg border border-slate-200 p-4 sm:p-5 shadow-2xs space-y-4">
      
      {/* Top Header & Simulation Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div className="flex items-center space-x-2.5">
          <div className="w-7 h-7 rounded bg-slate-100 border border-slate-200 flex items-center justify-center flex-shrink-0">
            <GitFork className="w-4 h-4 text-slate-700" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-xs sm:text-sm font-bold text-slate-900 font-mono">
                Verification Pipeline & Rollback Flow
              </span>
              <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold uppercase ${
                step === 1 ? 'bg-rose-50 text-rose-700 border border-rose-200' :
                step === 3 ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' :
                step === 2 ? 'bg-blue-50 text-blue-700 border border-blue-200' :
                'bg-slate-100 text-slate-700 border border-slate-200'
              }`}>
                {curr.stageBadge}
              </span>
            </div>
            <span className="text-[11px] text-slate-500 hidden sm:block">
              Demonstrates regression detection on downstream dependents and automatic recovery
            </span>
          </div>
        </div>

        {/* Action Controls */}
        <div className="flex items-center space-x-2 self-end sm:self-auto">
          <button
            onClick={handlePlaySimulation}
            disabled={isPlaying}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded bg-slate-900 hover:bg-slate-800 text-white text-xs font-mono font-medium shadow-2xs transition disabled:opacity-50"
          >
            <Play className="w-3 h-3 fill-white" />
            <span>{isPlaying ? 'Running Flow...' : 'Run Flow'}</span>
          </button>
        </div>
      </div>

      {/* Structured Pipeline Steps Scrubber */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
        {steps.map((st, i) => {
          const isActive = i === step;
          return (
            <button
              key={i}
              onClick={() => setStep(i)}
              className={`p-2 rounded border text-left transition font-mono ${
                isActive
                  ? 'border-blue-600 bg-blue-50/30 ring-1 ring-blue-600'
                  : 'border-slate-200 bg-slate-50/50 hover:bg-slate-100/60 text-slate-600'
              }`}
            >
              <div className="flex items-center justify-between text-[10px] mb-0.5">
                <span className={`font-semibold ${isActive ? 'text-blue-700' : 'text-slate-500'}`}>
                  Stage {i + 1}
                </span>
                {i === 1 && <span className="text-[9px] text-rose-600 font-semibold hidden md:inline">Caught</span>}
                {i === 2 && <span className="text-[9px] text-blue-600 font-semibold hidden md:inline">Reverted</span>}
                {i === 3 && <span className="text-[9px] text-emerald-600 font-semibold hidden md:inline">Pass</span>}
              </div>
              <div className="text-[11px] font-semibold text-slate-900 truncate">
                {st.title.split(':')[0]}
              </div>
            </button>
          );
        })}
      </div>

      {/* 3 Step Structured Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 font-mono text-xs items-stretch">
        
        {/* Tier 1: Target Test */}
        <div className={`p-3 rounded border flex flex-col justify-between ${
          curr.pricingState === 'pass'
            ? 'bg-emerald-50/40 border-emerald-300 text-emerald-950'
            : 'bg-rose-50/40 border-rose-300 text-rose-950'
        }`}>
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[10px] font-bold uppercase text-slate-600">Tier 1: Target Test</span>
              {curr.pricingState === 'pass' ? (
                <CheckCircle2 className="w-4 h-4 text-emerald-600" />
              ) : (
                <AlertTriangle className="w-4 h-4 text-rose-600" />
              )}
            </div>
            <div className="font-bold text-xs text-slate-900 truncate">
              tests/test_pricing.py
            </div>
          </div>

          <div className="mt-2.5 pt-2 border-t border-slate-200/60 text-[11px] leading-tight">
            <span className="text-slate-500 block mb-0.5 text-[10px]">Pytest Assertion:</span>
            <span className="font-semibold">{curr.pricingValue}</span>
          </div>
        </div>

        {/* Center: Defect Root Function */}
        <div className="p-3 rounded border bg-slate-50 border-slate-200 text-slate-800 flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[10px] font-bold uppercase text-slate-600">Defect Symbol</span>
              <span className="text-[9px] px-1.5 py-0.2 rounded bg-slate-200 text-slate-700 font-semibold">
                Modified
              </span>
            </div>
            <div className="font-bold text-xs text-slate-900 truncate">
              billing/utils.py::round_price()
            </div>
          </div>

          <div className="mt-2.5 pt-2 border-t border-slate-200/60 text-[11px] leading-tight">
            <span className="text-slate-500 block mb-0.5 text-[10px]">Applied Formula:</span>
            <span className="font-semibold text-slate-900 break-all">{curr.rootFormula}</span>
          </div>
        </div>

        {/* Tier 2: Downstream Dependent */}
        <div className={`p-3 rounded border flex flex-col justify-between ${
          curr.refundsState === 'pass'
            ? 'bg-emerald-50/40 border-emerald-300 text-emerald-950'
            : curr.refundsState === 'fail'
            ? 'bg-rose-50/60 border-rose-300 text-rose-950'
            : 'bg-slate-50 border-slate-200 text-slate-700'
        }`}>
          <div>
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[10px] font-bold uppercase text-slate-600">Tier 2: Blast Radius</span>
              {curr.refundsState === 'pass' && <CheckCircle2 className="w-4 h-4 text-emerald-600" />}
              {curr.refundsState === 'fail' && <AlertTriangle className="w-4 h-4 text-rose-600" />}
            </div>
            <div className="font-bold text-xs text-slate-900 truncate">
              billing/refunds.py (Dependent)
            </div>
          </div>

          <div className="mt-2.5 pt-2 border-t border-slate-200/60 text-[11px] leading-tight">
            <span className="text-slate-500 block mb-0.5 text-[10px]">Regression Status:</span>
            <span className={`font-semibold ${curr.refundsState === 'fail' ? 'text-rose-700' : ''}`}>
              {curr.refundsValue}
            </span>
          </div>
        </div>

      </div>

      {/* Action Summary Bar */}
      <div className="bg-slate-50 p-2.5 rounded border border-slate-200 text-xs font-mono">
        <div className="text-[11px] text-slate-700">
          <span className="font-bold text-slate-900">{curr.title}: </span>
          <span>{curr.action}</span>
        </div>
      </div>

    </div>
  );
};
