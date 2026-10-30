import React, { useState } from 'react';
import { CheckCircle2, AlertTriangle, XCircle, ShieldAlert, Download, Clock, Cpu, RotateCcw, Copy, Check } from 'lucide-react';
import { FinalReport } from '../types';

interface VerdictBannerProps {
  report: FinalReport;
  jobId: string;
}

export const VerdictBanner: React.FC<VerdictBannerProps> = ({ report, jobId }) => {
  const { verdict, metrics, patch, attempts } = report;
  const [copied, setCopied] = useState(false);

  const handleDownloadPatch = () => {
    if (!patch) return;
    const blob = new Blob([patch], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `emend_repair_${jobId}.patch`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleCopyPatch = () => {
    if (!patch) return;
    navigator.clipboard.writeText(patch);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getVerdictConfig = () => {
    switch (verdict) {
      case 'VERIFIED_FIXED':
        return {
          icon: CheckCircle2,
          color: 'text-emerald-600',
          border: 'border-emerald-300 bg-white',
          badge: 'bg-emerald-100 text-emerald-800 border-emerald-300',
          title: 'VERIFIED FIXED',
          desc: 'Target defect fixed. All blast-radius tests and full test suites pass.'
        };
      case 'FIXED_WITH_REGRESSIONS':
        return {
          icon: AlertTriangle,
          color: 'text-amber-600',
          border: 'border-amber-300 bg-white',
          badge: 'bg-amber-100 text-amber-800 border-amber-300',
          title: 'FIXED WITH REGRESSIONS',
          desc: 'Target passed, but downstream dependent tests caught regressions.'
        };
      case 'UNFIXED':
        return {
          icon: XCircle,
          color: 'text-slate-600',
          border: 'border-slate-300 bg-white',
          badge: 'bg-slate-100 text-slate-700 border-slate-300',
          title: 'UNFIXED (HONEST)',
          desc: 'Missing business context; halted safely after maximum attempts.'
        };
      case 'INVALID_PATCH':
      default:
        return {
          icon: ShieldAlert,
          color: 'text-purple-600',
          border: 'border-purple-300 bg-white',
          badge: 'bg-purple-100 text-purple-800 border-purple-300',
          title: 'GUARDRAIL BLOCKED',
          desc: 'Patch rejected by integrity guardrails.'
        };
    }
  };

  const cfg = getVerdictConfig();
  const Icon = cfg.icon;
  const regressionsCaught = attempts.filter(a => a.regressions && a.regressions.length > 0).length;

  return (
    <div className={`p-4 rounded-lg border ${cfg.border} text-slate-800 font-mono`}>
      <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-3">
        <div className="flex items-start sm:items-center space-x-2.5 sm:space-x-3">
          <div className="p-2 rounded bg-slate-50 border border-slate-200 flex-shrink-0 mt-0.5 sm:mt-0">
            <Icon className={`w-5 h-5 ${cfg.color}`} />
          </div>
          <div className="min-w-0">
            <div className="flex flex-wrap items-center gap-1.5 mb-0.5">
              <span className={`px-2 py-0.5 rounded text-[10px] sm:text-xs font-bold uppercase tracking-wider border ${cfg.badge}`}>
                {cfg.title}
              </span>
              <span className="text-xs text-slate-500 font-mono">Job #{jobId}</span>
              {regressionsCaught > 0 && (
                <span className="px-2 py-0.5 rounded text-[10px] bg-amber-50 text-amber-800 border border-amber-200 font-semibold">
                  {regressionsCaught} regression recovered
                </span>
              )}
            </div>
            <p className="text-xs text-slate-600 font-sans break-words leading-relaxed">
              {cfg.desc}
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-center gap-2 sm:gap-2.5 text-xs">
          <div className="flex flex-wrap items-center gap-2 bg-slate-50 px-3 py-1.5 rounded border border-slate-200 text-xs">
            <div className="flex items-center space-x-1 text-slate-700">
              <Clock className="w-3.5 h-3.5 text-slate-500" />
              <span>{metrics?.time_s || 0}s</span>
            </div>
            <span className="text-slate-300">·</span>
            <div className="flex items-center space-x-1 text-slate-700">
              <Cpu className="w-3.5 h-3.5 text-slate-500" />
              <span>{metrics?.tokens_total || 0} tok</span>
            </div>
            <span className="text-slate-300">·</span>
            <div className="flex items-center space-x-1 text-slate-700">
              <RotateCcw className="w-3.5 h-3.5 text-slate-500" />
              <span>{attempts?.length || 1} att</span>
            </div>
          </div>

          {patch && (
            <div className="flex items-center space-x-1.5 w-full sm:w-auto">
              <button
                onClick={handleCopyPatch}
                className="flex-1 sm:flex-none px-2.5 py-1.5 rounded bg-white hover:bg-slate-50 text-slate-700 border border-slate-200 text-xs flex items-center justify-center space-x-1 transition-colors active:scale-[0.98] focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-slate-600"
              >
                {copied ? <Check className="w-3.5 h-3.5 text-emerald-600" /> : <Copy className="w-3.5 h-3.5 text-slate-500" />}
                <span>{copied ? 'Copied' : 'Copy'}</span>
              </button>

              <button
                onClick={handleDownloadPatch}
                className="flex-1 sm:flex-none px-3 py-1.5 rounded bg-slate-900 hover:bg-slate-800 text-white font-semibold text-xs flex items-center justify-center space-x-1 transition-colors active:scale-[0.98] focus-visible:outline-2 focus-visible:outline-offset-1 focus-visible:outline-slate-900"
              >
                <Download className="w-3.5 h-3.5" />
                <span>Download Patch</span>
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
