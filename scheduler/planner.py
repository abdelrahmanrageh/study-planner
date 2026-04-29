from __future__ import annotations
from dataclasses import dataclass
from datetime import date
from models.task import Task
from config import WORK_START_HOUR, DAILY_HOURS


@dataclass
class Slot:
    """A scheduled time block assigned to one task."""
    task_id:        str
    task_title:     str
    subject:        str
    start_time:     str    # "09:00"
    end_time:       str    # "11:00"
    duration_hours: float
    is_done:        bool = False

    def display_range(self) -> str:
        return f"{self.start_time} – {self.end_time}"


def _fmt_time(hour_float: float) -> str:
    """Convert 9.5 → '09:30', 14.0 → '14:00'"""
    h = int(hour_float)
    m = int((hour_float - h) * 60)
    return f"{h:02d}:{m:02d}"


def generate_daily_plan(tasks: list[Task],
                        available_hours: float = DAILY_HOURS,
                        task_ids: set[str] | None = None) -> list[Slot]:
    """
    Sorts pending tasks by urgency score (highest first),
    then fills the day with time slots until available_hours is used up.

    Args:
        tasks:           All Task objects (done tasks are ignored).
        available_hours: Total study hours available today (default from config).

    Returns:
        List of Slot objects in time order, starting at WORK_START_HOUR.
    """
    pending = [t for t in tasks if not t.is_done]
    if task_ids is not None:
        pending = [t for t in pending if t.id in task_ids]

    # Sort by urgency score descending — Dev 1's formula drives this
    pending.sort(key=lambda t: t.urgency_score(), reverse=True)

    slots: list[Slot] = []
    current_hour = float(WORK_START_HOUR)
    hours_left   = available_hours

    for task in pending:
        if hours_left <= 0:
            break

        # Allocate either the full task effort or whatever time is left
        block = min(task.effort_hours, hours_left)

        slot = Slot(
            task_id        = task.id,
            task_title     = task.title,
            subject        = task.subject,
            start_time     = _fmt_time(current_hour),
            end_time       = _fmt_time(current_hour + block),
            duration_hours = block,
        )
        slots.append(slot)

        current_hour += block
        hours_left   -= block

    return slots

if __name__ == "__main__":
    from datetime import date, timedelta
    from models.task import Task

    tasks = [
        Task("Write essay",   "English", date.today() + timedelta(days=1), 3.0, 3),
        Task("Problem set",   "Math",    date.today() + timedelta(days=2), 2.0, 2),
        Task("Read chapter",  "History", date.today() + timedelta(days=5), 1.5, 1),
        Task("Lab report",    "CS",      date.today() + timedelta(days=1), 4.0, 3),
    ]

    plan = generate_daily_plan(tasks, available_hours=6)
    for s in plan:
        print(f"{s.display_range()}  |  {s.task_title} ({s.subject})  [{s.duration_hours}h]")