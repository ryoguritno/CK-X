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
