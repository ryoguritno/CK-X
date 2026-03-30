# Study Companion Bot — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Telegram bot that sends daily task notifications, tracks step-level progress via SQLite, and provides AI mentoring (explain/hint/quiz) via Ollama, running as a Docker service alongside ck-x-simulator.

**Architecture:** Single Python service using python-telegram-bot v20 (async). Four modules — state manager (SQLite), roadmap parser (markdown → DB seed), mentor (Ollama HTTP), scheduler (APScheduler cron). Wired together in main.py. Added to existing docker-compose.yml.

**Tech Stack:** Python 3.11, python-telegram-bot 20.7, APScheduler 3.10.4, httpx 0.27.0, pyyaml 6.0.1, pytz 2024.1, sqlite3 (stdlib), pytest + pytest-asyncio

---

## File Map

| File | Create/Modify | Responsibility |
|------|--------------|----------------|
| `study-companion/Dockerfile` | Create | Container image |
| `study-companion/requirements.txt` | Create | Python deps |
| `study-companion/config.yaml` | Create | Ollama, schedule, timezone config |
| `study-companion/.env.example` | Create | Token template (not committed) |
| `study-companion/state/__init__.py` | Create | Package marker |
| `study-companion/state/manager.py` | Create | SQLite CRUD — tasks, steps, sessions |
| `study-companion/roadmap/__init__.py` | Create | Package marker |
| `study-companion/roadmap/parser.py` | Create | Parse roadmap markdown → list of task dicts |
| `study-companion/bot/__init__.py` | Create | Package marker |
| `study-companion/bot/mentor.py` | Create | Ollama HTTP calls, prompt templates |
| `study-companion/bot/scheduler.py` | Create | APScheduler morning/evening jobs |
| `study-companion/bot/handlers.py` | Create | All Telegram command handlers |
| `study-companion/bot/main.py` | Create | Entry point — wires all components |
| `study-companion/tests/__init__.py` | Create | Package marker |
| `study-companion/tests/test_manager.py` | Create | State manager unit tests |
| `study-companion/tests/test_parser.py` | Create | Roadmap parser unit tests |
| `study-companion/tests/test_mentor.py` | Create | Mentor unit tests (mock HTTP) |
| `docker-compose.yml` | Modify | Add study-companion service |

---

## Task 1: Project Scaffold

**Files:**
- Create: `study-companion/Dockerfile`
- Create: `study-companion/requirements.txt`
- Create: `study-companion/config.yaml`
- Create: `study-companion/.env.example`
- Create: `study-companion/state/__init__.py`
- Create: `study-companion/roadmap/__init__.py`
- Create: `study-companion/bot/__init__.py`
- Create: `study-companion/tests/__init__.py`
- Create: `study-companion/data/.gitkeep`

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p ~/ck-x-simulator/study-companion/{state,roadmap,bot,tests,data}
touch ~/ck-x-simulator/study-companion/{state,roadmap,bot,tests}/__init__.py
touch ~/ck-x-simulator/study-companion/data/.gitkeep
```

- [ ] **Step 2: Create requirements.txt**

```
# study-companion/requirements.txt
python-telegram-bot==20.7
apscheduler==3.10.4
httpx==0.27.0
pyyaml==6.0.1
pytz==2024.1
pytest==8.1.1
pytest-asyncio==0.23.6
```

- [ ] **Step 3: Create Dockerfile**

```dockerfile
# study-companion/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "-m", "bot.main"]
```

- [ ] **Step 4: Create config.yaml**

```yaml
# study-companion/config.yaml
ollama:
  host: http://host.docker.internal:11434
  model: llama3.1:8b
  timeout_seconds: 60

notifications:
  morning_time: "07:00"
  evening_time: "19:00"
  timezone: "Asia/Jakarta"

roadmap:
  plan_file: /app/docs/superpowers/plans/2026-03-29-devops-certification-roadmap.md
```

- [ ] **Step 5: Create .env.example**

```bash
# study-companion/.env.example
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

- [ ] **Step 6: Verify structure**

```bash
find ~/ck-x-simulator/study-companion -type f | sort
```

Expected output includes:
```
study-companion/.env.example
study-companion/Dockerfile
study-companion/bot/__init__.py
study-companion/config.yaml
study-companion/data/.gitkeep
study-companion/requirements.txt
study-companion/roadmap/__init__.py
study-companion/state/__init__.py
study-companion/tests/__init__.py
```

- [ ] **Step 7: Commit**

```bash
cd ~/ck-x-simulator
git add study-companion/
git commit -m "feat: scaffold study-companion project structure"
```

---

## Task 2: State Manager

**Files:**
- Create: `study-companion/state/manager.py`
- Create: `study-companion/tests/test_manager.py`

- [ ] **Step 1: Write failing tests**

```python
# study-companion/tests/test_manager.py
import pytest
import tempfile
import os
from datetime import date
from state.manager import StateManager

@pytest.fixture
def db():
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        path = f.name
    sm = StateManager(path)
    sm.init_db()
    yield sm
    os.unlink(path)

SAMPLE_TASKS = [
    {
        "id": 1,
        "title": "Task 1: Setup",
        "phase": 1,
        "steps": ["Step 1: Do thing A", "Step 2: Do thing B"],
    },
    {
        "id": 2,
        "title": "Task 2: Networking",
        "phase": 1,
        "steps": ["Step 1: Learn iptables"],
    },
]

def test_is_seeded_false_on_empty_db(db):
    assert db.is_seeded() is False

def test_seed_and_is_seeded(db):
    db.seed_tasks(SAMPLE_TASKS)
    assert db.is_seeded() is True

def test_get_current_task_returns_first_pending(db):
    db.seed_tasks(SAMPLE_TASKS)
    task = db.get_current_task()
    assert task["id"] == 1
    assert task["title"] == "Task 1: Setup"

def test_get_current_step_returns_first_pending_step(db):
    db.seed_tasks(SAMPLE_TASKS)
    step = db.get_current_step()
    assert step["content"] == "Step 1: Do thing A"

def test_complete_step_returns_next_step(db):
    db.seed_tasks(SAMPLE_TASKS)
    step = db.get_current_step()
    next_step = db.complete_step(step["id"])
    assert next_step["content"] == "Step 2: Do thing B"

def test_complete_all_steps_marks_task_completed(db):
    db.seed_tasks(SAMPLE_TASKS)
    s1 = db.get_current_step()
    db.complete_step(s1["id"])
    s2 = db.get_current_step()
    db.complete_step(s2["id"])
    task = db.get_current_task()
    assert task["id"] == 2  # moved to next task

def test_skip_step(db):
    db.seed_tasks(SAMPLE_TASKS)
    step = db.get_current_step()
    next_step = db.skip_step(step["id"], "too easy")
    assert next_step["content"] == "Step 2: Do thing B"

def test_get_progress(db):
    db.seed_tasks(SAMPLE_TASKS)
    p = db.get_progress()
    assert p["total_steps"] == 3
    assert p["done_steps"] == 0
    assert p["pct"] == 0

def test_session_start_and_end(db):
    db.seed_tasks(SAMPLE_TASKS)
    session_id = db.start_session(task_id=1)
    assert session_id > 0
    active = db.get_active_session()
    assert active is not None
    duration = db.end_session(session_id, notes="studied iptables")
    assert duration >= 0
    assert db.get_active_session() is None

def test_get_task_steps(db):
    db.seed_tasks(SAMPLE_TASKS)
    steps = db.get_task_steps(1)
    assert len(steps) == 2
    assert steps[0]["content"] == "Step 1: Do thing A"

def test_get_steps_completed_today_zero_initially(db):
    db.seed_tasks(SAMPLE_TASKS)
    assert db.get_steps_completed_today() == 0

def test_get_steps_completed_today_after_done(db):
    db.seed_tasks(SAMPLE_TASKS)
    step = db.get_current_step()
    db.complete_step(step["id"])
    assert db.get_steps_completed_today() == 1
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/ck-x-simulator/study-companion
pip install -r requirements.txt
pytest tests/test_manager.py -v
```

Expected: `ModuleNotFoundError: No module named 'state.manager'`

- [ ] **Step 3: Implement state/manager.py**

```python
# study-companion/state/manager.py
import sqlite3
from datetime import date, datetime, timedelta
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
        now = datetime.utcnow().isoformat()
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
        now = datetime.utcnow().isoformat()
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
        now = datetime.utcnow().isoformat()
        with self._conn() as conn:
            cursor = conn.execute(
                "INSERT INTO sessions (date, started_at, task_id) VALUES (?, ?, ?)",
                (date.today().isoformat(), now, task_id),
            )
            return cursor.lastrowid

    def end_session(self, session_id: int, notes: str = "") -> int:
        now = datetime.utcnow()
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
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd ~/ck-x-simulator/study-companion
pytest tests/test_manager.py -v
```

Expected: all 12 tests PASS

- [ ] **Step 5: Commit**

```bash
cd ~/ck-x-simulator
git add study-companion/state/ study-companion/tests/test_manager.py
git commit -m "feat: add state manager with SQLite CRUD"
```

---

## Task 3: Roadmap Parser

**Files:**
- Create: `study-companion/roadmap/parser.py`
- Create: `study-companion/tests/test_parser.py`

- [ ] **Step 1: Write failing tests**

```python
# study-companion/tests/test_parser.py
import textwrap
import tempfile
import os
from roadmap.parser import parse_roadmap

SAMPLE_MARKDOWN = textwrap.dedent("""
    # My Roadmap

    ## Phase 1: Foundation (Months 1-4)

    ### Task 1: Study Environment Setup

    Some description here.

    - [ ] **Step 1: Verify ck-x-simulator is running**

    ```bash
    docker compose ps
    ```

    - [ ] **Step 2: Create a study log file**

    ## Phase 2: Kubernetes Core (Months 4-16)

    ### Task 2: Core Workloads

    - [ ] **Step 1: Create resources imperatively**

    ### Task 3: Networking

    - [ ] **Step 1: Master IP and routing commands**
    - [ ] **Step 2: Understand iptables**
""")

def _write_temp(content: str) -> str:
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False)
    f.write(content)
    f.close()
    return f.name

def test_parse_returns_list_of_tasks():
    path = _write_temp(SAMPLE_MARKDOWN)
    tasks = parse_roadmap(path)
    os.unlink(path)
    assert len(tasks) == 3

def test_task_has_correct_fields():
    path = _write_temp(SAMPLE_MARKDOWN)
    tasks = parse_roadmap(path)
    os.unlink(path)
    t = tasks[0]
    assert t["id"] == 1
    assert "Task 1" in t["title"]
    assert t["phase"] == 1

def test_task_steps_extracted():
    path = _write_temp(SAMPLE_MARKDOWN)
    tasks = parse_roadmap(path)
    os.unlink(path)
    assert len(tasks[0]["steps"]) == 2
    assert tasks[0]["steps"][0] == "Step 1: Verify ck-x-simulator is running"

def test_phase_assigned_correctly():
    path = _write_temp(SAMPLE_MARKDOWN)
    tasks = parse_roadmap(path)
    os.unlink(path)
    assert tasks[0]["phase"] == 1
    assert tasks[1]["phase"] == 2
    assert tasks[2]["phase"] == 2

def test_step_content_is_bold_text_only():
    path = _write_temp(SAMPLE_MARKDOWN)
    tasks = parse_roadmap(path)
    os.unlink(path)
    # Should not include markdown code blocks or surrounding text
    for task in tasks:
        for step in task["steps"]:
            assert "```" not in step
            assert "**" not in step
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/ck-x-simulator/study-companion
pytest tests/test_parser.py -v
```

Expected: `ModuleNotFoundError: No module named 'roadmap.parser'`

- [ ] **Step 3: Implement roadmap/parser.py**

```python
# study-companion/roadmap/parser.py
import re
from pathlib import Path


def parse_roadmap(file_path: str) -> list[dict]:
    """Parse roadmap markdown into a list of task dicts.

    Each dict: {"id": int, "title": str, "phase": int, "steps": list[str]}
    Steps are the bold text from lines matching: - [ ] **...**
    """
    text = Path(file_path).read_text()
    tasks: list[dict] = []
    current_phase = 1
    current_task: dict | None = None

    for line in text.splitlines():
        phase_match = re.match(r"^## Phase (\d+):", line)
        if phase_match:
            current_phase = int(phase_match.group(1))
            continue

        task_match = re.match(r"^### Task (\d+): (.+)", line)
        if task_match:
            if current_task is not None:
                tasks.append(current_task)
            task_id = int(task_match.group(1))
            title = task_match.group(2).strip()
            current_task = {
                "id": task_id,
                "title": f"Task {task_id}: {title}",
                "phase": current_phase,
                "steps": [],
            }
            continue

        step_match = re.match(r"^- \[ \] \*\*(.+?)\*\*", line)
        if step_match and current_task is not None:
            current_task["steps"].append(step_match.group(1).strip())

    if current_task is not None:
        tasks.append(current_task)

    return tasks
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd ~/ck-x-simulator/study-companion
pytest tests/test_parser.py -v
```

Expected: all 5 tests PASS

- [ ] **Step 5: Verify parser works on actual roadmap**

```bash
cd ~/ck-x-simulator/study-companion
python -c "
from roadmap.parser import parse_roadmap
tasks = parse_roadmap('../docs/superpowers/plans/2026-03-29-devops-certification-roadmap.md')
print(f'Parsed {len(tasks)} tasks')
for t in tasks[:3]:
    print(f'  Task {t[\"id\"]} (phase {t[\"phase\"]}): {len(t[\"steps\"])} steps')
"
```

Expected: `Parsed 19 tasks` with step counts listed

- [ ] **Step 6: Commit**

```bash
cd ~/ck-x-simulator
git add study-companion/roadmap/ study-companion/tests/test_parser.py
git commit -m "feat: add roadmap markdown parser"
```

---

## Task 4: Mentor (Ollama)

**Files:**
- Create: `study-companion/bot/mentor.py`
- Create: `study-companion/tests/test_mentor.py`

- [ ] **Step 1: Write failing tests**

```python
# study-companion/tests/test_mentor.py
import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from bot.mentor import Mentor

@pytest.fixture
def mentor():
    return Mentor(host="http://localhost:11434", model="llama3.1:8b", timeout=10)

@pytest.mark.asyncio
async def test_explain_calls_ollama(mentor):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "message": {"content": "NetworkPolicy controls traffic between pods."}
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        result = await mentor.explain("NetworkPolicy", "Task 10: Networking", phase=2)

    assert "NetworkPolicy" in result or len(result) > 0

@pytest.mark.asyncio
async def test_hint_calls_ollama(mentor):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "message": {"content": "Think about how packets flow through iptables chains."}
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        result = await mentor.hint("Step 2: Understand iptables", "Task 10: Networking")

    assert len(result) > 0

@pytest.mark.asyncio
async def test_quiz_calls_ollama(mentor):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "message": {"content": "Q: What does iptables ACCEPT do? A) ... B) ... C) ... D) ..."}
    }
    mock_response.raise_for_status = MagicMock()

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.post = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        result = await mentor.quiz("Task 10: Networking", phase=2)

    assert len(result) > 0

@pytest.mark.asyncio
async def test_is_reachable_true_on_200(mentor):
    mock_response = MagicMock()
    mock_response.status_code = 200

    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(return_value=mock_response)
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        result = await mentor.is_reachable()

    assert result is True

@pytest.mark.asyncio
async def test_is_reachable_false_on_exception(mentor):
    with patch("httpx.AsyncClient") as mock_client_class:
        mock_client = AsyncMock()
        mock_client.get = AsyncMock(side_effect=Exception("connection refused"))
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=None)
        mock_client_class.return_value = mock_client

        result = await mentor.is_reachable()

    assert result is False
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
cd ~/ck-x-simulator/study-companion
pytest tests/test_mentor.py -v
```

Expected: `ModuleNotFoundError: No module named 'bot.mentor'`

- [ ] **Step 3: Implement bot/mentor.py**

```python
# study-companion/bot/mentor.py
import httpx

EXPLAIN_SYSTEM = (
    "You are a concise DevOps mentor. Answer in under 200 words. "
    "Use analogies from Linux and Kubernetes when helpful. Be direct and practical."
)

HINT_SYSTEM = (
    "You are a DevOps mentor giving a hint. Do NOT give the full answer. "
    "Give a directional nudge in 2-3 sentences maximum. Make the student think."
)

QUIZ_SYSTEM = (
    "You are a DevOps mentor creating a quiz. Generate exactly 1 multiple-choice question "
    "with options A, B, C, D. Do NOT reveal the answer yet — wait for the student to reply."
)


class Mentor:
    def __init__(self, host: str, model: str, timeout: int = 60):
        self.host = host.rstrip("/")
        self.model = model
        self.timeout = timeout

    async def _call(self, system: str, prompt: str) -> str:
        url = f"{self.host}/api/chat"
        payload = {
            "model": self.model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
        }
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            resp = await client.post(url, json=payload)
            resp.raise_for_status()
            return resp.json()["message"]["content"].strip()

    async def explain(self, topic: str, task_title: str, phase: int) -> str:
        prompt = (
            f"The student is on Phase {phase}, working on: {task_title}.\n"
            f"Explain this concept: {topic}"
        )
        return await self._call(EXPLAIN_SYSTEM, prompt)

    async def hint(self, step_content: str, task_title: str) -> str:
        prompt = (
            f"The student is working on: {task_title}\n"
            f"They are stuck on this step: {step_content}\n"
            f"Give a hint."
        )
        return await self._call(HINT_SYSTEM, prompt)

    async def quiz(self, task_title: str, phase: int) -> str:
        prompt = f"Phase {phase} topic — {task_title}. Generate a quiz question."
        return await self._call(QUIZ_SYSTEM, prompt)

    async def is_reachable(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.host}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
cd ~/ck-x-simulator/study-companion
pytest tests/test_mentor.py -v
```

Expected: all 5 tests PASS

- [ ] **Step 5: Commit**

```bash
cd ~/ck-x-simulator
git add study-companion/bot/mentor.py study-companion/tests/test_mentor.py
git commit -m "feat: add Ollama mentor with explain/hint/quiz modes"
```

---

## Task 5: Scheduler

**Files:**
- Create: `study-companion/bot/scheduler.py`

- [ ] **Step 1: Implement bot/scheduler.py**

```python
# study-companion/bot/scheduler.py
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
import pytz

logger = logging.getLogger(__name__)


def setup_scheduler(
    bot,
    state_manager,
    chat_id: str,
    morning_time: str,
    evening_time: str,
    timezone: str,
) -> AsyncIOScheduler:
    tz = pytz.timezone(timezone)
    scheduler = AsyncIOScheduler(timezone=tz)

    morning_h, morning_m = map(int, morning_time.split(":"))
    evening_h, evening_m = map(int, evening_time.split(":"))

    scheduler.add_job(
        _send_morning,
        CronTrigger(hour=morning_h, minute=morning_m, timezone=tz),
        args=[bot, state_manager, chat_id],
        id="morning_notification",
        replace_existing=True,
    )
    scheduler.add_job(
        _send_evening,
        CronTrigger(hour=evening_h, minute=evening_m, timezone=tz),
        args=[bot, state_manager, chat_id],
        id="evening_notification",
        replace_existing=True,
    )

    return scheduler


async def _send_morning(bot, state, chat_id: str) -> None:
    task = state.get_current_task()
    step = state.get_current_step()
    if not task:
        await bot.send_message(chat_id=chat_id, text="All tasks complete! Check /progress.")
        return
    step_text = (
        f"▸ {step['content']}" if step
        else "All steps in this task done — use /done to confirm."
    )
    msg = (
        f"Good morning!\n\n"
        f"Today's task: {task['title']}\n"
        f"Phase: {task['phase']}\n\n"
        f"Your next step:\n{step_text}\n\n"
        f"Type /hint if you need a nudge. Type /session start when you begin."
    )
    await bot.send_message(chat_id=chat_id, text=msg)


async def _send_evening(bot, state, chat_id: str) -> None:
    completed_today = state.get_steps_completed_today()
    task = state.get_current_task()
    step = state.get_current_step()

    if completed_today == 0:
        step_text = (
            f"▸ {step['content']}" if step
            else "check /today for your next step"
        )
        msg = (
            f"Hey — no progress logged today.\n\n"
            f"Your next step:\n{step_text}\n\n"
            f"Even 15 minutes counts. Type /session start to begin."
        )
    else:
        task_title = task["title"] if task else "roadmap complete"
        msg = (
            f"Nice work today — you completed {completed_today} step(s).\n\n"
            f"Current task: {task_title}\n\n"
            f"See you tomorrow."
        )
    await bot.send_message(chat_id=chat_id, text=msg)
```

- [ ] **Step 2: Verify scheduler module imports cleanly**

```bash
cd ~/ck-x-simulator/study-companion
python -c "from bot.scheduler import setup_scheduler; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
cd ~/ck-x-simulator
git add study-companion/bot/scheduler.py
git commit -m "feat: add APScheduler morning/evening notifications"
```

---

## Task 6: Bot Handlers

**Files:**
- Create: `study-companion/bot/handlers.py`

- [ ] **Step 1: Implement bot/handlers.py**

```python
# study-companion/bot/handlers.py
import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def cmd_today(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = context.bot_data["state"]
    task = state.get_current_task()
    if not task:
        await update.message.reply_text(
            "All tasks completed! Use /progress to review your journey."
        )
        return

    steps = state.get_task_steps(task["id"])
    lines = [f"Task: {task['title']}\nPhase {task['phase']}\n"]
    for s in steps:
        if s["status"] == "completed":
            icon = "✅"
        elif s["status"] == "skipped":
            icon = "⏭"
        else:
            icon = "⬜"
        lines.append(f"{icon} {s['content']}")

    await update.message.reply_text("\n".join(lines))


async def cmd_done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = context.bot_data["state"]
    step = state.get_current_step()
    if not step:
        await update.message.reply_text(
            "No pending step found. Use /today to check your task."
        )
        return

    next_step = state.complete_step(step["id"])
    if next_step:
        await update.message.reply_text(
            f"✅ Completed: {step['content']}\n\n"
            f"Next step:\n▸ {next_step['content']}"
        )
    else:
        task = state.get_current_task()
        if task:
            await update.message.reply_text(
                f"✅ Completed: {step['content']}\n\n"
                f"All steps done! Next task: {task['title']}"
            )
        else:
            await update.message.reply_text("✅ All tasks complete! Amazing work.")


async def cmd_progress(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = context.bot_data["state"]
    p = state.get_progress()
    task_title = p["current_task"]["title"] if p["current_task"] else "All complete!"
    msg = (
        f"Progress: {p['pct']}% ({p['done_steps']}/{p['total_steps']} steps)\n"
        f"Phase: {p['phase']}\n"
        f"Current task: {task_title}\n"
        f"Sessions completed: {p['total_sessions']}\n"
        f"Study streak: {p['streak']} day(s)"
    )
    await update.message.reply_text(msg)


async def cmd_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = context.bot_data["state"]
    args = context.args or []

    if not args:
        await update.message.reply_text(
            "Usage:\n/session start\n/session end [optional notes]"
        )
        return

    action = args[0].lower()

    if action == "start":
        active = state.get_active_session()
        if active:
            await update.message.reply_text(
                "Session already active. Use /session end first."
            )
            return
        task = state.get_current_task()
        task_id = task["id"] if task else 0
        state.start_session(task_id)
        await update.message.reply_text(
            "Session started. Good luck! Use /session end [notes] when done."
        )

    elif action == "end":
        active = state.get_active_session()
        if not active:
            await update.message.reply_text(
                "No active session. Use /session start first."
            )
            return
        notes = " ".join(args[1:]) if len(args) > 1 else ""
        duration = state.end_session(active["id"], notes)
        reply = f"Session ended. Duration: {duration} minute(s)."
        if notes:
            reply += f"\nNotes: {notes}"
        await update.message.reply_text(reply)

    else:
        await update.message.reply_text(
            "Usage:\n/session start\n/session end [optional notes]"
        )


async def cmd_explain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mentor = context.bot_data["mentor"]
    state = context.bot_data["state"]

    if not context.args:
        await update.message.reply_text(
            "Usage: /explain <topic>\nExample: /explain NetworkPolicy"
        )
        return

    if not await mentor.is_reachable():
        await update.message.reply_text(
            "Mentor offline — Ollama not reachable.\n"
            "Check: systemctl status ollama"
        )
        return

    topic = " ".join(context.args)
    task = state.get_current_task()
    task_title = task["title"] if task else "general DevOps"
    phase = task["phase"] if task else 1

    await update.message.reply_text("Thinking...")
    answer = await mentor.explain(topic, task_title, phase)
    await update.message.reply_text(answer)


async def cmd_hint(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mentor = context.bot_data["mentor"]
    state = context.bot_data["state"]

    if not await mentor.is_reachable():
        await update.message.reply_text(
            "Mentor offline — Ollama not reachable.\n"
            "Check: systemctl status ollama"
        )
        return

    step = state.get_current_step()
    if not step:
        await update.message.reply_text(
            "No active step. Use /today to check your task."
        )
        return

    task = state.get_current_task()
    task_title = task["title"] if task else "current task"

    await update.message.reply_text("Thinking...")
    hint = await mentor.hint(step["content"], task_title)
    await update.message.reply_text(hint)


async def cmd_quiz(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    mentor = context.bot_data["mentor"]
    state = context.bot_data["state"]

    if not await mentor.is_reachable():
        await update.message.reply_text(
            "Mentor offline — Ollama not reachable.\n"
            "Check: systemctl status ollama"
        )
        return

    task = state.get_current_task()
    if not task:
        await update.message.reply_text(
            "No active task. Use /progress to check your state."
        )
        return

    await update.message.reply_text("Generating quiz question...")
    question = await mentor.quiz(task["title"], task["phase"])
    await update.message.reply_text(question)


async def cmd_skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    state = context.bot_data["state"]
    step = state.get_current_step()
    if not step:
        await update.message.reply_text("No pending step to skip.")
        return

    reason = " ".join(context.args) if context.args else "no reason given"
    next_step = state.skip_step(step["id"], reason)

    msg = f"⏭ Skipped: {step['content']}\nReason: {reason}\n\n"
    if next_step:
        msg += f"Next step:\n▸ {next_step['content']}"
    else:
        msg += "No more steps in current task."
    await update.message.reply_text(msg)
```

- [ ] **Step 2: Verify handlers module imports cleanly**

```bash
cd ~/ck-x-simulator/study-companion
python -c "from bot.handlers import cmd_today, cmd_done; print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
cd ~/ck-x-simulator
git add study-companion/bot/handlers.py
git commit -m "feat: add Telegram command handlers"
```

---

## Task 7: Main Entry Point

**Files:**
- Create: `study-companion/bot/main.py`

- [ ] **Step 1: Implement bot/main.py**

```python
# study-companion/bot/main.py
import logging
import os
import yaml
from telegram.ext import Application, CommandHandler
from state.manager import StateManager
from roadmap.parser import parse_roadmap
from bot.mentor import Mentor
from bot.scheduler import setup_scheduler
from bot import handlers

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


def load_config(path: str = "/app/config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def main() -> None:
    config = load_config()

    token = os.environ["TELEGRAM_BOT_TOKEN"]
    chat_id = os.environ["TELEGRAM_CHAT_ID"]
    db_path = "/app/data/state.db"

    state = StateManager(db_path)
    state.init_db()

    if not state.is_seeded():
        logger.info("Seeding database from roadmap...")
        tasks = parse_roadmap(config["roadmap"]["plan_file"])
        state.seed_tasks(tasks)
        logger.info("Seeded %d tasks", len(tasks))
    else:
        logger.info("Database already seeded, skipping")

    mentor = Mentor(
        host=config["ollama"]["host"],
        model=config["ollama"]["model"],
        timeout=config["ollama"]["timeout_seconds"],
    )

    app = Application.builder().token(token).build()
    app.bot_data["state"] = state
    app.bot_data["mentor"] = mentor
    app.bot_data["chat_id"] = chat_id

    app.add_handler(CommandHandler("today", handlers.cmd_today))
    app.add_handler(CommandHandler("done", handlers.cmd_done))
    app.add_handler(CommandHandler("progress", handlers.cmd_progress))
    app.add_handler(CommandHandler("session", handlers.cmd_session))
    app.add_handler(CommandHandler("explain", handlers.cmd_explain))
    app.add_handler(CommandHandler("hint", handlers.cmd_hint))
    app.add_handler(CommandHandler("quiz", handlers.cmd_quiz))
    app.add_handler(CommandHandler("skip", handlers.cmd_skip))

    scheduler = setup_scheduler(
        bot=app.bot,
        state_manager=state,
        chat_id=chat_id,
        morning_time=config["notifications"]["morning_time"],
        evening_time=config["notifications"]["evening_time"],
        timezone=config["notifications"]["timezone"],
    )

    async def on_startup(application: Application) -> None:
        scheduler.start()
        logger.info("Scheduler started")

    async def on_shutdown(application: Application) -> None:
        scheduler.shutdown(wait=False)

    app.post_init = on_startup
    app.post_shutdown = on_shutdown

    logger.info("Bot starting...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify main module imports cleanly (without running it)**

```bash
cd ~/ck-x-simulator/study-companion
python -c "import bot.main; print('OK')"
```

Expected: `OK` (will fail at runtime without env vars, but imports must succeed)

- [ ] **Step 3: Commit**

```bash
cd ~/ck-x-simulator
git add study-companion/bot/main.py
git commit -m "feat: add main entry point wiring all components"
```

---

## Task 8: Docker Compose Integration

**Files:**
- Modify: `docker-compose.yml`

- [ ] **Step 1: Read current docker-compose.yml**

```bash
cat ~/ck-x-simulator/docker-compose.yml
```

- [ ] **Step 2: Add study-companion service**

Add the following service block to the `services:` section in `docker-compose.yml` (before the `networks:` block):

```yaml
  study-companion:
    build:
      context: ./study-companion
    volumes:
      - ./study-companion/data:/app/data
      - ./docs:/app/docs:ro
    env_file:
      - ./study-companion/.env
    extra_hosts:
      - "host.docker.internal:host-gateway"
    restart: unless-stopped
    deploy:
      resources:
        limits:
          cpus: "0.3"
          memory: 256M
        reservations:
          cpus: "0.1"
          memory: 128M
    networks:
      - ckx-network
```

- [ ] **Step 3: Verify docker-compose.yml is valid**

```bash
cd ~/ck-x-simulator
docker compose config --quiet && echo "Valid"
```

Expected: `Valid`

- [ ] **Step 4: Commit**

```bash
cd ~/ck-x-simulator
git add docker-compose.yml
git commit -m "feat: add study-companion service to docker-compose"
```

---

## Task 9: First Run Setup

**One-time setup steps to get the bot running.**

- [ ] **Step 1: Create a Telegram bot via BotFather**

Open Telegram → search `@BotFather` → send `/newbot` → follow prompts.
Save the token you receive.

- [ ] **Step 2: Get your Telegram Chat ID**

Send any message to your new bot, then open this URL in a browser (replace TOKEN):
```
https://api.telegram.org/bot<TOKEN>/getUpdates
```
Find `"chat":{"id":XXXXXXXX}` in the response. Save that number.

- [ ] **Step 3: Create .env file**

```bash
cat > ~/ck-x-simulator/study-companion/.env << 'EOF'
TELEGRAM_BOT_TOKEN=paste_your_token_here
TELEGRAM_CHAT_ID=paste_your_chat_id_here
EOF
```

- [ ] **Step 4: Install and start Ollama on host**

```bash
curl -fsSL https://ollama.com/install.sh | sh
systemctl status ollama   # verify running
ollama pull llama3.1:8b   # ~4GB download, wait for completion
ollama run llama3.1:8b "say hello"   # verify it responds
```

- [ ] **Step 5: Build and start study-companion**

```bash
cd ~/ck-x-simulator
docker compose build study-companion
docker compose up -d study-companion
docker compose logs -f study-companion
```

Expected log output:
```
Seeding database from roadmap...
Seeded 19 tasks
Scheduler started
Bot starting...
```

- [ ] **Step 6: Verify bot responds**

Open Telegram → your bot → send `/today`

Expected: bot replies with current task and steps.

- [ ] **Step 7: Run full test suite**

```bash
cd ~/ck-x-simulator/study-companion
pytest tests/ -v
```

Expected: all tests PASS

- [ ] **Step 8: Final commit**

```bash
cd ~/ck-x-simulator
git add study-companion/.env.example
git commit -m "docs: add .env.example for study-companion setup"
```

---

## Self-Review Notes

**Spec coverage:**
- ✅ Telegram bot with all 8 commands
- ✅ Morning 07:00 + conditional evening 19:00 notifications
- ✅ Step-level checkpoints via `/done` and `/skip`
- ✅ Session logging via `/session start` / `/session end`
- ✅ Ollama explain/hint/quiz modes
- ✅ Roadmap markdown parser seeding SQLite on first run
- ✅ Docker service with host.docker.internal bridge to Ollama
- ✅ config.yaml for timezone, model, notification times
- ✅ Error handling: Ollama offline, no active task, no active session

**Type consistency:**
- `StateManager.get_current_task()` → `dict | None` — consistent across handlers and scheduler
- `StateManager.complete_step(step_id: int)` → `dict | None` — consistent
- `Mentor.explain/hint/quiz` → all `async def ... -> str` — consistent
- `context.bot_data["state"]` key used identically in all handlers — consistent
