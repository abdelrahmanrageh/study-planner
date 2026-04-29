# tests/test_storage.py
"""
Unit tests for storage.json — save_tasks / load_tasks.

Uses a temporary directory so tests never touch real data files.
"""

import json
import os
import unittest
from datetime import date, timedelta
from pathlib import Path
from unittest.mock import patch

from models.task import Task
from storage.json import save_tasks, load_tasks


# ── Helper ────────────────────────────────────────────────────────────────

def _future(days: int = 3) -> date:
    return date.today() + timedelta(days=days)


def _sample_tasks() -> list[Task]:
    return [
        Task("Essay", "English", _future(2), 2.0, 3),
        Task("Calc HW", "Math", _future(5), 1.5, 2),
    ]


class TestStorage(unittest.TestCase):
    """All tests patch DATA_FILE and BACKUP_FILE to use a temp directory."""

    def setUp(self):
        import tempfile
        self._tmpdir = tempfile.mkdtemp()
        self._data_path = os.path.join(self._tmpdir, "data.json")
        self._backup_path = os.path.join(self._tmpdir, "data.bak.json")

        # Patch config constants used inside storage.json
        self._patcher_data = patch("storage.json.DATA_FILE", self._data_path)
        self._patcher_bak  = patch("storage.json.BACKUP_FILE", self._backup_path)
        self._patcher_data.start()
        self._patcher_bak.start()

    def tearDown(self):
        self._patcher_data.stop()
        self._patcher_bak.stop()
        # Clean up temp files
        import shutil
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    # -- save --

    def test_save_creates_file(self):
        save_tasks(_sample_tasks())
        self.assertTrue(Path(self._data_path).exists())

    def test_save_writes_valid_json(self):
        save_tasks(_sample_tasks())
        with open(self._data_path) as f:
            data = json.load(f)
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 2)

    def test_save_creates_backup_on_overwrite(self):
        save_tasks(_sample_tasks())          # first save
        save_tasks(_sample_tasks()[:1])      # second save — should back up
        self.assertTrue(Path(self._backup_path).exists())

    # -- load --

    def test_load_returns_empty_when_no_file(self):
        tasks = load_tasks()
        self.assertEqual(tasks, [])

    def test_load_round_trip(self):
        original = _sample_tasks()
        save_tasks(original)
        loaded = load_tasks()
        self.assertEqual(len(loaded), len(original))
        for orig, ld in zip(original, loaded):
            self.assertEqual(orig.id, ld.id)
            self.assertEqual(orig.title, ld.title)
            self.assertEqual(orig.subject, ld.subject)
            self.assertEqual(orig.deadline, ld.deadline)
            self.assertEqual(orig.effort_hours, ld.effort_hours)
            self.assertEqual(orig.priority, ld.priority)
            self.assertEqual(orig.is_done, ld.is_done)

    def test_load_handles_malformed_json(self):
        with open(self._data_path, "w") as f:
            f.write("NOT VALID JSON{{{")
        tasks = load_tasks()
        self.assertEqual(tasks, [])

    def test_load_handles_missing_key(self):
        # Write valid JSON but missing a required key
        with open(self._data_path, "w") as f:
            json.dump([{"id": "abc", "title": "T"}], f)
        tasks = load_tasks()
        self.assertEqual(tasks, [])

    def test_save_preserves_done_status(self):
        tasks = _sample_tasks()
        tasks[0].is_done = True
        save_tasks(tasks)
        loaded = load_tasks()
        self.assertTrue(loaded[0].is_done)
        self.assertFalse(loaded[1].is_done)


if __name__ == "__main__":
    unittest.main()
