# main.py
"""
Smart Study Planner — Application Entry Point

Wires together every component and launches the GUI.
Run:  python main.py
"""

from __future__ import annotations
import customtkinter as ctk

from config import APP_TITLE, APP_GEOMETRY, AppleTheme, FONT_HEADING, FONT_SUBHEAD, FONT_BODY
from models.task import Task, TaskManager
from storage.json import save_tasks, load_tasks
from scheduler.planner import generate_daily_plan
from tracker.progress import ProgressTracker, ProgressWidget
from gui.task_form import open_add_form, open_edit_form
from gui.plan_picker import open_plan_picker
from gui.task_list import TaskListFrame
from gui.schedule_view import ScheduleFrame


class StudyPlannerApp(ctk.CTk):
    """Main application window — ties all components together."""

    def __init__(self):
        super().__init__()
        self.configure(fg_color=AppleTheme.BG_BASE)
        self.title(APP_TITLE)
        self.geometry(APP_GEOMETRY)
        self.minsize(960, 620)

        # ── Core objects ──────────────────────────────────────────────────
        self.manager = TaskManager()
        self.manager.load(load_tasks())
        self.tracker = ProgressTracker(self.manager)
        self._current_slots = []

        # ── Layout ────────────────────────────────────────────────────────
        self._stats = {}
        self._build_ui()

    # ── UI construction ───────────────────────────────────────────────────

    def _build_ui(self):
        self.root = ctk.CTkFrame(
            self,
            fg_color=AppleTheme.SURFACE_BASE,
            corner_radius=28,
            border_width=1,
            border_color=AppleTheme.BORDER_DEFAULT,
        )
        self.root.pack(fill="both", expand=True, padx=16, pady=16)

        # Header / dashboard strip
        hero = ctk.CTkFrame(
            self.root,
            fg_color=AppleTheme.SURFACE_RAISED,
            corner_radius=24,
            border_width=1,
            border_color=AppleTheme.BORDER_DEFAULT,
        )
        hero.pack(fill="x", padx=14, pady=(14, 10))

        accent = ctk.CTkFrame(hero, fg_color=AppleTheme.ACCENT, height=4, corner_radius=999)
        accent.pack(fill="x", padx=18, pady=(18, 0))

        hero_row = ctk.CTkFrame(hero, fg_color="transparent")
        hero_row.pack(fill="x", padx=18, pady=(12, 8))

        left = ctk.CTkFrame(hero_row, fg_color="transparent")
        left.pack(side="left", fill="x", expand=True)

        ctk.CTkLabel(
            left,
            text="Today",
            text_color=AppleTheme.TEXT_SECONDARY,
            font=FONT_BODY,
        ).pack(anchor="w")
        ctk.CTkLabel(
            left,
            text=APP_TITLE,
            text_color=AppleTheme.TEXT_PRIMARY,
            font=ctk.CTkFont(size=30, weight="bold"),
        ).pack(anchor="w", pady=(2, 2))
        ctk.CTkLabel(
            left,
            text="Plan your study blocks, track completion, and keep the next task in view.",
            text_color=AppleTheme.TEXT_SECONDARY,
            font=FONT_SUBHEAD,
        ).pack(anchor="w")

        right = ctk.CTkFrame(hero_row, fg_color="transparent")
        right.pack(side="right", anchor="n")

        ctk.CTkButton(
            right,
            text="+ Add Task",
            command=self._on_add_task,
            width=140,
            height=38,
            fg_color=AppleTheme.ACCENT,
            hover_color=AppleTheme.ACCENT_HOVER,
            text_color="#FFFFFF",
            corner_radius=999,
        ).pack(anchor="e")

        self.progress_widget = ProgressWidget(right, self.tracker)
        self.progress_widget.pack(anchor="e", pady=(12, 0))

        self.summary_strip = ctk.CTkFrame(hero, fg_color="transparent")
        self.summary_strip.pack(fill="x", padx=18, pady=(0, 18))

        self.total_card = self._make_stat_card(self.summary_strip, "Total tasks", "0")
        self.done_card = self._make_stat_card(self.summary_strip, "Completed", "0")
        self.pending_card = self._make_stat_card(self.summary_strip, "Pending", "0")

        self.total_card.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.done_card.pack(side="left", fill="x", expand=True, padx=8)
        self.pending_card.pack(side="left", fill="x", expand=True, padx=(8, 0))

        # Main content: left = task list, right = schedule
        body = ctk.CTkFrame(self.root, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=14, pady=(0, 14))

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

        self._refresh_stats()

    def _make_stat_card(self, parent, label: str, value: str) -> ctk.CTkFrame:
        card = ctk.CTkFrame(
            parent,
            fg_color=AppleTheme.SURFACE_BASE,
            corner_radius=18,
            border_width=1,
            border_color=AppleTheme.BORDER_DEFAULT,
        )
        ctk.CTkLabel(
            card,
            text=label,
            text_color=AppleTheme.TEXT_SECONDARY,
            font=FONT_BODY,
        ).pack(anchor="w", padx=14, pady=(12, 0))
        stat_value = ctk.CTkLabel(
            card,
            text=value,
            text_color=AppleTheme.TEXT_PRIMARY,
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        stat_value.pack(anchor="w", padx=14, pady=(2, 12))
        card._stat_value = stat_value
        return card

    def _refresh_stats(self):
        stats = self.tracker.get_stats()
        total = stats["total"]
        done = stats["done"]
        pending = total - done
        self.total_card._stat_value.configure(text=str(total))
        self.done_card._stat_value.configure(text=str(done))
        self.pending_card._stat_value.configure(text=str(pending))
        self._stats = stats

    # ── Callbacks ─────────────────────────────────────────────────────────

    def _refresh_all(self):
        """Refresh every widget and persist data to disk."""
        save_tasks(self.manager.get_all())
        self.task_list.refresh(self.manager.get_all())
        self.progress_widget.refresh()
        self._refresh_stats()

    def _invalidate_plan(self):
        self._current_slots = []
        self.schedule_view.refresh([])

    def _sync_current_slots(self):
        current_state = {task.id: task.is_done for task in self.manager.get_all()}
        for slot in self._current_slots:
            slot.is_done = current_state.get(slot.task_id, slot.is_done)

    def _on_add_task(self):
        open_add_form(self, self.manager, lambda: (self._refresh_all(), self._invalidate_plan()))

    def _on_edit_task(self, task: Task):
        open_edit_form(self, self.manager, task, lambda: (self._refresh_all(), self._invalidate_plan()))

    def _on_delete_task(self, task_id: str):
        self.manager.delete_task(task_id)
        self._refresh_all()
        self._invalidate_plan()

    def _on_generate_plan(self):
        pending = [task for task in self.manager.get_all() if not task.is_done]

        def _confirm(selected_ids: set[str]):
            self._current_slots = generate_daily_plan(
                self.manager.get_all(),
                task_ids=selected_ids,
            )
            self._sync_current_slots()
            self.schedule_view.refresh(self._current_slots)

        open_plan_picker(self, pending, _confirm)

    def _on_mark_done(self, task_id: str, done: bool):
        self.tracker.mark_done(task_id, done)
        self._sync_current_slots()
        self._refresh_all()
        if self._current_slots:
            self.schedule_view.refresh(self._current_slots)


def main():
    ctk.set_appearance_mode("system")
    app = StudyPlannerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
