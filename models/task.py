from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
import uuid


@dataclass
class Task:
    """
    Central data model. All other modules import this.
    Do NOT add fields without announcing it to the team —
    it will break Dev 3 (JSON), Dev 5 (table columns), Dev 7 (stats).
    """
    title:         str
    subject:       str
    deadline:      date
    effort_hours:  float          # total hours needed to complete the task
    priority:      int            # 1 = Low, 2 = Medium, 3 = High
    id:            str  = field(default_factory=lambda: str(uuid.uuid4()))
    is_done:       bool = False

    def days_until_deadline(self) -> int:
        """Returns days remaining. Negative means overdue."""
        return (self.deadline - date.today()).days

    def urgency_score(self) -> float:
        """
        Higher score = schedule sooner.
        Formula weighs deadline proximity, priority level, and effort.
        Dev 2 calls this — do not change the formula without telling Dev 2.
        """
        days_left = max(self.days_until_deadline(), 0.5)   # avoid division by zero
        return (self.priority * 10) + (self.effort_hours / days_left)

    def to_dict(self) -> dict:
        """Serialize to dict for JSON storage. Dev 3 uses this."""
        return {
            "id":           self.id,
            "title":        self.title,
            "subject":      self.subject,
            "deadline":     self.deadline.isoformat(),       # "2025-06-15"
            "effort_hours": self.effort_hours,
            "priority":     self.priority,
            "is_done":      self.is_done,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Task:
        """Deserialize from JSON dict. Dev 3 uses this."""
        return cls(
            id           = data["id"],
            title        = data["title"],
            subject      = data["subject"],
            deadline     = date.fromisoformat(data["deadline"]),
            effort_hours = float(data["effort_hours"]),
            priority     = int(data["priority"]),
            is_done      = bool(data.get("is_done", False)),
        )


class ValidationError(Exception):
    """Raised by TaskManager when input is invalid."""
    pass


class TaskManager:
    """
    Manages the in-memory list of tasks.
    GUI modules call these methods — they do NOT touch self._tasks directly.
    """

    def __init__(self, tasks: list[Task] | None = None):
        self._tasks: list[Task] = tasks or []

    # ── Read ──────────────────────────────────────────────────────────────

    def get_all(self) -> list[Task]:
        return list(self._tasks)

    def get_by_id(self, task_id: str) -> Task | None:
        return next((t for t in self._tasks if t.id == task_id), None)

    def get_pending(self) -> list[Task]:
        return [t for t in self._tasks if not t.is_done]

    # ── Validate ──────────────────────────────────────────────────────────

    @staticmethod
    def validate(title: str, subject: str, deadline: date,
                 effort_hours: float, priority: int) -> None:
        """
        Raises ValidationError with a human-readable message.
        Call this before add or edit.
        """
        if not title or not title.strip():
            raise ValidationError("Title cannot be empty.")
        if not subject or not subject.strip():
            raise ValidationError("Subject cannot be empty.")
        if deadline < date.today():
            raise ValidationError("Deadline cannot be in the past.")
        if effort_hours <= 0:
            raise ValidationError("Effort must be greater than 0 hours.")
        if priority not in (1, 2, 3):
            raise ValidationError("Priority must be 1 (Low), 2 (Medium), or 3 (High).")

    # ── Write ─────────────────────────────────────────────────────────────

    def add_task(self, title: str, subject: str, deadline: date,
                 effort_hours: float, priority: int) -> Task:
        """Validates, creates, appends, and returns the new Task."""
        self.validate(title, subject, deadline, effort_hours, priority)
        task = Task(
            title        = title.strip(),
            subject      = subject.strip(),
            deadline     = deadline,
            effort_hours = effort_hours,
            priority     = priority,
        )
        self._tasks.append(task)
        return task

    def edit_task(self, task_id: str, title: str, subject: str,
                  deadline: date, effort_hours: float, priority: int) -> Task:
        """Validates and updates an existing task in place."""
        task = self.get_by_id(task_id)
        if task is None:
            raise ValidationError(f"No task found with id {task_id}.")
        self.validate(title, subject, deadline, effort_hours, priority)
        task.title        = title.strip()
        task.subject      = subject.strip()
        task.deadline     = deadline
        task.effort_hours = effort_hours
        task.priority     = priority
        return task

    def delete_task(self, task_id: str) -> bool:
        """Removes task by id. Returns True if found and removed."""
        task = self.get_by_id(task_id)
        if task:
            self._tasks.remove(task)
            return True
        return False

    def set_done(self, task_id: str, done: bool = True) -> None:
        """Marks a task done or undone. Dev 7 calls this."""
        task = self.get_by_id(task_id)
        if task:
            task.is_done = done

    def load(self, tasks: list[Task]) -> None:
        """Replace internal list (called by Dev 3 on startup)."""
        self._tasks = list(tasks)