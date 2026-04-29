from __future__ import annotations

import customtkinter as ctk

from config import AppleTheme
from models.task import Task


class PlanPickerDialog(ctk.CTkToplevel):
    def __init__(self, parent, tasks: list[Task], on_confirm):
        super().__init__(parent)
        self.tasks = tasks
        self.on_confirm = on_confirm
        self._vars: dict[str, ctk.BooleanVar] = {}

        self.configure(fg_color=AppleTheme.BG_BASE)
        self.title("Choose Tasks for Today")
        self.geometry("640x560")
        self.resizable(False, False)
        self.transient(parent)

        self._build_ui()
        self.after(50, self._activate_modal)

    def _activate_modal(self, _retries: int = 20):
        if not self.winfo_exists():
            return
        if self.winfo_viewable():
            self.lift()
            try:
                self.grab_set()
            except Exception:
                pass
        elif _retries > 0:
            self.after(50, lambda: self._activate_modal(_retries - 1))

    def _build_ui(self):
        shell = ctk.CTkFrame(
            self,
            fg_color=AppleTheme.SURFACE_BASE,
            corner_radius=24,
            border_width=1,
            border_color=AppleTheme.BORDER_DEFAULT,
        )
        shell.pack(fill="both", expand=True, padx=20, pady=20)

        header = ctk.CTkFrame(shell, fg_color="transparent")
        header.pack(fill="x", padx=18, pady=(18, 10))
        ctk.CTkLabel(
            header,
            text="Choose what to plan today",
            text_color=AppleTheme.TEXT_PRIMARY,
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Select the tasks you want the planner to build around.",
            text_color=AppleTheme.TEXT_SECONDARY,
            font=ctk.CTkFont(size=13, weight="normal"),
        ).pack(anchor="w", pady=(2, 0))

        tools = ctk.CTkFrame(shell, fg_color="transparent")
        tools.pack(fill="x", padx=18, pady=(0, 8))

        ctk.CTkButton(
            tools,
            text="Select All",
            width=110,
            height=32,
            fg_color=AppleTheme.FILL_SECONDARY,
            hover_color=AppleTheme.FILL_PRIMARY,
            text_color=AppleTheme.TEXT_PRIMARY,
            command=self._select_all,
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            tools,
            text="Clear",
            width=88,
            height=32,
            fg_color=AppleTheme.FILL_SECONDARY,
            hover_color=AppleTheme.FILL_PRIMARY,
            text_color=AppleTheme.TEXT_PRIMARY,
            command=self._clear_all,
        ).pack(side="left")

        self.scroll = ctk.CTkScrollableFrame(
            shell,
            fg_color="transparent",
            scrollbar_button_color=AppleTheme.TEXT_TERTIARY,
            scrollbar_button_hover_color=AppleTheme.TEXT_SECONDARY,
        )
        self.scroll.pack(fill="both", expand=True, padx=16, pady=(0, 10))

        if not self.tasks:
            ctk.CTkLabel(
                self.scroll,
                text="No pending tasks available.",
                text_color=AppleTheme.TEXT_TERTIARY,
                font=ctk.CTkFont(size=15, weight="normal"),
            ).pack(pady=40)
        else:
            for task in self.tasks:
                self._add_task_row(task)

        self.err = ctk.CTkLabel(shell, text="", text_color=AppleTheme.DESTRUCTIVE)
        self.err.pack(anchor="w", padx=18, pady=(0, 6))

        footer = ctk.CTkFrame(shell, fg_color="transparent")
        footer.pack(fill="x", padx=18, pady=(0, 18))

        ctk.CTkButton(
            footer,
            text="Cancel",
            width=110,
            height=38,
            fg_color=AppleTheme.FILL_SECONDARY,
            hover_color=AppleTheme.FILL_PRIMARY,
            text_color=AppleTheme.TEXT_PRIMARY,
            command=self.destroy,
        ).pack(side="right", padx=(8, 0))
        ctk.CTkButton(
            footer,
            text="Generate Plan",
            width=150,
            height=38,
            fg_color=AppleTheme.ACCENT,
            hover_color=AppleTheme.ACCENT_HOVER,
            text_color="#FFFFFF",
            command=self._confirm,
        ).pack(side="right")

    def _add_task_row(self, task: Task):
        row = ctk.CTkFrame(
            self.scroll,
            fg_color=AppleTheme.SURFACE_RAISED,
            corner_radius=18,
            border_width=1,
            border_color=AppleTheme.BORDER_DEFAULT,
        )
        row.pack(fill="x", pady=4, padx=2)

        row.grid_columnconfigure(0, weight=1)
        row.grid_columnconfigure(1, weight=0)

        text_col = ctk.CTkFrame(row, fg_color="transparent")
        text_col.grid(row=0, column=0, sticky="ew", padx=14, pady=12)
        ctk.CTkLabel(
            text_col,
            text=self._truncate(task.title, 34),
            text_color=AppleTheme.TEXT_PRIMARY,
            font=ctk.CTkFont(size=16, weight="bold"),
            anchor="w",
        ).pack(anchor="w")
        ctk.CTkLabel(
            text_col,
            text=f"{self._truncate(task.subject, 24)}  ·  {task.deadline.isoformat()}  ·  {task.effort_hours:g}h",
            text_color=AppleTheme.TEXT_SECONDARY,
            font=ctk.CTkFont(size=13, weight="normal"),
            anchor="w",
        ).pack(anchor="w", pady=(2, 0))

        self._vars[task.id] = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            row,
            text="",
            variable=self._vars[task.id],
            fg_color=AppleTheme.ACCENT,
            border_color=AppleTheme.BORDER_DEFAULT,
            width=24,
            height=24,
        ).grid(row=0, column=1, sticky="e", padx=14)

    def _select_all(self):
        for var in self._vars.values():
            var.set(True)

    def _clear_all(self):
        for var in self._vars.values():
            var.set(False)

    def _confirm(self):
        selected = {task_id for task_id, var in self._vars.items() if var.get()}
        if not selected:
            self.err.configure(text="Select at least one task.")
            return
        self.on_confirm(selected)
        self.destroy()

    @staticmethod
    def _truncate(text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text
        return text[: max_chars - 1].rstrip() + "…"


def open_plan_picker(parent, tasks: list[Task], on_confirm):
    PlanPickerDialog(parent, tasks, on_confirm)