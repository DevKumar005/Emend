import React, { useEffect, useState } from 'react';
import {
  Job,
  ImpactReport,
  FinalReport,
  TestRun,
  AgentEvent
} from '../types';
import {
  fetchJob,
  fetchImpactReport,
  fetchFinalReport,
  fetchTestRuns,
  subscribeJobEvents
} from '../services/api';
import { VerdictBanner } from '../components/VerdictBanner';
import { AgentTimeline } from '../components/AgentTimeline';
import { DependencyGraph } from '../components/DependencyGraph';
import { CodeDiff } from '../components/CodeDiff';
import { TestResults } from '../components/TestResults';
import { ResidualRiskList } from '../components/ResidualRiskList';
import { ArrowLeft, RefreshCw, Layers, FileCode, AlertTriangle } from 'lucide-react';

interface AnalysisDetailsProps {
  jobId: string;
  onBack: () => void;
  preloadedData?: {
    events: AgentEvent[];
    impact: ImpactReport;
    report: FinalReport;
    testRuns?: TestRun[];
  };
}

export const AnalysisDetails: React.FC<AnalysisDetailsProps> = ({ jobId, onBack, preloadedData }) => {
  const [job, setJob] = useState<Job | null>(null);
  const [events, setEvents] = useState<AgentEvent[]>(preloadedData?.events || []);
  const [impact, setImpact] = useState<ImpactReport | null>(preloadedData?.impact || null);
  const [report, setReport] = useState<FinalReport | null>(preloadedData?.report || null);
  const [testRuns, setTestRuns] = useState<TestRun[]>(preloadedData?.testRuns || []);
  const [activeTab, setActiveTab] = useState<'diff' | 'tests' | 'risks'>('diff');

  useEffect(() => {
    if (preloadedData) {
      setEvents(preloadedData.events || []);
      setImpact(preloadedData.impact || null);
      setReport(preloadedData.report || null);
      if (preloadedData.testRuns && preloadedData.testRuns.length > 0) {
        setTestRuns(preloadedData.testRuns);
      } else if (preloadedData.report?.attempts) {
        const runsFromAttempts = preloadedData.report.attempts.flatMap(a =>
          [a.target_run, a.impacted_run, a.full_run].filter(Boolean) as TestRun[]
        );
        if (runsFromAttempts.length > 0) {
          setTestRuns(runsFromAttempts);
        }
      }
      return;
    }

    // 1. Initial Job Poll
    fetchJob(jobId)
      .then(setJob)
      .catch(console.error);

    // 2. Subscribe to live SSE events
    const unsubscribe = subscribeJobEvents(
      jobId,
      (newEvent) => {
        setEvents((prev) => [...prev, newEvent]);

        if (newEvent.type === 'verdict' || newEvent.title.toLowerCase().includes('verdict')) {
          fetchFinalReport(jobId).then(setReport).catch(() => {});
          fetchTestRuns(jobId).then(setTestRuns).catch(() => {});
        }
        if (newEvent.type === 'stage' || newEvent.title.toLowerCase().includes('impact') || newEvent.title.toLowerCase().includes('graph')) {
          fetchImpactReport(jobId).then(setImpact).catch(() => {});
        }
      },
      (err) => console.log('SSE status:', err)
    );

    // 3. Periodic Poll check for data ready
    const interval = setInterval(async () => {
      try {
        const currentJob = await fetchJob(jobId);
        setJob(currentJob);

        if (!impact) {
          fetchImpactReport(jobId).then(setImpact).catch(() => {});
        }
        if (!report && (currentJob.status === 'done' || currentJob.status === 'error')) {
          fetchFinalReport(jobId).then(setReport).catch(() => {});
          fetchTestRuns(jobId).then(setTestRuns).catch(() => {});
          clearInterval(interval);
        }
      } catch (e) {
        // Still processing
      }
    }, 1500);

    return () => {
      unsubscribe();
      clearInterval(interval);
    };
  }, [jobId, preloadedData]);

  const displayTestRuns = testRuns.length > 0
    ? testRuns
    : (report?.attempts.flatMap(a => [a.target_run, a.impacted_run, a.full_run].filter(Boolean) as TestRun[]) || []);

  const attemptsCount = report?.attempts?.length || 0;
  const risksCount = report?.residual_risk?.length || 0;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6 space-y-5">
      
      {/* Top Breadcrumb Navigation */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-3 border-b border-slate-200">
        <div className="flex items-center space-x-2">
          <button
            onClick={onBack}
            className="flex items-center space-x-1.5 text-xs font-mono text-slate-700 hover:text-slate-900 px-2.5 py-1.5 rounded-lg bg-white border border-slate-200 hover:bg-slate-50 transition shadow-2xs font-medium"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>Back to Scenarios</span>
          </button>
          <span className="text-slate-300">/</span>
          <span className="font-mono text-xs text-slate-500">
            Job #{jobId}
          </span>
        </div>

        <div className="flex items-center space-x-2 text-xs font-mono">
          <span className="text-slate-500">Status:</span>
          <span className={`px-2.5 py-0.5 rounded-full border text-[10px] font-bold uppercase ${
            report
              ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
              : job?.status === 'error'
              ? 'bg-rose-50 text-rose-800 border-rose-300'
              : 'bg-blue-50 text-blue-800 border-blue-300 animate-pulse'
          }`}>
            {report ? 'Completed' : job?.status || 'Active Proof Loop...'}
          </span>
        </div>
      </div>

      {/* Final Verdict Banner (when available) */}
      {report && <VerdictBanner report={report} jobId={jobId} />}

      {/* Main Split: Execution Stream (Left) and AST Blast Radius Graph (Right) */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        <AgentTimeline events={events} />
        {impact ? (
          <DependencyGraph impact={impact} />
        ) : (
          <div className="bg-white rounded-xl border border-slate-200 flex flex-col items-center justify-center text-center p-8 h-[520px] font-mono text-xs shadow-sm">
            <RefreshCw className="w-6 h-6 animate-spin text-blue-600 mb-3" />
            <span className="text-slate-800 font-bold">Constructing AST Call Graph...</span>
            <span className="text-[11px] text-slate-500 mt-1">Mapping callers and reachability</span>
          </div>
        )}
      </div>

      {/* Inspection Tabs */}
      <div className="space-y-3 pt-1">
        <div className="flex items-center space-x-1.5 sm:space-x-2 border-b border-slate-200 pb-2 font-mono text-xs overflow-x-auto">
          <button
            onClick={() => setActiveTab('diff')}
            className={`flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg transition font-medium flex-shrink-0 ${
              activeTab === 'diff'
                ? 'bg-slate-900 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <FileCode className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Code Diffs ({attemptsCount} Attempts)</span>
            <span className="sm:hidden">Diffs ({attemptsCount})</span>
          </button>

          <button
            onClick={() => setActiveTab('tests')}
            className={`flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg transition font-medium flex-shrink-0 ${
              activeTab === 'tests'
                ? 'bg-slate-900 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Test Suites ({displayTestRuns.length > 0 ? displayTestRuns.length : (report ? '3 Tiers' : 'Pending')})</span>
            <span className="sm:hidden">Tests ({displayTestRuns.length > 0 ? displayTestRuns.length : (report ? '3' : '...')})</span>
          </button>

          <button
            onClick={() => setActiveTab('risks')}
            className={`flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 rounded-lg transition font-medium flex-shrink-0 ${
              activeTab === 'risks'
                ? 'bg-slate-900 text-white shadow-xs'
                : 'text-slate-600 hover:text-slate-900 hover:bg-slate-100'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            <span className="hidden sm:inline">Residual Risks ({risksCount} Untested)</span>
            <span className="sm:hidden">Risks ({risksCount})</span>
          </button>
        </div>

        <div>
          {activeTab === 'diff' && <CodeDiff attempts={report?.attempts || []} />}
          {activeTab === 'tests' && <TestResults runs={displayTestRuns} />}
          {activeTab === 'risks' && <ResidualRiskList risks={report?.residual_risk || []} />}
        </div>
      </div>

    </div>
  );
};
