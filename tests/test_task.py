# tests/test_task.py
"""
Unit tests for models.task — Task dataclass & TaskManager.
"""

import unittest
from datetime import date, timedelta

from models.task import Task, TaskManager, ValidationError


# ── Helper ────────────────────────────────────────────────────────────────

def _future(days: int = 3) -> date:
    """Return a date `days` in the future (avoids past-date validation errors)."""
    return date.today() + timedelta(days=days)


# ── Task dataclass tests ─────────────────────────────────────────────────

class TestTask(unittest.TestCase):

    def setUp(self):
        self.task = Task(
            title="Write essay",
            subject="English",
            deadline=_future(5),
            effort_hours=3.0,
            priority=3,
        )

    # -- basic fields --

    def test_fields_assigned(self):
        self.assertEqual(self.task.title, "Write essay")
        self.assertEqual(self.task.subject, "English")
        self.assertEqual(self.task.effort_hours, 3.0)
        self.assertEqual(self.task.priority, 3)
        self.assertFalse(self.task.is_done)

    def test_id_auto_generated(self):
        """Each Task gets a unique uuid by default."""
        t2 = Task("Other", "Math", _future(), 1.0, 1)
        self.assertNotEqual(self.task.id, t2.id)

    # -- days_until_deadline --

    def test_days_until_deadline_positive(self):
        self.assertEqual(self.task.days_until_deadline(), 5)

    def test_days_until_deadline_today(self):
        t = Task("X", "Y", date.today(), 1.0, 1)
        self.assertEqual(t.days_until_deadline(), 0)

    def test_days_until_deadline_overdue(self):
        t = Task("X", "Y", date.today() - timedelta(days=2), 1.0, 1)
        self.assertEqual(t.days_until_deadline(), -2)

    # -- urgency_score --

    def test_urgency_score_returns_float(self):
        self.assertIsInstance(self.task.urgency_score(), float)

    def test_higher_priority_means_higher_score(self):
        low  = Task("A", "S", _future(5), 2.0, 1)
        high = Task("B", "S", _future(5), 2.0, 3)
        self.assertGreater(high.urgency_score(), low.urgency_score())

    def test_closer_deadline_means_higher_score(self):
        far   = Task("A", "S", _future(10), 2.0, 2)
        close = Task("B", "S", _future(1),  2.0, 2)
        self.assertGreater(close.urgency_score(), far.urgency_score())

    # -- serialization round-trip --

    def test_to_dict_keys(self):
        d = self.task.to_dict()
        expected_keys = {"id", "title", "subject", "deadline",
                         "effort_hours", "priority", "is_done"}
        self.assertEqual(set(d.keys()), expected_keys)

    def test_to_dict_deadline_is_iso(self):
        d = self.task.to_dict()
        self.assertEqual(d["deadline"], self.task.deadline.isoformat())

    def test_from_dict_round_trip(self):
        d = self.task.to_dict()
        restored = Task.from_dict(d)
        self.assertEqual(restored.id, self.task.id)
        self.assertEqual(restored.title, self.task.title)
        self.assertEqual(restored.subject, self.task.subject)
        self.assertEqual(restored.deadline, self.task.deadline)
        self.assertEqual(restored.effort_hours, self.task.effort_hours)
        self.assertEqual(restored.priority, self.task.priority)
        self.assertEqual(restored.is_done, self.task.is_done)

    def test_from_dict_missing_is_done_defaults_false(self):
        d = self.task.to_dict()
        del d["is_done"]
        restored = Task.from_dict(d)
        self.assertFalse(restored.is_done)


# ── TaskManager tests ────────────────────────────────────────────────────

class TestTaskManager(unittest.TestCase):

    def setUp(self):
        self.mgr = TaskManager()

    # -- add --

    def test_add_task_returns_task(self):
        t = self.mgr.add_task("Essay", "English", _future(), 2.0, 3)
        self.assertIsInstance(t, Task)
        self.assertEqual(t.title, "Essay")

    def test_add_task_appears_in_get_all(self):
        self.mgr.add_task("A", "B", _future(), 1.0, 1)
        self.assertEqual(len(self.mgr.get_all()), 1)

    def test_add_task_strips_whitespace(self):
        t = self.mgr.add_task("  Essay   ", "  English  ", _future(), 2.0, 3)
        self.assertEqual(t.title, "Essay")
        self.assertEqual(t.subject, "English")

    # -- get --

    def test_get_by_id_found(self):
        t = self.mgr.add_task("X", "Y", _future(), 1.0, 1)
        self.assertIs(self.mgr.get_by_id(t.id), t)

    def test_get_by_id_not_found(self):
        self.assertIsNone(self.mgr.get_by_id("nonexistent"))

    def test_get_pending_excludes_done(self):
        t1 = self.mgr.add_task("A", "B", _future(), 1.0, 1)
        t2 = self.mgr.add_task("C", "D", _future(), 1.0, 2)
        t1.is_done = True
        pending = self.mgr.get_pending()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0].id, t2.id)

    # -- edit --

    def test_edit_task_updates_fields(self):
        t = self.mgr.add_task("Old", "Sub", _future(), 1.0, 1)
        new_dl = _future(10)
        self.mgr.edit_task(t.id, "New", "SubNew", new_dl, 5.0, 3)
        self.assertEqual(t.title, "New")
        self.assertEqual(t.subject, "SubNew")
        self.assertEqual(t.deadline, new_dl)
        self.assertEqual(t.effort_hours, 5.0)
        self.assertEqual(t.priority, 3)

    def test_edit_nonexistent_raises(self):
        with self.assertRaises(ValidationError):
            self.mgr.edit_task("nope", "T", "S", _future(), 1.0, 1)

    # -- delete --

    def test_delete_existing(self):
        t = self.mgr.add_task("X", "Y", _future(), 1.0, 1)
        self.assertTrue(self.mgr.delete_task(t.id))
        self.assertEqual(len(self.mgr.get_all()), 0)

    def test_delete_nonexistent_returns_false(self):
        self.assertFalse(self.mgr.delete_task("nope"))

    # -- set_done --

    def test_set_done_marks_done(self):
        t = self.mgr.add_task("X", "Y", _future(), 1.0, 1)
        self.mgr.set_done(t.id, True)
        self.assertTrue(t.is_done)

    def test_set_done_unmarks(self):
        t = self.mgr.add_task("X", "Y", _future(), 1.0, 1)
        t.is_done = True
        self.mgr.set_done(t.id, False)
        self.assertFalse(t.is_done)

    # -- load --

    def test_load_called_without_error(self):
        """load() is currently a stub — verify it can be called safely."""
        self.mgr.add_task("A", "B", _future(), 1.0, 1)
        new_tasks = [Task("Z", "W", _future(), 2.0, 2)]
        # Should not raise
        self.mgr.load(new_tasks)


# ── Validation tests ─────────────────────────────────────────────────────

class TestTaskValidation(unittest.TestCase):

    def test_empty_title_raises(self):
        with self.assertRaises(ValidationError):
            TaskManager.validate("", "Sub", _future(), 1.0, 1)

    def test_whitespace_only_title_raises(self):
        with self.assertRaises(ValidationError):
            TaskManager.validate("   ", "Sub", _future(), 1.0, 1)

    def test_empty_subject_raises(self):
        with self.assertRaises(ValidationError):
            TaskManager.validate("Title", "", _future(), 1.0, 1)

    def test_past_deadline_raises(self):
        with self.assertRaises(ValidationError):
            TaskManager.validate("T", "S", date.today() - timedelta(1), 1.0, 1)

    def test_zero_effort_raises(self):
        with self.assertRaises(ValidationError):
            TaskManager.validate("T", "S", _future(), 0, 1)

    def test_negative_effort_raises(self):
        with self.assertRaises(ValidationError):
            TaskManager.validate("T", "S", _future(), -2.0, 1)

    def test_invalid_priority_raises(self):
        with self.assertRaises(ValidationError):
            TaskManager.validate("T", "S", _future(), 1.0, 5)

    def test_valid_input_passes(self):
        # Should not raise
        TaskManager.validate("Title", "Subject", _future(), 2.0, 2)


if __name__ == "__main__":
    unittest.main()
