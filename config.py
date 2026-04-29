# config.py
# Shared constants — do not hardcode these values in your own module.
# Import like: from config import WORK_START_HOUR, PRIORITY_LABELS

WORK_START_HOUR = 9        # daily schedule starts at 09:00
WORK_END_HOUR   = 21       # daily schedule ends at 21:00
DAILY_HOURS     = WORK_END_HOUR - WORK_START_HOUR   # = 12

PRIORITY_LABELS = {1: "Low", 2: "Medium", 3: "High"}
PRIORITY_VALUES = {"Low": 1, "Medium": 2, "High": 3}


class AppleTheme:
	"""Adaptive Apple-inspired tokens for customtkinter widgets."""

	BG_BASE = ("#F2F2F7", "#000000")
	SURFACE_BASE = ("#FFFFFF", "#1C1C1E")
	SURFACE_RAISED = ("#F5F5F7", "#2C2C2E")
	SURFACE_TERTIARY = ("#E5E5EA", "#3A3A3C")

	TEXT_PRIMARY = ("#1D1D1F", "#F5F5F7")
	TEXT_SECONDARY = ("#6E6E73", "#A1A1A6")
	TEXT_TERTIARY = ("#86868B", "#6E6E73")

	BORDER_DEFAULT = ("#D2D2D7", "#38383A")
	ACCENT = ("#155BD0", "#0A84FF")
	ACCENT_HOVER = ("#1149AB", "#409CFF")
	DESTRUCTIVE = ("#C0392B", "#FF453A")
	DESTRUCTIVE_HOVER = ("#A93226", "#D93E36")
	FILL_PRIMARY = ("#D1D1D6", "#48484A")
	FILL_SECONDARY = ("#E5E5EA", "#3A3A3C")

DATA_FILE       = "data.json"
BACKUP_FILE     = "data.bak.json"

APP_TITLE       = "Smart Study Planner"
APP_GEOMETRY    = "1000x650"

# Centralized typography tokens. Try to use CTkFont when CustomTkinter
# is available (normal app run). Fall back to simple tuples so modules
# that import config in non-GUI contexts (tests, CLI) still work.
try:
	import customtkinter as ctk  # type: ignore

	FONT_HEADING = ctk.CTkFont(size=22, weight="bold")
	FONT_SUBHEAD = ctk.CTkFont(size=16, weight="normal")
	FONT_BODY = ctk.CTkFont(size=13, weight="normal")
except Exception:
	FONT_HEADING = ("", 22, "bold")
	FONT_SUBHEAD = ("", 16, "normal")
	FONT_BODY = ("", 13, "normal")