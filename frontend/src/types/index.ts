export interface AnalysisRequest {
  repo_source: string;
  branch?: string;
  failing_test: string;
  mode: 'hosted' | 'local';
}

export interface Job {
  id: string;
  status: 'queued' | 'baseline' | 'impact' | 'repair' | 'verify' | 'done' | 'error';
  created_at: string;
  updated_at: string;
  attempts_used: number;
  error_message?: string;
}

export interface ImpactNode {
  id: string;
  kind: 'module' | 'class' | 'function' | 'test';
  file: string;
  lines: number[];
  risk: 'high' | 'medium' | 'low' | 'none';
  label: 'verified pass' | 'verified fail' | 'predicted risk, unverified' | 'not affected (predicted)';
}

export interface ImpactEdge {
  source: string;
  target: string;
  kind: 'imports' | 'calls' | 'tests';
}

export interface RankedTest {
  id: string;
  score: number;
  reason: string;
  label: string;
}

export interface ImpactReport {
  changed_symbols: string[];
  nodes: ImpactNode[];
  edges: ImpactEdge[];
  ranked_tests: RankedTest[];
  caveats: string[];
}

export interface TestItem {
  id: string;
  outcome: 'passed' | 'failed' | 'error' | 'skipped';
  duration: number;
  message?: string;
}

export interface TestRun {
  scope: 'target' | 'impacted' | 'full';
  command: string;
  exit_code: number;
  duration_s: number;
  tests: TestItem[];
  output_tail: string;
}

export interface RepairAttempt {
  n: number;
  model: string;
  rationale: string;
  patch_blocks: any[];
  diff: string;
  status: 'applied' | 'invalid_patch' | 'reverted' | 'accepted' | 'rejected' | 'verified' | 'regression' | 'failed';
  target_run?: TestRun;
  impacted_run?: TestRun;
  full_run?: TestRun;
  regressions: string[];
  tokens_in: number;
  tokens_out: number;
}

export interface AgentEvent {
  ts: string | number;
  type: 'stage' | 'tool_call' | 'model_message' | 'test_result' | 'verdict' | 'error';
  title: string;
  payload: Record<string, any>;
}

export interface ResidualRisk {
  symbol: string;
  file: string;
  reason: string;
  callers_count: number;
}

export interface FinalReport {
  verdict: 'VERIFIED_FIXED' | 'FIXED_WITH_REGRESSIONS' | 'UNFIXED' | 'INVALID_PATCH';
  patch: string;
  attempts: RepairAttempt[];
  baseline_summary: Record<string, any>;
  residual_risk: ResidualRisk[];
  metrics: {
    time_s: number;
    tokens_total: number;
    attempts: number;
    revert_policy_executed?: boolean;
    deterministic_verification?: boolean;
    ripple_regressions_caught?: number;
    guardrails_passed?: boolean;
  };
}

export interface DemoRepoInfo {
  id: string;
  name: string;
  description: string;
  purpose: string;
  failing_test: string;
  expected_verdict: string;
}
