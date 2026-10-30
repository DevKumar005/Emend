import sqlite3
import json
import os
import time
from typing import Optional, List, Dict, Any
from contracts.schemas import Job, AgentEvent, ImpactReport, FinalReport, TestRun

DB_PATH = os.environ.get("DATABASE_URL", "sqlite:///./emend.db").replace("sqlite:///", "")

class DatabaseStore:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id TEXT PRIMARY KEY,
                    repo_source TEXT,
                    failing_test TEXT,
                    mode TEXT,
                    status TEXT,
                    created_at TEXT,
                    updated_at TEXT,
                    attempts_used INTEGER DEFAULT 0,
                    error_message TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT,
                    ts TEXT,
                    type TEXT,
                    title TEXT,
                    payload_json TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS impact_reports (
                    job_id TEXT PRIMARY KEY,
                    data_json TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS final_reports (
                    job_id TEXT PRIMARY KEY,
                    verdict TEXT,
                    patch TEXT,
                    data_json TEXT
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id TEXT,
                    scope TEXT,
                    data_json TEXT
                )
            """)
            conn.commit()

    def create_job(self, job_id: str, repo_source: str, failing_test: str, mode: str) -> Job:
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO jobs (id, repo_source, failing_test, mode, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (job_id, repo_source, failing_test, mode, "queued", now, now)
            )
            conn.commit()
        return Job(id=job_id, status="queued", created_at=now, updated_at=now, attempts_used=0)

    def update_job_status(self, job_id: str, status: str, attempts: int = 0, error_msg: Optional[str] = None):
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with self._get_conn() as conn:
            conn.execute(
                "UPDATE jobs SET status = ?, attempts_used = ?, error_message = ?, updated_at = ? WHERE id = ?",
                (status, attempts, error_msg, now, job_id)
            )
            conn.commit()

    def get_job(self, job_id: str) -> Optional[Job]:
        with self._get_conn() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE id = ?", (job_id,)).fetchone()
            if not row:
                return None
            return Job(
                id=row["id"],
                status=row["status"],
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                attempts_used=row["attempts_used"],
                error_message=row["error_message"]
            )

    def add_event(self, job_id: str, event: AgentEvent):
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO events (job_id, ts, type, title, payload_json) VALUES (?, ?, ?, ?, ?)",
                (job_id, event.ts, event.type, event.title, json.dumps(event.payload))
            )
            conn.commit()

    def get_events(self, job_id: str) -> List[AgentEvent]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT * FROM events WHERE job_id = ? ORDER BY id ASC", (job_id,)).fetchall()
            events = []
            for r in rows:
                events.append(AgentEvent(
                    ts=r["ts"],
                    type=r["type"],
                    title=r["title"],
                    payload=json.loads(r["payload_json"])
                ))
            return events

    def save_impact_report(self, job_id: str, report: ImpactReport):
        with self._get_conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO impact_reports (job_id, data_json) VALUES (?, ?)",
                (job_id, report.model_dump_json())
            )
            conn.commit()

    def get_impact_report(self, job_id: str) -> Optional[ImpactReport]:
        with self._get_conn() as conn:
            row = conn.execute("SELECT data_json FROM impact_reports WHERE job_id = ?", (job_id,)).fetchone()
            if not row:
                return None
            return ImpactReport.model_validate_json(row["data_json"])

    def save_final_report(self, job_id: str, report: FinalReport):
        with self._get_conn() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO final_reports (job_id, verdict, patch, data_json) VALUES (?, ?, ?, ?)",
                (job_id, report.verdict, report.patch, report.model_dump_json())
            )
            conn.commit()

    def get_final_report(self, job_id: str) -> Optional[FinalReport]:
        with self._get_conn() as conn:
            row = conn.execute("SELECT data_json FROM final_reports WHERE job_id = ?", (job_id,)).fetchone()
            if not row:
                return None
            return FinalReport.model_validate_json(row["data_json"])

    def save_test_run(self, job_id: str, test_run: TestRun):
        with self._get_conn() as conn:
            conn.execute(
                "INSERT INTO test_runs (job_id, scope, data_json) VALUES (?, ?, ?)",
                (job_id, test_run.scope, test_run.model_dump_json())
            )
            conn.commit()

    def get_test_runs(self, job_id: str) -> List[TestRun]:
        with self._get_conn() as conn:
            rows = conn.execute("SELECT data_json FROM test_runs WHERE job_id = ?", (job_id,)).fetchall()
            return [TestRun.model_validate_json(r["data_json"]) for r in rows]
