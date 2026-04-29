# main.py
"""
Smart Study Planner — Application Entry Point

Wires together every component and launches the GUI.
Run:  python main.py
"""

from __future__ import annotations
import customtkinter as ctk

from config import APP_TITLE, APP_GEOMETRY
from models.task import Task, TaskManager
from storage.json import save_tasks, load_tasks
from scheduler.planner import generate_daily_plan
from tracker.progress import ProgressTracker, ProgressWidget
from gui.task_form import open_add_form, open_edit_form
from gui.task_list import TaskListFrame
from gui.schedule_view import ScheduleFrame


class StudyPlannerApp(ctk.CTk):
    """Main application window — ties all components together."""

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)

        # ── Core objects ──────────────────────────────────────────────────
        self.manager = TaskManager()
        self.manager.load(load_tasks())
        self.tracker = ProgressTracker(self.manager)

        # ── Layout ────────────────────────────────────────────────────────
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────

    def _build_ui(self):
        # Top bar: Add button + progress
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=12, pady=(12, 4))

        ctk.CTkButton(
            top, text="+ Add Task",
            command=self._on_add_task,
            width=130, height=34,
        ).pack(side="left")

        self.progress_widget = ProgressWidget(top, self.tracker)
        self.progress_widget.pack(side="right")

        # Main content: left = task list, right = schedule
        body = ctk.CTkFrame(self, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=12, pady=8)

        # Task list (left side, ~55 %)
        self.task_list = TaskListFrame(
            body,
            tasks=self.manager.get_all(),
            on_edit=self._on_edit_task,
            on_delete=self._on_delete_task,
        )
        self.task_list.pack(side="left", fill="both", expand=True, padx=(0, 6))

        # Schedule view (right side, ~45 %)
        self.schedule_view = ScheduleFrame(
            body,
            slots=[],
            on_generate=self._on_generate_plan,
            on_mark_done=self._on_mark_done,
        )
        self.schedule_view.pack(side="right", fill="both", expand=True, padx=(6, 0))

    # ── Callbacks ─────────────────────────────────────────────────────────

    def _refresh_all(self):
        """Refresh every widget and persist data to disk."""
        save_tasks(self.manager.get_all())
        self.task_list.refresh(self.manager.get_all())
        self.progress_widget.refresh()

    def _on_add_task(self):
        open_add_form(self, self.manager, self._refresh_all)

    def _on_edit_task(self, task: Task):
        open_edit_form(self, self.manager, task, self._refresh_all)

    def _on_delete_task(self, task_id: str):
        self.manager.delete_task(task_id)
        self._refresh_all()

    def _on_generate_plan(self):
        slots = generate_daily_plan(self.manager.get_all())
        self.schedule_view.refresh(slots)

    def _on_mark_done(self, task_id: str, done: bool):
        self.tracker.mark_done(task_id, done)
        self._refresh_all()
        # Re-generate the plan so the schedule updates too
        self._on_generate_plan()


def main():
    ctk.set_appearance_mode("light")
    app = StudyPlannerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
