from __future__ import annotations
import json
import shutil
from pathlib import Path
from models.task import Task
from config import DATA_FILE, BACKUP_FILE


def save_tasks(tasks: list[Task]) -> None:
    """
    Serializes all tasks to DATA_FILE (data.json).
    Creates a backup (data.bak.json) before overwriting.

    Called by Dev 8 (main.py) whenever the task list changes.
    """
    data_path   = Path(DATA_FILE)
    backup_path = Path(BACKUP_FILE)

    # Back up existing file before overwriting
    if data_path.exists():
        shutil.copy2(data_path, backup_path)

    payload = [task.to_dict() for task in tasks]

    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)


def load_tasks() -> list[Task]:
    """
    Reads DATA_FILE and returns a list of Task objects.
    Returns an empty list if the file doesn't exist or is malformed.

    Called once on startup by Dev 8 (main.py).
    """
    data_path = Path(DATA_FILE)

    if not data_path.exists():
        return []

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        return [Task.from_dict(item) for item in raw]
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"[storage] Warning: could not load {DATA_FILE}: {e}")
        return []


### How to test your module in isolation

# Run from repo root:  python -m storage.json_store
if __name__ == "__main__":
    from datetime import date, timedelta
    from models.task import Task, TaskManager

    mgr = TaskManager()
    mgr.add_task("Finals prep", "Math", date.today() + timedelta(days=4), 3.0, 3)
    mgr.add_task("Essay draft", "English", date.today() + timedelta(days=2), 2.0, 2)

    save_tasks(mgr.get_all())
    print("Saved.")

    loaded = load_tasks()
    print(f"Loaded {len(loaded)} tasks:")
    for t in loaded:
        print(f"  {t.title} | {t.subject} | done={t.is_done}")