# tests/test_tracker.py
"""
Unit tests for tracker.progress — ProgressTracker (logic only, no GUI).

We mock save_tasks so tests don't touch the filesystem,
and mock customtkinter so tests run without a display server.
"""

import sys
import types
import unittest
from datetime import date, timedelta
from unittest.mock import patch, MagicMock

# ── Stub out dependencies before importing tracker.progress ───────────
# The module imports customtkinter at the top level for ProgressWidget.
# We only test ProgressTracker (pure logic), so fake modules are enough.
_ctk_stub = types.ModuleType("customtkinter")
_ctk_stub.CTkFrame = MagicMock
_ctk_stub.CTkProgressBar = MagicMock
_ctk_stub.CTkLabel = MagicMock
_ctk_stub.CTkFont = MagicMock
sys.modules.setdefault("customtkinter", _ctk_stub)

# tracker.progress imports from storage.json_store which may not exist
# (the actual file is storage/json.py). Provide a stub with save_tasks.
_json_store_stub = types.ModuleType("storage.json_store")
_json_store_stub.save_tasks = MagicMock()
sys.modules.setdefault("storage.json_store", _json_store_stub)

from models.task import Task, TaskManager
from tracker.progress import ProgressTracker


# ── Helper ────────────────────────────────────────────────────────────────

def _future(days: int = 3) -> date:
    return date.today() + timedelta(days=days)


def _populated_manager() -> TaskManager:
    mgr = TaskManager()
    mgr.add_task("Essay",    "English", _future(2), 2.0, 3)
    mgr.add_task("Calc HW", "Math",    _future(5), 1.5, 2)
    mgr.add_task("Reading",  "English", _future(4), 1.0, 1)
    return mgr


class TestProgressTracker(unittest.TestCase):

    def setUp(self):
        self.mgr = _populated_manager()
        self.tracker = ProgressTracker(self.mgr)

    # -- mark_done --

    @patch("tracker.progress.save_tasks")
    def test_mark_done_persists(self, mock_save):
        task = self.mgr.get_all()[0]
        self.tracker.mark_done(task.id, True)
        self.assertTrue(task.is_done)
        mock_save.assert_called_once()

    @patch("tracker.progress.save_tasks")
    def test_mark_undone(self, mock_save):
        task = self.mgr.get_all()[0]
        task.is_done = True
        self.tracker.mark_done(task.id, False)
        self.assertFalse(task.is_done)

    # -- get_stats --

    def test_stats_total(self):
        stats = self.tracker.get_stats()
        self.assertEqual(stats["total"], 3)

    def test_stats_done_zero_initially(self):
        stats = self.tracker.get_stats()
        self.assertEqual(stats["done"], 0)
        self.assertAlmostEqual(stats["percent"], 0.0)

    @patch("tracker.progress.save_tasks")
    def test_stats_after_marking_done(self, _):
        task = self.mgr.get_all()[0]
        self.tracker.mark_done(task.id, True)
        stats = self.tracker.get_stats()
        self.assertEqual(stats["done"], 1)
        self.assertAlmostEqual(stats["percent"], 100 / 3, places=1)

    def test_stats_by_subject(self):
        stats = self.tracker.get_stats()
        by_sub = stats["by_subject"]
        self.assertEqual(by_sub["English"]["total"], 2)
        self.assertEqual(by_sub["Math"]["total"], 1)

    @patch("tracker.progress.save_tasks")
    def test_stats_by_subject_done(self, _):
        task = self.mgr.get_all()[0]   # "Essay" — English
        self.tracker.mark_done(task.id, True)
        stats = self.tracker.get_stats()
        self.assertEqual(stats["by_subject"]["English"]["done"], 1)
        self.assertEqual(stats["by_subject"]["Math"]["done"], 0)

    def test_stats_empty_manager(self):
        empty_mgr = TaskManager()
        tracker = ProgressTracker(empty_mgr)
        stats = tracker.get_stats()
        self.assertEqual(stats["total"], 0)
        self.assertEqual(stats["done"], 0)
        self.assertAlmostEqual(stats["percent"], 0.0)
        self.assertEqual(stats["by_subject"], {})

    @patch("tracker.progress.save_tasks")
    def test_stats_all_done(self, _):
        for t in self.mgr.get_all():
            self.tracker.mark_done(t.id, True)
        stats = self.tracker.get_stats()
        self.assertEqual(stats["done"], stats["total"])
        self.assertAlmostEqual(stats["percent"], 100.0)


if __name__ == "__main__":
    unittest.main()
