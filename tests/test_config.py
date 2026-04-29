# tests/test_config.py
"""
Unit tests for config.py — ensures shared constants are consistent.
"""

import unittest

from config import (
    WORK_START_HOUR,
    WORK_END_HOUR,
    DAILY_HOURS,
    PRIORITY_LABELS,
    PRIORITY_VALUES,
    DATA_FILE,
    BACKUP_FILE,
    APP_TITLE,
    APP_GEOMETRY,
)


class TestConfig(unittest.TestCase):

    def test_daily_hours_consistency(self):
        self.assertEqual(DAILY_HOURS, WORK_END_HOUR - WORK_START_HOUR)

    def test_work_hours_positive(self):
        self.assertGreater(DAILY_HOURS, 0)

    def test_work_start_before_end(self):
        self.assertLess(WORK_START_HOUR, WORK_END_HOUR)

    def test_priority_labels_and_values_are_inverse(self):
        for num, label in PRIORITY_LABELS.items():
            self.assertEqual(PRIORITY_VALUES[label], num)

    def test_priority_has_three_levels(self):
        self.assertEqual(len(PRIORITY_LABELS), 3)
        self.assertEqual(len(PRIORITY_VALUES), 3)

    def test_data_file_is_json(self):
        self.assertTrue(DATA_FILE.endswith(".json"))

    def test_backup_file_is_json(self):
        self.assertTrue(BACKUP_FILE.endswith(".json"))

    def test_app_title_not_empty(self):
        self.assertTrue(len(APP_TITLE) > 0)

    def test_app_geometry_format(self):
        # Should look like "WIDTHxHEIGHT"
        parts = APP_GEOMETRY.split("x")
        self.assertEqual(len(parts), 2)
        self.assertTrue(parts[0].isdigit())
        self.assertTrue(parts[1].isdigit())


if __name__ == "__main__":
    unittest.main()
