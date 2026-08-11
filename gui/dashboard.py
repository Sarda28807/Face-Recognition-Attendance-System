"""
Dashboard page — Premium Dark Theme
====================================

Layout (inspired by SaaS analytics dashboards):
  Row 1 — Compact header  (title + date + status)
  Row 2 — Three stat cards (Total · Present · Rate)
  Row 3 — Attendance Analytics chart (left) + Today donut (right)
  Row 4 — Recent Attendance list (left) + Quick Actions (mid) + System Status (right)
"""

import os
import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from gui.theme import COLORS, RADIUS, PAD, CHART, FONT_FAMILY
from gui.components import (
    font, ModernCard, StatCard, ActionCard, SectionHeader, StatusBadge, Toast,
)
from utils.helpers import get_display_date, get_date_string, format_confidence
from utils.config import PRIVACY_NOTICE, FACES_DIR


class DashboardPage(ctk.CTkFrame):
    """Premium analytics-style dashboard."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg"])
        self.app = app
        self._chart_canvases = []
        self._build_ui()

    # ================================================================
    # UI
    # ================================================================

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)

        # Row 0 — Header
        header = SectionHeader(
            self, "Dashboard", "Attendance overview",
            right_text=f"{get_display_date()}   ● System Online",
        )
        header.grid(row=0, column=0, columnspan=2,
                    padx=PAD["page"], pady=(PAD["page"], PAD["md"]), sticky="ew")

        # Row 1 — Stat cards
        self._build_stat_cards()

        # Row 2 — Charts row
        self._build_charts_row()

        # Row 3 — Bottom row
        self._build_bottom_row()

    # ---- stat cards ----

    def _build_stat_cards(self):
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=1, column=0, columnspan=2,
                         padx=PAD["page"], pady=(0, PAD["sm"]), sticky="ew")
        for i in range(3):
            cards_frame.grid_columnconfigure(i, weight=1)

        self.stat_cards = {}

        defs = [
            ("total",   "◆", "TOTAL STUDENTS", "0", "Registered",  COLORS["purple"]),
            ("present", "▲", "PRESENT TODAY",   "0", "Checked in",  COLORS["success"]),
            ("rate",    "●", "ATTENDANCE RATE",  "0%", "Today",      COLORS["cyan"]),
        ]
        for i, (key, icon, label, val, sub, accent) in enumerate(defs):
            card = StatCard(cards_frame, icon=icon, label=label,
                            value=val, subtitle=sub, accent=accent)
            card.grid(row=0, column=i, padx=PAD["xs"], pady=PAD["xs"], sticky="nsew")
            self.stat_cards[key] = card

    # ---- charts ----

    def _build_charts_row(self):
        # Left: 7-day trend
        self.trend_card = ModernCard(self)
        self.trend_card.grid(row=2, column=0, padx=(PAD["page"], PAD["xs"]),
                             pady=PAD["xs"], sticky="nsew")
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self.trend_card, text="ATTENDANCE ANALYTICS",
                     font=font("small", "bold"),
                     text_color=COLORS["text_secondary"]).pack(
            padx=16, pady=(14, 0), anchor="w")
        ctk.CTkLabel(self.trend_card, text="7-day attendance trend",
                     font=font("tiny"),
                     text_color=COLORS["muted"]).pack(padx=16, anchor="w")

        self.trend_chart_frame = ctk.CTkFrame(self.trend_card, fg_color="transparent")
        self.trend_chart_frame.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        # Right: Today donut
        self.donut_card = ModernCard(self)
        self.donut_card.grid(row=2, column=1, padx=(PAD["xs"], PAD["page"]),
                             pady=PAD["xs"], sticky="nsew")

        ctk.CTkLabel(self.donut_card, text="TODAY'S ATTENDANCE",
                     font=font("small", "bold"),
                     text_color=COLORS["text_secondary"]).pack(
            padx=16, pady=(14, 0), anchor="w")

        self.donut_chart_frame = ctk.CTkFrame(self.donut_card, fg_color="transparent")
        self.donut_chart_frame.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        # Donut details
        self.donut_pct_label = ctk.CTkLabel(
            self.donut_card, text="0%",
            font=font("card_number_lg", "bold"),
            text_color=COLORS["purple"],
        )
        # will be positioned by chart drawing

    # ---- bottom row ----

    def _build_bottom_row(self):
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=3, column=0, columnspan=2,
                    padx=PAD["page"], pady=(PAD["xs"], PAD["page"]), sticky="ew")
        bottom.grid_columnconfigure(0, weight=2)
        bottom.grid_columnconfigure(1, weight=2)
        bottom.grid_columnconfigure(2, weight=1)

        # Left — Recent Attendance
        self._build_recent_attendance(bottom)

        # Middle — Quick Actions
        self._build_quick_actions(bottom)

        # Right — System Status
        self._build_system_status(bottom)

    def _build_recent_attendance(self, parent):
        card = ModernCard(parent)
        card.grid(row=0, column=0, padx=(0, PAD["xs"]), sticky="nsew")

        ctk.CTkLabel(card, text="RECENT ATTENDANCE", font=font("small", "bold"),
                     text_color=COLORS["text_secondary"]).pack(
            padx=14, pady=(12, 6), anchor="w")

        self.recent_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.recent_frame.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def _build_quick_actions(self, parent):
        card = ModernCard(parent)
        card.grid(row=0, column=1, padx=PAD["xs"], sticky="nsew")

        ctk.CTkLabel(card, text="QUICK ACTIONS", font=font("small", "bold"),
                     text_color=COLORS["text_secondary"]).pack(
            padx=14, pady=(12, 6), anchor="w")

        actions_inner = ctk.CTkFrame(card, fg_color="transparent")
        actions_inner.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        actions_inner.grid_columnconfigure(0, weight=1)
        actions_inner.grid_columnconfigure(1, weight=1)

        action_defs = [
            ("\u25C9", "Recognition", "Mark attendance",
             lambda: self.app.navigate_to("recognition"), COLORS["purple"]),
            ("\u25CE", "Register", "Add student",
             lambda: self.app.navigate_to("registration"), COLORS["blue"]),
            ("\u2630", "Attendance", "View records",
             lambda: self.app.navigate_to("attendance"), COLORS["cyan"]),
            ("\u25BC", "Export CSV", "Download data",
             self._export_csv, COLORS["success"]),
        ]

        for i, (icon, title, sub, cmd, accent) in enumerate(action_defs):
            ac = ActionCard(actions_inner, icon=icon, title=title,
                            subtitle=sub, command=cmd, accent=accent)
            ac.grid(row=i // 2, column=i % 2, padx=3, pady=3, sticky="nsew")
            actions_inner.grid_rowconfigure(i // 2, weight=1)

    def _build_system_status(self, parent):
        card = ModernCard(parent)
        card.grid(row=0, column=2, padx=(PAD["xs"], 0), sticky="nsew")

        ctk.CTkLabel(card, text="SYSTEM STATUS", font=font("small", "bold"),
                     text_color=COLORS["text_secondary"]).pack(
            padx=14, pady=(12, 8), anchor="w")

        self.status_items = {}
        items = [
            ("camera",    "Camera",      "Ready",     COLORS["success"]),
            ("database",  "Database",    "Connected", COLORS["success"]),
            ("engine",    "Face Engine", "Ready",     COLORS["success"]),
            ("storage",   "Storage",     "—",         COLORS["muted"]),
        ]
        for key, label, status, color in items:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=2)
            ctk.CTkLabel(row, text=label, font=font("tiny"),
                         text_color=COLORS["muted"]).pack(side="left")
            badge = StatusBadge(row, status, color)
            badge.pack(side="right")
            self.status_items[key] = badge

    # ================================================================
    # Data Refresh
    # ================================================================

    def refresh(self):
        try:
            stats = self.app.attendance_mgr.get_today_stats()
            self.stat_cards["total"].set_value(stats["total"])
            self.stat_cards["present"].set_value(stats["present"])
            self.stat_cards["rate"].set_value(f"{stats['percentage']}%")
        except Exception:
            pass

        self._draw_trend_chart()
        self._draw_donut_chart()
        self._refresh_recent()
        self._refresh_status()

    # ---- trend chart ----

    def _draw_trend_chart(self):
        for c in self._chart_canvases:
            try:
                c.get_tk_widget().destroy()
            except Exception:
                pass
        self._chart_canvases.clear()

        fig = Figure(figsize=(5, 2.2), dpi=CHART["dpi"])
        fig.patch.set_facecolor(CHART["bg"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(CHART["axes_bg"])

        try:
            summary = self.app.attendance_mgr.get_daily_summary(days=7)
            if summary:
                dates = [s["date"][-5:] for s in reversed(summary)]
                counts = [s["present_count"] for s in reversed(summary)]
                ax.plot(dates, counts, color=CHART["line_color"],
                        linewidth=2.5, marker="o", markersize=5,
                        markerfacecolor=COLORS["purple"],
                        markeredgecolor=COLORS["text"], markeredgewidth=1)
                ax.fill_between(dates, counts, alpha=CHART["fill_alpha"],
                                color=CHART["fill_color"])
            else:
                ax.text(0.5, 0.5, "No data yet", ha="center", va="center",
                        color=COLORS["muted"], fontsize=11,
                        transform=ax.transAxes, fontfamily=FONT_FAMILY)
        except Exception:
            pass

        for spine in ax.spines.values():
            spine.set_color(CHART["spine_color"])
        ax.tick_params(colors=CHART["tick_color"], labelsize=8)
        ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        ax.grid(axis="y", alpha=CHART["grid_alpha"], color=CHART["grid_color"])
        fig.tight_layout(pad=1.0)

        canvas = FigureCanvasTkAgg(fig, master=self.trend_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self._chart_canvases.append(canvas)

    # ---- donut chart ----

    def _draw_donut_chart(self):
        fig = Figure(figsize=(2.5, 2.5), dpi=CHART["dpi"])
        fig.patch.set_facecolor(CHART["bg"])
        ax = fig.add_subplot(111)

        try:
            stats = self.app.attendance_mgr.get_today_stats()
            present = stats["present"]
            absent = stats["absent"]
            pct = stats["percentage"]

            if present + absent > 0:
                sizes = [present, absent]
                colors_list = [COLORS["purple"], COLORS["border"]]
                ax.pie(sizes, colors=colors_list, startangle=90,
                       wedgeprops=dict(width=0.35, edgecolor=CHART["bg"]))
                ax.text(0, 0, f"{pct}%", ha="center", va="center",
                        fontsize=20, color=COLORS["text"],
                        fontweight="bold", fontfamily=FONT_FAMILY)
            else:
                ax.pie([1], colors=[COLORS["border"]], startangle=90,
                       wedgeprops=dict(width=0.35, edgecolor=CHART["bg"]))
                ax.text(0, 0, "0%", ha="center", va="center",
                        fontsize=20, color=COLORS["muted"],
                        fontweight="bold", fontfamily=FONT_FAMILY)
        except Exception:
            pass

        fig.tight_layout(pad=0.5)
        canvas = FigureCanvasTkAgg(fig, master=self.donut_chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self._chart_canvases.append(canvas)

    # ---- recent attendance ----

    def _refresh_recent(self):
        for w in self.recent_frame.winfo_children():
            w.destroy()

        try:
            records = self.app.attendance_mgr.get_attendance_records(
                date_filter=get_date_string()
            )[:6]

            if not records:
                ctk.CTkLabel(
                    self.recent_frame,
                    text="No attendance recorded today.\nStart recognition to begin.",
                    font=font("small"), text_color=COLORS["muted"],
                    justify="center",
                ).pack(expand=True)
                return

            for rec in records:
                row = ctk.CTkFrame(self.recent_frame, fg_color=COLORS["elevated"],
                                   corner_radius=RADIUS["sm"], height=36)
                row.pack(fill="x", pady=2, padx=2)
                row.pack_propagate(False)

                ctk.CTkLabel(row, text="●", font=font(8),
                             text_color=COLORS["success"]).pack(
                    side="left", padx=(10, 4))
                ctk.CTkLabel(row, text=rec.get("name", ""),
                             font=font("small", "bold"),
                             text_color=COLORS["text"]).pack(side="left")
                ctk.CTkLabel(row, text=rec.get("student_id", ""),
                             font=font("tiny"),
                             text_color=COLORS["muted"]).pack(side="left", padx=(8, 0))
                ctk.CTkLabel(row, text=rec.get("time", ""),
                             font=font("tiny"),
                             text_color=COLORS["text_secondary"]).pack(
                    side="right", padx=10)
        except Exception:
            pass

    # ---- system status ----

    def _refresh_status(self):
        # Face engine
        if self.app.face_recognizer.is_trained:
            n = len(self.app.face_recognizer.label_map)
            self.status_items["engine"].set(f"{n} students", COLORS["success"])
        else:
            self.status_items["engine"].set("Not trained", COLORS["warning"])

        # Storage
        try:
            total = sum(
                f.stat().st_size for f in FACES_DIR.rglob("*") if f.is_file()
            )
            mb = total / (1024 * 1024)
            self.status_items["storage"].set(f"{mb:.1f} MB", COLORS["cyan"])
        except Exception:
            self.status_items["storage"].set("—", COLORS["muted"])

    # ---- export ----

    def _export_csv(self):
        success, msg = self.app.attendance_mgr.export_csv()
        kind = "success" if success else "danger"
        Toast.show(self.app, msg, kind)
