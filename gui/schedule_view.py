# gui/schedule_view.py
from __future__ import annotations
import customtkinter as ctk
from typing import Callable
from scheduler.planner import Slot


# Apple Design Tokens (from SKILL.md)
class AppleTheme:
    """Apple design system color tokens."""
    SURFACE_BASE = "#FFFFFF"       # Page background
    SURFACE_RAISED = "#F5F5F7"     # Cards, elevated surfaces
    ACCENT = "#155BD0"             # Primary actions, focus
    TEXT_PRIMARY = "#1D1D1F"        # Headings, body text
    TEXT_SECONDARY = "#6E6E73"     # Secondary, muted text
    TEXT_TERTIARY = "#86868B"      # Additional text
    BORDER_DEFAULT = "#D2D2D7"      # Subtle borders
    SUCCESS = "#34C759"            # Success states
    DESTRUCTIVE = "#FF3B30"        # Destructive actions


class ScheduleFrame(ctk.CTkFrame):
    """
    Displays the generated daily schedule as time-slot cards.
    Apple-inspired design with clean aesthetics.

    Args:
        parent:        Parent CTk widget.
        slots:         Initial list of Slot objects (can be empty).
        on_generate:   Callback() — called when 'Generate Plan' is clicked.
        on_mark_done:  Callback(task_id: str, done: bool) — called when checkbox toggled.
    """

    def __init__(self, parent, slots: list[Slot],
                 on_generate: Callable,
                 on_mark_done: Callable[[str, bool], None]):
        super().__init__(
            parent,
            fg_color=AppleTheme.SURFACE_BASE,
            corner_radius=21
        )
        self.on_generate  = on_generate
        self.on_mark_done = on_mark_done

        self._build_header()
        self._build_scroll()
        self.refresh(slots)

    # ── Header ────────────────────────────────────────────────────────────

    def _build_header(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.pack(fill="x", padx=13, pady=(13, 4))

        # Apple-style heading: 27px, normal weight
        ctk.CTkLabel(
            bar,
            text="Today's Study Plan",
            font=ctk.CTkFont(size=27, weight="normal"),
            text_color=AppleTheme.TEXT_PRIMARY
        ).pack(side="left")

        # Apple-style ghost button with hover effect
        ctk.CTkButton(
            bar,
            text="Generate Plan",
            fg_color="transparent",
            text_color=AppleTheme.ACCENT,
            border_width=1,
            border_color=AppleTheme.ACCENT,
            corner_radius=21,
            height=34,
            hover_color=AppleTheme.SURFACE_RAISED,
            font=ctk.CTkFont(size=14, weight="normal"),
            command=self.on_generate
        ).pack(side="right")

    # ── Scroll area ───────────────────────────────────────────────────────

    def _build_scroll(self):
        self.scroll = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color=AppleTheme.TEXT_TERTIARY,
            scrollbar_button_hover_color=AppleTheme.TEXT_SECONDARY
        )
        self.scroll.pack(fill="both", expand=True, padx=13, pady=8)

    # ── Public API ───────────────────────────────────────────────────────

    def refresh(self, slots: list[Slot]):
        """Re-render with a new slot list. Called after generate or mark-done."""
        for widget in self.scroll.winfo_children():
            widget.destroy()

        if not slots:
            ctk.CTkLabel(
                self.scroll,
                text="No plan yet. Add tasks and click 'Generate Plan'.",
                font=ctk.CTkFont(size=16, weight="normal"),
                text_color=AppleTheme.TEXT_TERTIARY
            ).pack(pady=40)
            return

        for slot in slots:
            self._add_slot_card(slot)

    # ── Slot card ─────────────────────────────────────────────────────────

    def _add_slot_card(self, slot: Slot):
        # Apple-style card with subtle border
        card = ctk.CTkFrame(
            self.scroll,
            fg_color=AppleTheme.SURFACE_RAISED,
            corner_radius=21,
            border_width=1,
            border_color=AppleTheme.BORDER_DEFAULT
        )
        card.pack(fill="x", pady=4)

        # Time badge - Apple style
        time_lbl = ctk.CTkLabel(
            card,
            text=slot.display_range(),
            width=130,
            anchor="center",
            font=ctk.CTkFont(size=16, weight="normal"),
            text_color=AppleTheme.TEXT_PRIMARY
        )
        time_lbl.pack(side="left", padx=(13, 8), pady=13)

        # Task info section
        info = ctk.CTkFrame(card, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True, pady=8)

        # Task title: 16px , normal weight
        # Note: Apple design often uses a single font weight for body text, relying on size and color for hierarchy.
        ctk.CTkLabel(
            info,
            text=slot.task_title,
            font=ctk.CTkFont(size=16, weight="normal"),
            text_color=AppleTheme.TEXT_PRIMARY,
            anchor="w"
        ).pack(anchor="w", padx=(0, 0))

        # Subject and duration: 14px, secondary color
        ctk.CTkLabel(
            info,
            text=f"{slot.subject}  ·  {slot.duration_hours}h",
            font=ctk.CTkFont(size=14, weight="normal"),
            text_color=AppleTheme.TEXT_SECONDARY,
            anchor="w"
        ).pack(anchor="w", padx=(0, 0))

        # Apple-style checkbox (no text, just indicator)
        done_var = ctk.BooleanVar(value=slot.is_done)
        ctk.CTkCheckBox(
            card,
            text="",
            variable=done_var,
            fg_color=AppleTheme.ACCENT,
            border_color=AppleTheme.BORDER_DEFAULT,
            width=24,
            height=24,
            command=lambda s=slot, v=done_var: self.on_mark_done(s.task_id, v.get())
        ).pack(side="right", padx=13)