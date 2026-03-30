import sqlite3
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Optional


class StateManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        with self._conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY,
                    title TEXT NOT NULL,
                    phase INTEGER NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS steps (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL REFERENCES tasks(id),
                    content TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'pending',
                    completed_at TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE NOT NULL,
                    started_at TIMESTAMP NOT NULL,
                    ended_at TIMESTAMP,
                    duration_minutes INTEGER,
                    task_id INTEGER REFERENCES tasks(id),
                    notes TEXT DEFAULT ''
                );
            """)

    def is_seeded(self) -> bool:
        with self._conn() as conn:
            row = conn.execute("SELECT COUNT(*) as n FROM tasks").fetchone()
            return row["n"] > 0

    def seed_tasks(self, tasks: list[dict]) -> None:
        with self._conn() as conn:
            for task in tasks:
                conn.execute(
                    "INSERT OR IGNORE INTO tasks (id, title, phase) VALUES (?, ?, ?)",
                    (task["id"], task["title"], task["phase"]),
                )
                for content in task["steps"]:
                    conn.execute(
                        "INSERT INTO steps (task_id, content) VALUES (?, ?)",
                        (task["id"], content),
                    )

    def get_current_task(self) -> Optional[dict]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE status != 'completed' ORDER BY id LIMIT 1"
            ).fetchone()
            return dict(row) if row else None

    def get_current_step(self) -> Optional[dict]:
        task = self.get_current_task()
        if not task:
            return None
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM steps WHERE task_id=? AND status='pending' ORDER BY id LIMIT 1",
                (task["id"],),
            ).fetchone()
            return dict(row) if row else None

    def get_task_steps(self, task_id: int) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM steps WHERE task_id=? ORDER BY id",
                (task_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def complete_step(self, step_id: int) -> Optional[dict]:
        now = datetime.now(timezone.utc).isoformat()
        with self._conn() as conn:
            conn.execute(
                "UPDATE steps SET status='completed', completed_at=? WHERE id=?",
                (now, step_id),
            )
            step = conn.execute(
                "SELECT task_id FROM steps WHERE id=?", (step_id,)
            ).fetchone()
            if step:
                conn.execute(
                    "UPDATE tasks SET status='in_progress', started_at=COALESCE(started_at, ?) "
                    "WHERE id=? AND status='pending'",
                    (now, step["task_id"]),
                )
                remaining = conn.execute(
                    "SELECT COUNT(*) as n FROM steps WHERE task_id=? AND status='pending'",
                    (step["task_id"],),
                ).fetchone()["n"]
                if remaining == 0:
                    conn.execute(
                        "UPDATE tasks SET status='completed', completed_at=? WHERE id=?",
                        (now, step["task_id"]),
                    )
        return self.get_current_step()

    def skip_step(self, step_id: int, reason: str) -> Optional[dict]:
        now = datetime.now(timezone.utc).isoformat()
        with self._conn() as conn:
            conn.execute(
                "UPDATE steps SET status='skipped', completed_at=? WHERE id=?",
                (now, step_id),
            )
        return self.get_current_step()

    def get_progress(self) -> dict:
        with self._conn() as conn:
            total = conn.execute("SELECT COUNT(*) as n FROM steps").fetchone()["n"]
            done = conn.execute(
                "SELECT COUNT(*) as n FROM steps WHERE status IN ('completed','skipped')"
            ).fetchone()["n"]
            total_sessions = conn.execute(
                "SELECT COUNT(*) as n FROM sessions WHERE ended_at IS NOT NULL"
            ).fetchone()["n"]
            streak = self._calculate_streak(conn)
        current_task = self.get_current_task()
        pct = round(done / total * 100) if total > 0 else 0
        phase = current_task["phase"] if current_task else 3
        return {
            "total_steps": total,
            "done_steps": done,
            "pct": pct,
            "phase": phase,
            "current_task": current_task,
            "total_sessions": total_sessions,
            "streak": streak,
        }

    def _calculate_streak(self, conn: sqlite3.Connection) -> int:
        rows = conn.execute(
            "SELECT DISTINCT DATE(completed_at) as d FROM steps "
            "WHERE status='completed' ORDER BY d DESC"
        ).fetchall()
        if not rows:
            return 0
        streak = 0
        today = date.today()
        for i, row in enumerate(rows):
            expected = (today - timedelta(days=i)).isoformat()
            if row["d"] == expected:
                streak += 1
            else:
                break
        return streak

    def start_session(self, task_id: int) -> int:
        now = datetime.now(timezone.utc).isoformat()
        with self._conn() as conn:
            cursor = conn.execute(
                "INSERT INTO sessions (date, started_at, task_id) VALUES (?, ?, ?)",
                (date.today().isoformat(), now, task_id),
            )
            return cursor.lastrowid

    def end_session(self, session_id: int, notes: str = "") -> int:
        now = datetime.now(timezone.utc)
        with self._conn() as conn:
            row = conn.execute(
                "SELECT started_at FROM sessions WHERE id=?", (session_id,)
            ).fetchone()
            if not row:
                return 0
            started = datetime.fromisoformat(row["started_at"])
            duration = max(0, int((now - started).total_seconds() / 60))
            conn.execute(
                "UPDATE sessions SET ended_at=?, duration_minutes=?, notes=? WHERE id=?",
                (now.isoformat(), duration, notes, session_id),
            )
            return duration

    def get_active_session(self) -> Optional[dict]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM sessions WHERE ended_at IS NULL ORDER BY id DESC LIMIT 1"
            ).fetchone()
            return dict(row) if row else None

    def get_steps_completed_today(self) -> int:
        today = date.today().isoformat()
        with self._conn() as conn:
            return conn.execute(
                "SELECT COUNT(*) as n FROM steps "
                "WHERE status='completed' AND DATE(completed_at)=?",
                (today,),
            ).fetchone()["n"]
