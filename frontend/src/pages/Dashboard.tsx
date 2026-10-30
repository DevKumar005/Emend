import React from 'react';
import { DemoRepoInfo, AnalysisRequest } from '../types';
import { RepositoryForm } from '../components/RepositoryForm';
import { RippleSimulator } from '../components/RippleSimulator';
import { CheckCircle2, RotateCcw, GitFork, ShieldCheck } from 'lucide-react';

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
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-6">
      
      {/* Authentic Engineering Workspace Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-200 pb-4">
        <div>
          <h1 className="text-xl sm:text-2xl font-bold tracking-tight text-slate-900">
            Automated Code Repair & Verification
          </h1>
          <p className="text-xs sm:text-sm text-slate-600 mt-1 max-w-2xl leading-relaxed">
            Diagnoses failing tests, traces downstream dependencies via AST call graphs, and verifies all test suites before committing patches.
          </p>
        </div>

        {/* System Capability Badges */}
        <div className="flex flex-wrap items-center gap-2 text-xs font-mono">
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-white border border-slate-200 text-slate-700 shadow-2xs">
            <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
            <span>Multi-Tier Pytest</span>
          </div>
          <div className="flex items-center space-x-1.5 px-2.5 py-1 rounded bg-white border border-slate-200 text-slate-700 shadow-2xs">
            <RotateCcw className="w-3.5 h-3.5 text-blue-600" />
            <span>Git Rollback on Regression</span>
          </div>
        </div>
      </div>

      {/* Verification Pipeline / Proof Loop Simulator */}
      <RippleSimulator />

      {/* Scenario Intake & Test Run Intake */}
      <RepositoryForm
        demoRepos={demoRepos}
        onSubmit={onStartAnalysis}
        onInstantReplay={onInstantReplay}
        isLoading={isLoading}
      />

    </div>
  );
};
