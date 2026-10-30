import React, { useState } from 'react';
import { DemoRepoInfo, AnalysisRequest } from '../types';
import { Play, History, GitBranch, Terminal } from 'lucide-react';

interface RepositoryFormProps {
  demoRepos: DemoRepoInfo[];
  onSubmit: (req: AnalysisRequest) => void;
  onInstantReplay?: (demoId: string) => void;
  isLoading: boolean;
}

export const RepositoryForm: React.FC<RepositoryFormProps> = ({
  demoRepos,
  onSubmit,
  onInstantReplay,
  isLoading
}) => {
  const [selectedDemoId, setSelectedDemoId] = useState<string>('billing_ripple');
  const [customGitUrl, setCustomGitUrl] = useState<string>('');
  const [isCustomRepo, setIsCustomRepo] = useState<boolean>(false);
  const [failingTest, setFailingTest] = useState<string>('tests/test_pricing.py::test_round_half_up_positive');
  const [branch, setBranch] = useState<string>('main');
  const [mode, setMode] = useState<'hosted' | 'local'>('hosted');

  const handleSelectDemo = (demo: DemoRepoInfo) => {
    setSelectedDemoId(demo.id);
    setIsCustomRepo(false);
    setFailingTest(demo.failing_test);
  };

  const handleDirectLaunch = (demo: DemoRepoInfo, e: React.MouseEvent) => {
    e.stopPropagation();
    onSubmit({
      repo_source: demo.id,
      branch: 'main',
      failing_test: demo.failing_test,
      mode
    });
  };

  const handleDirectReplay = (demoId: string, e: React.MouseEvent) => {
    e.stopPropagation();
    if (onInstantReplay) {
      onInstantReplay(demoId);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const repoSource = isCustomRepo ? customGitUrl.trim() : selectedDemoId;
    if (!repoSource || !failingTest.trim()) return;

    onSubmit({
      repo_source: repoSource,
      branch: branch || 'main',
      failing_test: failingTest.trim(),
      mode
    });
  };

  return (
    <div className="space-y-4">
      
      {/* 3 Benchmark Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3.5">
        {demoRepos.map((demo) => {
          const isSelected = !isCustomRepo && selectedDemoId === demo.id;

          return (
            <div
              key={demo.id}
              onClick={() => handleSelectDemo(demo)}
              className={`cursor-pointer rounded-lg border p-4 text-left transition relative flex flex-col justify-between ${
                isSelected
                  ? 'bg-white border-blue-600 ring-1 ring-blue-600 shadow-2xs'
                  : 'bg-white border-slate-200 hover:border-slate-300 shadow-2xs'
              }`}
            >
              <div>
                <div className="flex items-center justify-between gap-1.5 mb-2">
                  <div className="flex items-center space-x-1.5 min-w-0">
                    <span className="w-2 h-2 rounded-full bg-slate-400 flex-shrink-0" />
                    <h3 className="font-bold text-xs sm:text-sm text-slate-900 font-mono truncate">
                      {demo.id}
                    </h3>
                  </div>

                  <span className={`text-[10px] font-mono px-2 py-0.5 rounded font-semibold uppercase flex-shrink-0 ${
                    demo.expected_verdict === 'VERIFIED_FIXED'
                      ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                      : 'bg-slate-100 text-slate-700 border border-slate-200'
                  }`}>
                    {demo.expected_verdict}
                  </span>
                </div>

                <p className="text-xs text-slate-600 leading-relaxed mb-3">
                  {demo.description}
                </p>
              </div>

              <div className="pt-2.5 border-t border-slate-100 space-y-2">
                <div className="text-[11px] font-mono text-slate-600 truncate flex items-center space-x-1.5 bg-slate-50 p-1.5 rounded border border-slate-200">
                  <Terminal className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
                  <span className="truncate" title={demo.failing_test}>
                    {demo.failing_test.split('::').pop()}
                  </span>
                </div>

                {/* Direct Action Buttons */}
                <div className="flex items-center space-x-2 pt-0.5">
                  <button
                    type="button"
                    disabled={isLoading}
                    onClick={(e) => handleDirectLaunch(demo, e)}
                    className="flex-1 py-1.5 px-3 rounded bg-slate-900 hover:bg-slate-800 text-white text-xs font-medium flex items-center justify-center space-x-1.5 shadow-2xs transition disabled:opacity-50"
                  >
                    <Play className="w-3 h-3 fill-white" />
                    <span>Run Live</span>
                  </button>

                  <button
                    type="button"
                    disabled={isLoading}
                    onClick={(e) => handleDirectReplay(demo.id, e)}
                    className="py-1.5 px-3 rounded bg-white hover:bg-slate-50 text-slate-700 text-xs font-mono font-medium flex items-center justify-center space-x-1 border border-slate-300 transition shadow-2xs disabled:opacity-50"
                  >
                    <History className="w-3 h-3 text-slate-500" />
                    <span>Replay</span>
                  </button>
                </div>
              </div>

            </div>
          );
        })}
      </div>

      {/* Target Defect Configuration Box */}
      <form onSubmit={handleSubmit} className="bg-white rounded-lg border border-slate-200 p-4 shadow-2xs space-y-3.5">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-100 pb-2.5">
          <div className="flex items-center space-x-2">
            <Terminal className="w-4 h-4 text-slate-700" />
            <span className="text-xs font-bold font-mono uppercase text-slate-800">
              Target Defect Intake
            </span>
          </div>

          <button
            type="button"
            onClick={() => setIsCustomRepo(!isCustomRepo)}
            className="text-xs font-mono text-blue-600 hover:text-blue-700 flex items-center space-x-1 underline"
          >
            <GitBranch className="w-3.5 h-3.5" />
            <span>{isCustomRepo ? 'Use Bundled Scenarios' : 'Switch to Custom Git URL'}</span>
          </button>
        </div>

        {isCustomRepo ? (
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div className="sm:col-span-2 space-y-1">
              <label className="block text-xs font-mono text-slate-600">Git Repository URL</label>
              <input
                type="text"
                required
                value={customGitUrl}
                onChange={(e) => setCustomGitUrl(e.target.value)}
                placeholder="https://github.com/organization/repo.git"
                className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-xs font-mono text-slate-900 focus:outline-none focus:border-blue-500 transition"
              />
            </div>
            <div className="space-y-1">
              <label className="block text-xs font-mono text-slate-600">Branch</label>
              <input
                type="text"
                value={branch}
                onChange={(e) => setBranch(e.target.value)}
                placeholder="main"
                className="w-full bg-white border border-slate-300 rounded px-3 py-1.5 text-xs font-mono text-slate-900 focus:outline-none focus:border-blue-500 transition"
              />
            </div>
          </div>
        ) : null}

        <div className="space-y-1">
          <label className="block text-xs font-mono text-slate-600">
            Target Failing Test (Pytest Identifier)
          </label>
          <input
            type="text"
            required
            value={failingTest}
            onChange={(e) => setFailingTest(e.target.value)}
            placeholder="tests/test_file.py::test_failing_function"
            className="w-full bg-white border border-slate-300 rounded px-3 py-2 text-xs font-mono text-slate-900 focus:outline-none focus:border-blue-500 transition"
          />
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-1">
          <div className="flex flex-wrap items-center gap-3 text-xs font-mono text-slate-600">
            <span className="text-slate-500 text-xs">Sandbox Environment:</span>
            <label className="flex items-center space-x-1 cursor-pointer text-slate-800 text-xs">
              <input
                type="radio"
                name="run_mode"
                checked={mode === 'hosted'}
                onChange={() => setMode('hosted')}
                className="accent-blue-600"
              />
              <span>Host Process</span>
            </label>
            <label className="flex items-center space-x-1 cursor-pointer text-slate-600 hover:text-slate-900 text-xs">
              <input
                type="radio"
                name="run_mode"
                checked={mode === 'local'}
                onChange={() => setMode('local')}
                className="accent-blue-600"
              />
              <span>Docker Container</span>
            </label>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full sm:w-auto px-4 py-2 rounded bg-blue-600 hover:bg-blue-700 text-white font-medium text-xs font-mono shadow-2xs transition disabled:opacity-50 flex items-center justify-center space-x-2"
          >
            {isLoading ? (
              <>
                <div className="w-3.5 h-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                <span>Executing Repair Loop...</span>
              </>
            ) : (
              <>
                <Play className="w-3.5 h-3.5 fill-white" />
                <span>Execute & Prove Repair</span>
              </>
            )}
          </button>
        </div>

      </form>

    </div>
  );
};
