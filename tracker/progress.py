from __future__ import annotations

import customtkinter as ctk

from models.task import TaskManager
from storage.json import save_tasks


class ProgressTracker:
	"""
	Wraps TaskManager to add done-marking with auto-save.

	Dev 6 (schedule view) calls mark_done() when a checkbox is ticked.
	Dev 8 (main.py) creates one shared instance and passes it around.
	"""

	def __init__(self, manager: TaskManager):
		self.manager = manager

	def mark_done(self, task_id: str, done: bool = True) -> None:
		"""Mark a task done/undone and immediately persist to disk."""
		self.manager.set_done(task_id, done)
		save_tasks(self.manager.get_all())

	def get_stats(self) -> dict:
		"""
		Returns:
			{
			  "total":      int,
			  "done":       int,
			  "percent":    float (0.0-100.0),
			  "by_subject": { "Math": {"total": 3, "done": 1}, ... }
			}
		"""
		tasks = self.manager.get_all()
		total = len(tasks)
		done = sum(1 for t in tasks if t.is_done)
		percent = (done / total * 100) if total else 0.0

		by_subject: dict[str, dict] = {}
		for t in tasks:
			subj = t.subject
			if subj not in by_subject:
				by_subject[subj] = {"total": 0, "done": 0}
			by_subject[subj]["total"] += 1
			if t.is_done:
				by_subject[subj]["done"] += 1

		return {
			"total": total,
			"done": done,
			"percent": percent,
			"by_subject": by_subject,
		}


class ProgressWidget(ctk.CTkFrame):
	"""
	Compact progress bar + summary label.
	Embed anywhere with: widget = ProgressWidget(parent, tracker)
	Call widget.refresh() after any done/undone action.
	"""

	def __init__(self, parent, tracker: ProgressTracker):
		super().__init__(parent, fg_color="transparent")
		self.tracker = tracker

		self.bar = ctk.CTkProgressBar(self, width=300)
		self.bar.pack(side="left", padx=(0, 12))

		self.label = ctk.CTkLabel(self, text="")
		self.label.pack(side="left")

		self.refresh()

	def refresh(self) -> None:
		stats = self.tracker.get_stats()
		pct = stats["percent"] / 100
		self.bar.set(pct)
		self.label.configure(
			text=(
				f"{stats['done']} of {stats['total']} tasks done "
				f"({stats['percent']:.0f}%)"
			)
		)


if __name__ == "__main__":
	import customtkinter as ctk
	from datetime import date, timedelta
	from models.task import TaskManager

	mgr = TaskManager()
	mgr.add_task("Essay", "English", date.today() + timedelta(days=2), 2.0, 3)
	mgr.add_task("Calc HW", "Math", date.today() + timedelta(days=3), 1.5, 2)
	mgr.add_task("Reading", "History", date.today() + timedelta(days=5), 1.0, 1)
	mgr.get_all()[0].is_done = True

	tracker = ProgressTracker(mgr)
	print(tracker.get_stats())

	root = ctk.CTk()
	root.geometry("500x100")
	w = ProgressWidget(root, tracker)
	w.pack(pady=30)
	root.mainloop()
