from __future__ import annotations
import customtkinter as ctk
from typing import Callable
from models.task import Task
from config import PRIORITY_LABELS

COLUMNS = ["Title", "Subject", "Deadline", "Effort (h)", "Priority", "Status", "Actions"]
COL_W   = [200,      120,       100,        80,           80,         70,       120]


class TaskListFrame(ctk.CTkFrame):
    """
    Scrollable task table embedded in a parent frame.

    Args:
        parent:    Parent CTk widget.
        tasks:     Initial list of Task objects.
        on_edit:   Callback(task: Task) — called when Edit is clicked.
        on_delete: Callback(task_id: str) — called when Delete is clicked.
    """

    def __init__(self, parent, tasks: list[Task],
                 on_edit: Callable[[Task], None],
                 on_delete: Callable[[str], None]):
        super().__init__(parent)
        self.on_edit   = on_edit
        self.on_delete = on_delete
        self._filter   = "All"


        self._build_toolbar()
        self._build_header()
        self._build_scroll_area()
        self.refresh(tasks)

    # ── Toolbar ───────────────────────────────────────────────────────────

    def _build_toolbar(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=8, pady=(8, 0))
        ctk.CTkLabel(bar, text="Show:").pack(side="left", padx=(0, 6))
        self.filter_var = ctk.StringVar(value="All")
        ctk.CTkOptionMenu(bar, variable=self.filter_var,
                          values=["All", "Pending", "Done"],
                          width=120,
                          command=self._on_filter_change).pack(side="left")

    def _on_filter_change(self, _=None):
        self._filter = self.filter_var.get()
        self.refresh(self._all_tasks)

    # ── Header row ────────────────────────────────────────────────────────

    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=8, pady=4)
        for col, w in zip(COLUMNS, COL_W):
            ctk.CTkLabel(hdr, text=col, width=w,
                         font=ctk.CTkFont(weight="bold"),
                         anchor="w").pack(side="left", padx=2)

    # ── Scrollable body ───────────────────────────────────────────────────

    def _build_scroll_area(self):
        self.scroll = ctk.CTkScrollableFrame(self, height=400)
        self.scroll.pack(fill="both", expand=True, padx=8, pady=4)

    # ── Public API ────────────────────────────────────────────────────────


    def refresh(self, tasks: list[Task]):
        """Re-render the table with a new task list. Call after any change."""
        self._all_tasks = tasks

        # Apply filter
        if self._filter == "Pending":
            visible = [t for t in tasks if not t.is_done]
        elif self._filter == "Done":
            visible = [t for t in tasks if t.is_done]
        else:
            visible = tasks

        # Clear existing rows
        for widget in self.scroll.winfo_children():
            widget.destroy()

        if not visible:
            ctk.CTkLabel(self.scroll, text="No tasks to show.",
                         text_color="gray").pack(pady=20)
            return

        for task in visible:
            self._add_row(task)

    # ── Row builder ───────────────────────────────────────────────────────

    def _add_row(self, task: Task):
        row = ctk.CTkFrame(self.scroll, fg_color="transparent")
        row.pack(fill="x", pady=2)

        status_text  = "Done" if task.is_done else "Pending"
        priority_text = PRIORITY_LABELS.get(task.priority, str(task.priority))

        values = [
            task.title,
            task.subject,
            task.deadline.isoformat(),
            str(task.effort_hours),
            priority_text,
            status_text,
        ]

        for val, w in zip(values, COL_W):
            ctk.CTkLabel(row, text=val, width=w, anchor="w",
                         wraplength=w - 4).pack(side="left", padx=2)

        # Action buttons
        btn_frame = ctk.CTkFrame(row, fg_color="transparent", width=COL_W[-1])
        btn_frame.pack(side="left", padx=2)

        ctk.CTkButton(btn_frame, text="Edit", width=52, height=26,
                      command=lambda t=task: self.on_edit(t)).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame, text="Delete", width=58, height=26,
                      fg_color="#c0392b", hover_color="#922b21",
                      command=lambda t=task: self.on_delete(t.id)).pack(side="left", padx=2)
        

if __name__ == "__main__":
    import customtkinter as ctk
    from datetime import date, timedelta
    from models.task import Task

    sample = [
        Task("Write report", "CS",      date.today() + timedelta(2), 3.0, 3),
        Task("Read chapter", "History", date.today() + timedelta(5), 1.5, 1),
        Task("Problem set",  "Math",    date.today() + timedelta(1), 2.0, 2, is_done=True),
    ]

    root = ctk.CTk()
    root.geometry("900x400")
    frame = TaskListFrame(root, sample,
                          on_edit=lambda t: print("Edit:", t.title),
                          on_delete=lambda tid: print("Delete:", tid))
    frame.pack(fill="both", expand=True)
    root.mainloop()