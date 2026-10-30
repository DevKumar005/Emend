import React, { useRef } from 'react';
import { DemoRepoInfo, AnalysisRequest } from '../types';
import { RepositoryForm } from '../components/RepositoryForm';
import { RippleSimulator } from '../components/RippleSimulator';
import {
  CheckCircle2,
  RotateCcw,
  GitFork,
  Cpu,
  ShieldCheck,
  AlertTriangle,
  Play,
  ArrowRight,
  Terminal,
  Activity,
  Layers,
  Sparkles,
  Search
} from 'lucide-react';

interface DashboardProps {
  demoRepos: DemoRepoInfo[];
  onStartAnalysis: (req: AnalysisRequest) => void;
  onInstantReplay: (demoId: string) => void;
  isLoading: boolean;
}

export const Dashboard: React.FC<DashboardProps> = ({
  demoRepos,
  onStartAnalysis,
  onInstantReplay,
  isLoading
}) => {
  const workbenchRef = useRef<HTMLDivElement>(null);
  const simulatorRef = useRef<HTMLDivElement>(null);

  const scrollToWorkbench = () => {
    workbenchRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const scrollToSimulator = () => {
    simulatorRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  return (
    <div className="space-y-12 pb-12">
      {/* Hero Section */}
      <section className="relative overflow-hidden bg-white border-b border-slate-200">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 via-white to-indigo-50/30 pointer-events-none" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12 sm:py-16">
          <div className="max-w-3xl space-y-5">
            {/* Tag Badge */}
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 border border-blue-200/80 text-blue-700 text-xs font-mono font-medium shadow-xs">
              <Sparkles className="w-3.5 h-3.5 text-blue-600" />
              <span>Fix it. Prove it. · Nebius x NVIDIA AI Hackathon</span>
            </div>

            {/* Main Headline */}
            <h1 className="text-3xl sm:text-4xl lg:text-5xl font-extrabold text-slate-900 tracking-tight leading-[1.15]">
              Autonomous Code Repair That <span className="text-blue-600">Verifies Its Own Work</span>.
            </h1>

            {/* Subtitle */}
            <p className="text-base sm:text-lg text-slate-600 leading-relaxed">
              When AI coding assistants patch a bug, they claim victory on a single green unit test while silently breaking downstream modules. 
              <strong> Emend</strong> maps blast radiuses via AST call graphs, writes syntax-guaranteed patches with <strong>NVIDIA Nemotron</strong>, 
              verifies across 3 execution tiers, and automatically rolls back if collateral damage occurs.
            </p>

            {/* Action Buttons */}
            <div className="flex flex-wrap items-center gap-3 pt-2">
              <button
                onClick={scrollToWorkbench}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-blue-600 hover:bg-blue-700 text-white font-medium text-sm shadow-sm transition-all focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 active:scale-[0.99]"
              >
                <span>Launch Interactive Workbench</span>
                <ArrowRight className="w-4 h-4" />
              </button>

              <button
                onClick={() => onInstantReplay('billing_ripple')}
                className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-white hover:bg-slate-50 text-slate-700 font-medium text-sm border border-slate-300 shadow-xs transition-colors focus:outline-none focus:ring-2 focus:ring-slate-400 focus:ring-offset-2"
              >
                <Play className="w-4 h-4 text-blue-600 fill-blue-600" />
                <span>Instant Ripple Replay</span>
              </button>

              <button
                onClick={scrollToSimulator}
                className="inline-flex items-center gap-2 px-4 py-2.5 rounded-lg text-slate-600 hover:text-slate-900 text-sm font-medium transition-colors"
              >
                <Activity className="w-4 h-4 text-slate-500" />
                <span>See Ripple Catch Demo</span>
              </button>
            </div>

            {/* Key Value Highlights */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-6 border-t border-slate-100 text-xs font-mono text-slate-600">
              <div className="flex items-center gap-1.5">
                <CheckCircle2 className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>3-Tier Verification</span>
              </div>
              <div className="flex items-center gap-1.5">
                <GitFork className="w-4 h-4 text-indigo-600 flex-shrink-0" />
                <span>AST Call Graph</span>
              </div>
              <div className="flex items-center gap-1.5">
                <RotateCcw className="w-4 h-4 text-amber-600 flex-shrink-0" />
                <span>Git Auto-Rollback</span>
              </div>
              <div className="flex items-center gap-1.5">
                <Cpu className="w-4 h-4 text-purple-600 flex-shrink-0" />
                <span>NVIDIA Nemotron</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Container */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-12">
        {/* The Problem vs Emend Comparison Cards */}
        <section className="space-y-4">
          <div className="text-center max-w-2xl mx-auto space-y-1">
            <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
              Why Traditional AI Code Assistants Break Production
            </h2>
            <p className="text-xs sm:text-sm text-slate-500">
              The difference between superficial fixes and verifiable software repair.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
            {/* The Fragile Way */}
            <div className="rounded-xl border border-rose-200/80 bg-rose-50/30 p-6 space-y-3">
              <div className="flex items-center gap-2 text-rose-800 font-semibold text-sm">
                <AlertTriangle className="w-4 h-4 text-rose-600" />
                <span>Current Assistants (Blind Spot)</span>
              </div>
              <ul className="space-y-2.5 text-xs text-slate-600 leading-relaxed">
                <li className="flex items-start gap-2">
                  <span className="text-rose-500 font-bold">✕</span>
                  <span><strong>Single-Test Bias:</strong> Marks tasks "Fixed" if the isolated failing unit test passes, ignoring caller dependencies.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-rose-500 font-bold">✕</span>
                  <span><strong>Silent Regressions:</strong> Changes to shared utility functions cause silent ripple-effect crashes in downstream modules.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-rose-500 font-bold">✕</span>
                  <span><strong>No Rollback Mechanism:</strong> If a patch breaks secondary tests, developer is left with corrupted git trees and dirty states.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-rose-500 font-bold">✕</span>
                  <span><strong>Overconfident Hallucination:</strong> Never tells you which modified code paths have zero test coverage.</span>
                </li>
              </ul>
            </div>

            {/* The Emend Way */}
            <div className="rounded-xl border border-emerald-200/80 bg-emerald-50/30 p-6 space-y-3">
              <div className="flex items-center gap-2 text-emerald-800 font-semibold text-sm">
                <ShieldCheck className="w-4 h-4 text-emerald-600" />
                <span>The Emend Proof Architecture</span>
              </div>
              <ul className="space-y-2.5 text-xs text-slate-600 leading-relaxed">
                <li className="flex items-start gap-2">
                  <span className="text-emerald-600 font-bold">✓</span>
                  <span><strong>AST Blast Radius Engine:</strong> Computes transitive reverse reachability to pinpoint every caller affected by the patch.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-600 font-bold">✓</span>
                  <span><strong>3-Tier Cascading Verification:</strong> Runs the target test, blast-radius downstream suites, and full baseline diff before acceptance.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-600 font-bold">✓</span>
                  <span><strong>Atomic Revert Policy:</strong> Automatically reverts to baseline on regression, feeds failure trace back to Nemotron, and tries again.</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-emerald-600 font-bold">✓</span>
                  <span><strong>Residual Risk Audit:</strong> Transparently identifies code symbols in the blast radius that lack test coverage.</span>
                </li>
              </ul>
            </div>
          </div>
        </section>

        {/* Interactive Ripple Simulator */}
        <section ref={simulatorRef} className="space-y-3">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-200 pb-3">
            <div>
              <h2 className="text-lg sm:text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
                <Activity className="w-5 h-5 text-blue-600" />
                <span>Interactive Demonstration: The Ripple Catch</span>
              </h2>
              <p className="text-xs sm:text-sm text-slate-500">
                Step through how Emend catches a naive price-rounding fix that silently breaks downstream refunds.
              </p>
            </div>
            <span className="text-xs font-mono px-2.5 py-1 rounded bg-slate-100 text-slate-600 w-fit">
              Scenario: billing_ripple
            </span>
          </div>

          <RippleSimulator />
        </section>

        {/* 4-Step Technical Architecture */}
        <section className="space-y-6">
          <div className="text-center max-w-2xl mx-auto space-y-1">
            <h2 className="text-xl sm:text-2xl font-bold text-slate-900 tracking-tight">
              How Emend Operates
            </h2>
            <p className="text-xs sm:text-sm text-slate-500">
              A closed-loop agentic workflow powered by static analysis and deterministic verification.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-3 shadow-xs">
              <div className="w-8 h-8 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center font-bold text-sm">
                1
              </div>
              <h3 className="font-semibold text-slate-900 text-sm">Reproduce Baseline</h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Executes the targeted failing test in an isolated test runner to confirm the failure and capture the baseline traceback.
              </p>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-3 shadow-xs">
              <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-sm">
                2
              </div>
              <h3 className="font-semibold text-slate-900 text-sm">Predict Blast Radius</h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Builds an AST directed call-and-import graph using NetworkX to map all dependent modules and ranking downstream test suites.
              </p>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-3 shadow-xs">
              <div className="w-8 h-8 rounded-lg bg-purple-50 text-purple-600 flex items-center justify-center font-bold text-sm">
                3
              </div>
              <h3 className="font-semibold text-slate-900 text-sm">Synthesize Patch</h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                NVIDIA Nemotron generates syntax-verified <code className="text-slate-800 bg-slate-100 px-1 py-0.5 rounded">SEARCH/REPLACE</code> blocks with security guardrails preventing test tampering.
              </p>
            </div>

            <div className="bg-white rounded-xl border border-slate-200 p-5 space-y-3 shadow-xs">
              <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-sm">
                4
              </div>
              <h3 className="font-semibold text-slate-900 text-sm">Verify & Rollback</h3>
              <p className="text-xs text-slate-500 leading-relaxed">
                Deterministically tests Tier 1, Tier 2, and Tier 3 suites. If any regression occurs, reverts git state and retries with the regression trace.
              </p>
            </div>
          </div>
        </section>

        {/* Interactive Repair Workbench */}
        <section ref={workbenchRef} className="space-y-4">
          <div className="border-b border-slate-200 pb-3">
            <h2 className="text-lg sm:text-xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
              <Terminal className="w-5 h-5 text-blue-600" />
              <span>Interactive Repair Workbench</span>
            </h2>
            <p className="text-xs sm:text-sm text-slate-500 mt-0.5">
              Select one of the bundled benchmark repositories to trigger real-time autonomous analysis, or enter a custom repository path.
            </p>
          </div>

          <RepositoryForm
            demoRepos={demoRepos}
            onSubmit={onStartAnalysis}
            onInstantReplay={onInstantReplay}
            isLoading={isLoading}
          />
        </section>

        {/* Benchmark Evaluation Matrix */}
        <section className="bg-white rounded-xl border border-slate-200 p-6 space-y-4 shadow-xs">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-3">
            <div>
              <h3 className="text-base font-bold text-slate-900">
                Evaluation Benchmark Results
              </h3>
              <p className="text-xs text-slate-500">
                System performance across the bundled benchmark defect scenarios.
              </p>
            </div>
            <span className="text-xs font-mono text-slate-500">
              Harness: eval/run_eval.py
            </span>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs font-mono">
              <thead>
                <tr className="border-b border-slate-200 bg-slate-50/60 text-slate-700">
                  <th className="py-2.5 px-3 font-semibold">Benchmark Scenario</th>
                  <th className="py-2.5 px-3 font-semibold">Scenario Type</th>
                  <th className="py-2.5 px-3 font-semibold text-center">Baseline Repro</th>
                  <th className="py-2.5 px-3 font-semibold text-center">Ripple Caught?</th>
                  <th className="py-2.5 px-3 font-semibold text-center">Final Verdict</th>
                  <th className="py-2.5 px-3 font-semibold text-center">Attempts</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 text-slate-600">
                <tr className="hover:bg-slate-50/50 transition-colors">
                  <td className="py-2.5 px-3 font-semibold text-slate-900">shopcalc</td>
                  <td className="py-2.5 px-3">Simple percentage calculation defect</td>
                  <td className="py-2.5 px-3 text-center text-emerald-600 font-semibold">100%</td>
                  <td className="py-2.5 px-3 text-center text-slate-400">N/A (Isolated)</td>
                  <td className="py-2.5 px-3 text-center">
                    <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 font-semibold border border-emerald-200">
                      VERIFIED_FIXED
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-center font-bold text-slate-900">1</td>
                </tr>
                <tr className="hover:bg-slate-50/50 transition-colors bg-blue-50/20">
                  <td className="py-2.5 px-3 font-semibold text-blue-900">billing_ripple</td>
                  <td className="py-2.5 px-3">Ripple catch (half-up rounding vs refunds)</td>
                  <td className="py-2.5 px-3 text-center text-emerald-600 font-semibold">100%</td>
                  <td className="py-2.5 px-3 text-center text-blue-700 font-bold">Yes (Caught)</td>
                  <td className="py-2.5 px-3 text-center">
                    <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700 font-semibold border border-emerald-200">
                      VERIFIED_FIXED
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-center font-bold text-slate-900">2</td>
                </tr>
                <tr className="hover:bg-slate-50/50 transition-colors">
                  <td className="py-2.5 px-3 font-semibold text-slate-900">scheduler_hard</td>
                  <td className="py-2.5 px-3">External business holiday dependency</td>
                  <td className="py-2.5 px-3 text-center text-emerald-600 font-semibold">100%</td>
                  <td className="py-2.5 px-3 text-center text-slate-400">N/A</td>
                  <td className="py-2.5 px-3 text-center">
                    <span className="px-2 py-0.5 rounded bg-amber-50 text-amber-700 font-semibold border border-amber-200">
                      UNFIXED (Honest)
                    </span>
                  </td>
                  <td className="py-2.5 px-3 text-center font-bold text-slate-900">3</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>
      </div>
    </div>
  );
};
