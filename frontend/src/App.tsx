import React, { useState, useEffect } from 'react';
import { DemoRepoInfo, AnalysisRequest, AgentEvent, ImpactReport, FinalReport, TestRun } from './types';
import { fetchDemoRepos, createAnalysis, fetchRecordedRun, fetchHealth } from './services/api';
import { Navbar } from './components/Navbar';
import { Dashboard } from './pages/Dashboard';
import { AnalysisDetails } from './pages/AnalysisDetails';
import { Github, ExternalLink } from 'lucide-react';

export const App: React.FC = () => {
  const [demoRepos, setDemoRepos] = useState<DemoRepoInfo[]>([]);
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isLiveTokenFactory, setIsLiveTokenFactory] = useState<boolean>(false);
  const [preloadedData, setPreloadedData] = useState<{
    events: AgentEvent[];
    impact: ImpactReport;
    report: FinalReport;
    testRuns?: TestRun[];
  } | undefined>(undefined);

  useEffect(() => {
    fetchDemoRepos()
      .then(setDemoRepos)
      .catch((err) => {
        console.warn('Could not fetch demo repos from API:', err);
        setDemoRepos([
          {
            id: 'billing_ripple',
            name: 'billing_ripple (Ripple Catch Demo)',
            description: 'Naive fix passes target test but silently causes regressions in downstream refunds.py. Emend catches the regression, rolls back, and verifies a symmetric Decimal repair.',
            purpose: 'Demonstrate Blast Radius Engine & proof verification loop with regression recovery.',
            failing_test: 'tests/test_pricing.py::test_round_half_up_positive',
            expected_verdict: 'VERIFIED_FIXED'
          },
          {
            id: 'shopcalc',
            name: 'shopcalc (Simple Bug)',
            description: 'Discount logic subtracts percent directly instead of percentage computation. One-line repairable bug.',
            purpose: 'Fast demonstration of single-attempt diagnosis, patch generation, and deterministic verification.',
            failing_test: 'tests/test_shop.py::test_apply_discount_fifty_percent',
            expected_verdict: 'VERIFIED_FIXED'
          },
          {
            id: 'scheduler_hard',
            name: 'scheduler_hard (Honest Failure)',
            description: 'Business logic relies on an external holiday calendar not derivable from code. Emend tries 3 times, honestly declares UNFIXED, and documents residual risks.',
            purpose: 'Demonstrate agent honesty: never claiming more than it can deterministically verify.',
            failing_test: 'tests/test_scheduler.py::test_corporate_founding_day_holiday',
            expected_verdict: 'UNFIXED'
          }
        ]);
      });

    fetchHealth()
      .then((data) => {
        setIsLiveTokenFactory(data?.models?.live_tokenfactory_active ?? false);
      })
      .catch(() => {});
  }, []);

  const handleStartAnalysis = async (req: AnalysisRequest) => {
    setIsLoading(true);
    try {
      setPreloadedData(undefined);
      const res = await createAnalysis(req);
      setCurrentJobId(res.job_id);
    } catch (err) {
      console.error('Failed to create analysis:', err);
      handleInstantReplay(req.repo_source || 'billing_ripple');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInstantReplay = async (demoId: string = 'billing_ripple') => {
    setIsLoading(true);
    try {
      const data = await fetchRecordedRun(demoId);
      setPreloadedData({
        events: data.events,
        impact: data.impact,
        report: data.report,
        testRuns: data.test_runs
      });
      setCurrentJobId(`replay_${demoId}`);
    } catch (err) {
      console.error('Error fetching recorded run:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#f6f8fa] text-slate-900 antialiased selection:bg-blue-100 selection:text-blue-900">
      <Navbar
        onRecordedReplay={handleInstantReplay}
        isLiveTokenFactory={isLiveTokenFactory}
      />

      <main className="flex-1 w-full max-w-full overflow-x-hidden">
        {currentJobId ? (
          <AnalysisDetails
            jobId={currentJobId}
            onBack={() => {
              setCurrentJobId(null);
              setPreloadedData(undefined);
            }}
            preloadedData={preloadedData}
          />
        ) : (
          <Dashboard
            demoRepos={demoRepos}
            onStartAnalysis={handleStartAnalysis}
            onInstantReplay={handleInstantReplay}
            isLoading={isLoading}
          />
        )}
      </main>

      <footer className="border-t border-slate-200 bg-white py-4 px-4 sm:px-6 lg:px-8 text-xs text-slate-600 mt-12 font-mono">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3 text-center md:text-left">
          <div className="flex flex-wrap items-center justify-center md:justify-start gap-2 text-slate-700">
            <span className="font-bold text-slate-900 tracking-tight">Emend</span>
            <span className="text-slate-300 hidden sm:inline">·</span>
            <span>Automated Code Repair & Blast-Radius Engine</span>
          </div>

          <div className="flex flex-wrap items-center justify-center md:justify-end gap-2.5 sm:gap-3 text-slate-600">
            <a
              href="https://github.com/DevKumar005/Emend"
              target="_blank"
              rel="noreferrer"
              className="text-slate-800 hover:text-blue-600 font-medium inline-flex items-center space-x-1 transition-colors"
            >
              <Github className="w-3.5 h-3.5 text-slate-700" />
              <span>GitHub Repo</span>
            </a>
            
            <span className="text-slate-300 hidden sm:inline">·</span>
            <span className="text-slate-500 font-medium">Authors:</span>
            
            <a
              href="https://github.com/anuragkumar80"
              target="_blank"
              rel="noreferrer"
              className="text-slate-800 hover:text-blue-600 font-semibold inline-flex items-center space-x-1 transition-colors"
            >
              <span>Anurag Kumar (@anuragkumar80)</span>
              <ExternalLink className="w-3 h-3 text-slate-400" />
            </a>

            <span className="text-slate-300">·</span>

            <a
              href="https://github.com/DevKumar005"
              target="_blank"
              rel="noreferrer"
              className="text-slate-800 hover:text-blue-600 font-semibold inline-flex items-center space-x-1 transition-colors"
            >
              <span>Dev Kumar (@DevKumar005)</span>
              <ExternalLink className="w-3 h-3 text-slate-400" />
            </a>
          </div>
        </div>
      </footer>
    </div>
  );
};
