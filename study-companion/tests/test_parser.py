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
    for task in tasks:
        for step in task["steps"]:
            assert "```" not in step
            assert "**" not in step
