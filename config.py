# config.py
# Shared constants — do not hardcode these values in your own module.
# Import like: from config import WORK_START_HOUR, PRIORITY_LABELS

WORK_START_HOUR = 9        # daily schedule starts at 09:00
WORK_END_HOUR   = 21       # daily schedule ends at 21:00
DAILY_HOURS     = WORK_END_HOUR - WORK_START_HOUR   # = 12

PRIORITY_LABELS = {1: "Low", 2: "Medium", 3: "High"}
PRIORITY_VALUES = {"Low": 1, "Medium": 2, "High": 3}

DATA_FILE       = "data.json"
BACKUP_FILE     = "data.bak.json"

APP_TITLE       = "Smart Study Planner"
APP_GEOMETRY    = "1000x650"