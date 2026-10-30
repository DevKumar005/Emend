import {
  AnalysisRequest,
  Job,
  ImpactReport,
  FinalReport,
  TestRun,
  AgentEvent,
  DemoRepoInfo
} from '../types';

const API_BASE = '/api';

export async function fetchDemoRepos(): Promise<DemoRepoInfo[]> {
  const res = await fetch(`${API_BASE}/demo-repos`);
  if (!res.ok) throw new Error('Failed to load demo repositories');
  return res.json();
}

export async function createAnalysis(req: AnalysisRequest): Promise<{ job_id: string; analysis_id: string; status: string }> {
  const res = await fetch(`${API_BASE}/analysis`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req)
  });
  if (!res.ok) throw new Error('Failed to initiate analysis');
  return res.json();
}

export async function fetchJob(jobId: string): Promise<Job> {
  const res = await fetch(`${API_BASE}/jobs/${jobId}`);
  if (!res.ok) throw new Error('Failed to fetch job');
  return res.json();
}

export async function fetchImpactReport(jobId: string): Promise<ImpactReport> {
  const res = await fetch(`${API_BASE}/analysis/${jobId}/impact`);
  if (!res.ok) throw new Error('Impact report is not ready yet');
  return res.json();
}

export async function fetchFinalReport(jobId: string): Promise<FinalReport> {
  const res = await fetch(`${API_BASE}/analysis/${jobId}/report`);
  if (!res.ok) throw new Error('Final report is not ready yet');
  return res.json();
}

export async function fetchTestRuns(jobId: string): Promise<TestRun[]> {
  const res = await fetch(`${API_BASE}/analysis/${jobId}/tests`);
  if (!res.ok) throw new Error('Failed to load test runs');
  return res.json();
}

export async function fetchHealth(): Promise<any> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Health check failed');
  return res.json();
}

export async function fetchRecordedRun(demoId: string): Promise<{
  demo_id: string;
  events: AgentEvent[];
  impact: ImpactReport;
  report: FinalReport;
  test_runs?: TestRun[];
}> {
  const res = await fetch(`${API_BASE}/demo-repos/recorded-run/${demoId}`);
  if (!res.ok) throw new Error('Failed to load recorded run');
  return res.json();
}

export function subscribeJobEvents(
  jobId: string,
  onEvent: (event: AgentEvent) => void,
  onError?: (err: any) => void
): () => void {
  const eventSource = new EventSource(`${API_BASE}/jobs/${jobId}/events`);

  eventSource.onmessage = (e) => {
    try {
      const data: AgentEvent = JSON.parse(e.data);
      onEvent(data);
    } catch (err) {
      // Ignore keepalive comments
    }
  };

  eventSource.onerror = (err) => {
    if (onError) onError(err);
  };

  return () => {
    eventSource.close();
  };
}
