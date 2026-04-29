# tests/test_scheduler.py
"""
Unit tests for scheduler.planner — Slot, _fmt_time, generate_daily_plan.
"""

import unittest
from datetime import date, timedelta

from models.task import Task
from scheduler.planner import Slot, _fmt_time, generate_daily_plan
from config import WORK_START_HOUR, DAILY_HOURS


# ── Helper ────────────────────────────────────────────────────────────────

def _future(days: int = 3) -> date:
    return date.today() + timedelta(days=days)


def _make_task(title="Task", subject="Sub", days=3,
               effort=2.0, priority=2, done=False) -> Task:
    t = Task(title, subject, _future(days), effort, priority)
    t.is_done = done
    return t


# ── Slot tests ────────────────────────────────────────────────────────────

class TestSlot(unittest.TestCase):

    def test_display_range(self):
        s = Slot("id1", "Title", "Math", "09:00", "11:00", 2.0)
        self.assertEqual(s.display_range(), "09:00 – 11:00")

    def test_default_is_done_false(self):
        s = Slot("id1", "Title", "Math", "09:00", "11:00", 2.0)
        self.assertFalse(s.is_done)


# ── _fmt_time tests ───────────────────────────────────────────────────────

class TestFmtTime(unittest.TestCase):

    def test_whole_hour(self):
        self.assertEqual(_fmt_time(9.0), "09:00")

    def test_half_hour(self):
        self.assertEqual(_fmt_time(9.5), "09:30")

    def test_afternoon(self):
        self.assertEqual(_fmt_time(14.0), "14:00")

    def test_quarter_hour(self):
        self.assertEqual(_fmt_time(10.25), "10:15")

    def test_zero_hour(self):
        self.assertEqual(_fmt_time(0.0), "00:00")


# ── generate_daily_plan tests ────────────────────────────────────────────

class TestGenerateDailyPlan(unittest.TestCase):

    def test_empty_task_list(self):
        plan = generate_daily_plan([])
        self.assertEqual(plan, [])

    def test_all_done_tasks_produce_no_slots(self):
        tasks = [_make_task(done=True), _make_task(title="B", done=True)]
        plan = generate_daily_plan(tasks)
        self.assertEqual(plan, [])

    def test_single_task_fits(self):
        tasks = [_make_task(effort=3.0)]
        plan = generate_daily_plan(tasks, available_hours=6)
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0].duration_hours, 3.0)
        self.assertEqual(plan[0].start_time, _fmt_time(WORK_START_HOUR))

    def test_slots_are_contiguous(self):
        tasks = [
            _make_task("A", effort=2.0, priority=3),
            _make_task("B", effort=1.5, priority=1),
        ]
        plan = generate_daily_plan(tasks, available_hours=6)
        # Second slot should start where the first ended
        self.assertEqual(plan[1].start_time, plan[0].end_time)

    def test_total_duration_does_not_exceed_available(self):
        tasks = [
            _make_task("A", effort=5.0, priority=3),
            _make_task("B", effort=5.0, priority=2),
            _make_task("C", effort=5.0, priority=1),
        ]
        plan = generate_daily_plan(tasks, available_hours=8)
        total = sum(s.duration_hours for s in plan)
        self.assertLessEqual(total, 8.0)

    def test_higher_urgency_scheduled_first(self):
        far_low  = _make_task("Far-Low",  days=10, effort=2.0, priority=1)
        near_high = _make_task("Near-High", days=1,  effort=2.0, priority=3)
        plan = generate_daily_plan([far_low, near_high], available_hours=6)
        # Near-high should have a higher urgency score → scheduled first
        self.assertEqual(plan[0].task_title, "Near-High")

    def test_done_tasks_excluded(self):
        done_task = _make_task("Done", done=True, effort=2.0)
        pending   = _make_task("Pending", effort=1.0)
        plan = generate_daily_plan([done_task, pending], available_hours=6)
        titles = [s.task_title for s in plan]
        self.assertNotIn("Done", titles)
        self.assertIn("Pending", titles)

    def test_task_truncated_when_time_runs_out(self):
        tasks = [_make_task(effort=10.0)]
        plan = generate_daily_plan(tasks, available_hours=3)
        self.assertEqual(len(plan), 1)
        self.assertEqual(plan[0].duration_hours, 3.0)

    def test_start_time_begins_at_work_start(self):
        tasks = [_make_task(effort=1.0)]
        plan = generate_daily_plan(tasks, available_hours=6)
        self.assertEqual(plan[0].start_time, _fmt_time(WORK_START_HOUR))

    def test_slot_fields_match_task(self):
        t = _make_task("Essay", "English", effort=2.0)
        plan = generate_daily_plan([t], available_hours=6)
        s = plan[0]
        self.assertEqual(s.task_id, t.id)
        self.assertEqual(s.task_title, t.title)
        self.assertEqual(s.subject, t.subject)

    def test_selected_task_ids_limit_plan(self):
        t1 = _make_task("A", priority=3)
        t2 = _make_task("B", priority=2)
        plan = generate_daily_plan([t1, t2], available_hours=6, task_ids={t2.id})
        self.assertEqual([s.task_title for s in plan], ["B"])


if __name__ == "__main__":
    unittest.main()
