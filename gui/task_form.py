# gui/task_form.py
from __future__ import annotations
import customtkinter as ctk
from datetime import date
from typing import Callable
from models.task import Task, TaskManager, ValidationError
from config import PRIORITY_LABELS, PRIORITY_VALUES


class TaskFormWindow(ctk.CTkToplevel):
    def __init__(self, parent, manager: TaskManager,
                 on_save: Callable, task: Task | None = None):
        super().__init__(parent)
        self.manager  = manager
        self.on_save  = on_save
        self.task     = task

        self.title("Edit Task" if task else "Add Task")
        self.geometry("420x420")
        self.resizable(False, False)
        self.grab_set()

        self._build_form()
        if task:
            self._populate(task)

    def _build_form(self):
        pad = {"padx": 20, "pady": 6}

        ctk.CTkLabel(self, text="Title").pack(anchor="w", **pad)
        self.title_var = ctk.StringVar()
        ctk.CTkEntry(self, textvariable=self.title_var, width=380).pack(**pad)
        self.err_title = ctk.CTkLabel(self, text="", text_color="red", font=("", 11))
        self.err_title.pack(anchor="w", padx=20)

        ctk.CTkLabel(self, text="Subject").pack(anchor="w", **pad)
        self.subject_var = ctk.StringVar()
        ctk.CTkEntry(self, textvariable=self.subject_var, width=380).pack(**pad)
        self.err_subject = ctk.CTkLabel(self, text="", text_color="red", font=("", 11))
        self.err_subject.pack(anchor="w", padx=20)

        ctk.CTkLabel(self, text="Deadline (YYYY-MM-DD)").pack(anchor="w", **pad)
        self.deadline_var = ctk.StringVar(value=date.today().isoformat())
        ctk.CTkEntry(self, textvariable=self.deadline_var, width=380).pack(**pad)
        self.err_deadline = ctk.CTkLabel(self, text="", text_color="red", font=("", 11))
        self.err_deadline.pack(anchor="w", padx=20)

        ctk.CTkLabel(self, text="Effort (hours)").pack(anchor="w", **pad)
        self.effort_var = ctk.StringVar(value="1.0")
        ctk.CTkEntry(self, textvariable=self.effort_var, width=380).pack(**pad)
        self.err_effort = ctk.CTkLabel(self, text="", text_color="red", font=("", 11))
        self.err_effort.pack(anchor="w", padx=20)

        ctk.CTkLabel(self, text="Priority").pack(anchor="w", **pad)
        self.priority_var = ctk.StringVar(value="Medium")
        ctk.CTkOptionMenu(self, variable=self.priority_var,
                          values=list(PRIORITY_VALUES.keys()),
                          width=380).pack(**pad)

        self.err_general = ctk.CTkLabel(self, text="", text_color="red", font=("", 11))
        self.err_general.pack(anchor="w", padx=20)

        ctk.CTkButton(self, text="Save", command=self._submit, width=380).pack(pady=16)

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