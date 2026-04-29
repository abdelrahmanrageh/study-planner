# gui/task_form.py
from __future__ import annotations
import customtkinter as ctk
from datetime import date
from typing import Callable
from models.task import Task, TaskManager, ValidationError
from config import PRIORITY_LABELS, PRIORITY_VALUES, AppleTheme


class TaskFormWindow(ctk.CTkToplevel):
    def __init__(self, parent, manager: TaskManager,
                 on_save: Callable, task: Task | None = None):
        super().__init__(parent)
        self.manager  = manager
        self.on_save  = on_save
        self.task     = task

        self.configure(fg_color=AppleTheme.BG_BASE)
        self.title("Edit Task" if task else "Add Task")
        self.geometry("560x680")
        self.resizable(False, False)
        self.transient(parent)

        self._build_form()
        if task:
            self._populate(task)

        self.after(50, self._activate_modal)

    def _activate_modal(self, _retries: int = 20):
        """
        Safely grab modal focus once the window is visible.

        wait_visibility() raises TclError on Linux if the window is destroyed
        before it finishes mapping, so we poll winfo_viewable() instead.
        """
        if not self.winfo_exists():
            return
        if self.winfo_viewable():
            self.lift()
            try:
                self.grab_set()
            except Exception:
                pass
        elif _retries > 0:
            # Window not yet visible — try again after one more event loop tick
            self.after(50, lambda: self._activate_modal(_retries - 1))

    def _build_form(self):
        shell = ctk.CTkFrame(
            self,
            fg_color=AppleTheme.SURFACE_BASE,
            corner_radius=24,
            border_width=1,
            border_color=AppleTheme.BORDER_DEFAULT,
        )
        shell.pack(fill="both", expand=True, padx=20, pady=20)

        content = ctk.CTkScrollableFrame(
            shell,
            fg_color="transparent",
            scrollbar_button_color=AppleTheme.TEXT_TERTIARY,
            scrollbar_button_hover_color=AppleTheme.TEXT_SECONDARY,
        )
        content.pack(fill="both", expand=True, padx=4, pady=(8, 4))

        footer = ctk.CTkFrame(shell, fg_color="transparent")
        footer.pack(fill="x", padx=24, pady=(0, 18))

        pad = {"padx": 24, "pady": 6}

        ctk.CTkLabel(content, text="Title", text_color=AppleTheme.TEXT_PRIMARY).pack(anchor="w", **pad)
        self.title_var = ctk.StringVar()
        ctk.CTkEntry(content, textvariable=self.title_var, width=380,
                     fg_color=AppleTheme.SURFACE_RAISED,
                     border_color=AppleTheme.BORDER_DEFAULT).pack(**pad)
        self.err_title = ctk.CTkLabel(content, text="", text_color=AppleTheme.DESTRUCTIVE, font=("", 11))
        self.err_title.pack(anchor="w", padx=24)

        ctk.CTkLabel(content, text="Subject", text_color=AppleTheme.TEXT_PRIMARY).pack(anchor="w", **pad)
        self.subject_var = ctk.StringVar()
        ctk.CTkEntry(content, textvariable=self.subject_var, width=380,
                     fg_color=AppleTheme.SURFACE_RAISED,
                     border_color=AppleTheme.BORDER_DEFAULT).pack(**pad)
        self.err_subject = ctk.CTkLabel(content, text="", text_color=AppleTheme.DESTRUCTIVE, font=("", 11))
        self.err_subject.pack(anchor="w", padx=24)

        ctk.CTkLabel(content, text="Deadline (YYYY-MM-DD)", text_color=AppleTheme.TEXT_PRIMARY).pack(anchor="w", **pad)
        self.deadline_var = ctk.StringVar(value=date.today().isoformat())
        ctk.CTkEntry(content, textvariable=self.deadline_var, width=380,
                     fg_color=AppleTheme.SURFACE_RAISED,
                     border_color=AppleTheme.BORDER_DEFAULT).pack(**pad)
        self.err_deadline = ctk.CTkLabel(content, text="", text_color=AppleTheme.DESTRUCTIVE, font=("", 11))
        self.err_deadline.pack(anchor="w", padx=24)

        ctk.CTkLabel(content, text="Effort (hours)", text_color=AppleTheme.TEXT_PRIMARY).pack(anchor="w", **pad)
        self.effort_var = ctk.StringVar(value="1.0")
        ctk.CTkEntry(content, textvariable=self.effort_var, width=380,
                     fg_color=AppleTheme.SURFACE_RAISED,
                     border_color=AppleTheme.BORDER_DEFAULT).pack(**pad)
        self.err_effort = ctk.CTkLabel(content, text="", text_color=AppleTheme.DESTRUCTIVE, font=("", 11))
        self.err_effort.pack(anchor="w", padx=24)

        ctk.CTkLabel(content, text="Priority", text_color=AppleTheme.TEXT_PRIMARY).pack(anchor="w", **pad)
        self.priority_var = ctk.StringVar(value="Medium")
        ctk.CTkOptionMenu(
            content,
            variable=self.priority_var,
            values=list(PRIORITY_VALUES.keys()),
            width=380,
            fg_color=AppleTheme.SURFACE_RAISED,
            button_color=AppleTheme.ACCENT,
            button_hover_color=AppleTheme.ACCENT_HOVER,
            dropdown_fg_color=AppleTheme.SURFACE_BASE,
            dropdown_text_color=AppleTheme.TEXT_PRIMARY,
            text_color=AppleTheme.TEXT_PRIMARY,
        ).pack(**pad)

        self.err_general = ctk.CTkLabel(content, text="", text_color=AppleTheme.DESTRUCTIVE, font=("", 11))
        self.err_general.pack(anchor="w", padx=24)

        ctk.CTkButton(
            footer,
            text="Save",
            command=self._submit,
            width=380,
            fg_color=AppleTheme.ACCENT,
            hover_color=AppleTheme.ACCENT_HOVER,
            text_color="#FFFFFF",
            corner_radius=999,
            height=38,
        ).pack(anchor="center")

    def _populate(self, task: Task):
        self.title_var.set(task.title)
        self.subject_var.set(task.subject)
        self.deadline_var.set(task.deadline.isoformat())
        self.effort_var.set(str(task.effort_hours))
        self.priority_var.set(PRIORITY_LABELS[task.priority])

    def _clear_errors(self):
        for lbl in (self.err_title, self.err_subject,
                    self.err_deadline, self.err_effort, self.err_general):
            lbl.configure(text="")

    def _submit(self):
        self._clear_errors()

        try:
            deadline = date.fromisoformat(self.deadline_var.get().strip())
        except ValueError:
            self.err_deadline.configure(text="Use YYYY-MM-DD format.")
            return

        try:
            effort = float(self.effort_var.get().strip())
        except ValueError:
            self.err_effort.configure(text="Must be a number, e.g. 2.5")
            return

        priority = PRIORITY_VALUES[self.priority_var.get()]

        try:
            if self.task:
                self.manager.edit_task(
                    self.task.id,
                    self.title_var.get(), self.subject_var.get(),
                    deadline, effort, priority
                )
            else:
                self.manager.add_task(
                    self.title_var.get(), self.subject_var.get(),
                    deadline, effort, priority
                )
        except ValidationError as e:
            self.err_general.configure(text=str(e))
            return

        self.on_save()
        self.destroy()


def open_add_form(parent, manager: TaskManager, on_save: Callable):
    TaskFormWindow(parent, manager, on_save)

def open_edit_form(parent, manager: TaskManager,
                   task: Task, on_save: Callable):
    TaskFormWindow(parent, manager, on_save, task=task)


if __name__ == "__main__":
    import customtkinter as ctk
    from models.task import TaskManager

    mgr = TaskManager()
    root = ctk.CTk()
    root.geometry("400x200")

    def on_save():
        print("Saved! Tasks:", [t.title for t in mgr.get_all()])

    ctk.CTkButton(root, text="Add Task",
                  command=lambda: open_add_form(root, mgr, on_save)).pack(pady=40)
    root.mainloop()