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
