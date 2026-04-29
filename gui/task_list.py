from __future__ import annotations
import customtkinter as ctk
from typing import Callable
from textwrap import shorten
from pathlib import Path
from PIL import Image
from models.task import Task
from config import PRIORITY_LABELS, AppleTheme, FONT_HEADING, FONT_BODY

COLUMNS = ["Title", "Subject", "Deadline", "Effort (h)", "Priority", "Status", "Actions"]
COL_W   = [280,      180,       120,        100,          120,        100,      96]


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
        super().__init__(
            parent,
            fg_color=AppleTheme.SURFACE_BASE,
            corner_radius=21,
            border_width=1,
            border_color=AppleTheme.BORDER_DEFAULT,
        )
        self.on_edit   = on_edit
        self.on_delete = on_delete
        self._filter   = "All"

        # Load icon images from the project's assets folder and keep references
        # Keep both CTkImage and original PIL images to avoid GC issues.
        assets_dir = Path(__file__).resolve().parent.parent / "assets"
        self._icons = {}
        self._pil_images = {}

        edit_path = assets_dir / "edit.png"
        delete_path = assets_dir / "delete.png"

        for name, path in (("edit", edit_path), ("delete", delete_path)):
            try:
                if path.exists():
                    pil = Image.open(path).convert("RGBA")
                    # Resize/thumbnail for consistent CTkImage sizing
                    pil.thumbnail((18, 18), Image.LANCZOS)
                    self._pil_images[name] = pil
                    self._icons[name] = ctk.CTkImage(light_image=pil, dark_image=pil, size=(18, 18))
            except Exception:
                # If a single image fails, continue — we'll fall back to text buttons.
                pass


        self._build_toolbar()
        self._build_header()
        self._build_scroll_area()
        self.refresh(tasks)
        

        

    # ── Toolbar ───────────────────────────────────────────────────────────

    def _build_toolbar(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=14, pady=(14, 8))

        title_col = ctk.CTkFrame(header, fg_color="transparent")
        title_col.pack(side="left")
        ctk.CTkLabel(
            title_col,
            text="Tasks",
            text_color=AppleTheme.TEXT_PRIMARY,
            font=FONT_HEADING,
        ).pack(anchor="w")
        self.count_label = ctk.CTkLabel(
            title_col,
            text="",
            text_color=AppleTheme.TEXT_SECONDARY,
            font=FONT_BODY,
        )
        self.count_label.pack(anchor="w", pady=(2, 0))

        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=14, pady=(0, 2))
        ctk.CTkLabel(bar, text="Show:", text_color=AppleTheme.TEXT_SECONDARY).pack(side="left", padx=(0, 6))
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
        hdr.pack(fill="x", padx=12, pady=(6, 4))
        for column_index, (col, _) in enumerate(zip(COLUMNS, COL_W)):
            hdr.grid_columnconfigure(column_index, weight=1, uniform="taskcols")
            ctk.CTkLabel(
                hdr,
                text=col,
                font=ctk.CTkFont(weight="bold"),
                text_color=AppleTheme.TEXT_SECONDARY,
                anchor="w",
            ).grid(row=0, column=column_index, sticky="ew", padx=8, pady=2)

    # ── Scrollable body ───────────────────────────────────────────────────

    def _build_scroll_area(self):
        self.scroll = ctk.CTkScrollableFrame(self, height=400)
        self.scroll.pack(fill="both", expand=True, padx=8, pady=4)

    # ── Public API ────────────────────────────────────────────────────────


    def refresh(self, tasks: list[Task]):
        """Re-render the table with a new task list. Call after any change."""
        self._all_tasks = tasks
        self.count_label.configure(text=f"{len(tasks)} total tasks")

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
                         text_color=AppleTheme.TEXT_TERTIARY).pack(pady=20)
            return

        for task in visible:
            self._add_row(task)

    # ── Row builder ───────────────────────────────────────────────────────

    def _add_row(self, task: Task):
        row = ctk.CTkFrame(
            self.scroll,
            fg_color=AppleTheme.SURFACE_RAISED,
            corner_radius=18,
            border_width=1,
            border_color=AppleTheme.BORDER_DEFAULT,
        )
        row.pack(fill="x", pady=6, padx=2)

        for column_index, width in enumerate(COL_W):
            row.grid_columnconfigure(column_index, weight=1, uniform="taskcols")

        status_text  = "Done" if task.is_done else "Pending"
        priority_text = PRIORITY_LABELS.get(task.priority, str(task.priority))

        values = [
            self._truncate(task.title, 34),
            self._truncate(task.subject, 22),
            task.deadline.isoformat(),
            str(task.effort_hours),
        ]

        for column_index, (val, width) in enumerate(zip(values, COL_W[:4])):
            ctk.CTkLabel(
                row,
                text=val,
                anchor="w",
                width=width,
                height=26,
                text_color=AppleTheme.TEXT_PRIMARY,
            ).grid(row=0, column=column_index, sticky="ew", padx=10, pady=14)

        priority_pill = ctk.CTkFrame(
            row,
            fg_color=AppleTheme.FILL_SECONDARY,
            corner_radius=999,
            width=96,
            height=28,
        )
        priority_pill.grid(row=0, column=4, sticky="ew", padx=10, pady=12)
        ctk.CTkLabel(
            priority_pill,
            text=priority_text,
            text_color=AppleTheme.TEXT_PRIMARY,
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(expand=True)

        status_colors = AppleTheme.ACCENT if task.is_done else AppleTheme.FILL_PRIMARY
        status_text_color = "#FFFFFF" if task.is_done else AppleTheme.TEXT_PRIMARY
        status_pill = ctk.CTkFrame(
            row,
            fg_color=status_colors,
            corner_radius=999,
            width=96,
            height=28,
        )
        status_pill.grid(row=0, column=5, sticky="ew", padx=10, pady=12)
        ctk.CTkLabel(
            status_pill,
            text=status_text,
            text_color=status_text_color,
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(expand=True)

        # Action buttons
        btn_frame = ctk.CTkFrame(row, fg_color="transparent", width=COL_W[-1])
        btn_frame.grid(row=0, column=6, sticky="e", padx=10, pady=10)

        edit_img = self._icons.get("edit")
        delete_img = self._icons.get("delete")

        if edit_img:
            ctk.CTkButton(
                btn_frame,
                image=edit_img,
                text="",
                width=34,
                height=34,
                fg_color=AppleTheme.FILL_SECONDARY,
                hover_color=AppleTheme.FILL_PRIMARY,
                corner_radius=10,
                command=lambda t=task: self.on_edit(t),
            ).pack(side="left", padx=6)
        else:
            ctk.CTkButton(
                btn_frame,
                text="✎",
                width=30,
                height=30,
                fg_color=AppleTheme.FILL_SECONDARY,
                hover_color=AppleTheme.FILL_PRIMARY,
                text_color=AppleTheme.TEXT_PRIMARY,
                font=ctk.CTkFont(size=15, weight="bold"),
                corner_radius=999,
                command=lambda t=task: self.on_edit(t),
            ).pack(side="left", padx=2)

        if delete_img:
            ctk.CTkButton(
                btn_frame,
                image=delete_img,
                text="",
                width=34,
                height=34,
                fg_color=AppleTheme.DESTRUCTIVE,
                hover_color=AppleTheme.DESTRUCTIVE_HOVER,
                corner_radius=10,
                command=lambda t=task: self.on_delete(t.id),
            ).pack(side="left", padx=6)
        else:
            ctk.CTkButton(
                btn_frame,
                text="🗑",
                width=30,
                height=30,
                fg_color=AppleTheme.DESTRUCTIVE,
                hover_color=AppleTheme.DESTRUCTIVE_HOVER,
                text_color="#FFFFFF",
                font=ctk.CTkFont(size=14, weight="bold"),
                corner_radius=999,
                command=lambda t=task: self.on_delete(t.id),
            ).pack(side="left", padx=2)

    @staticmethod
    def _truncate(text: str, max_chars: int) -> str:
        return shorten(text, width=max_chars, placeholder="…")
        

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