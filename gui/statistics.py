"""
Analytics / Statistics page — Premium Dark Theme
==================================================

Professional analytics dashboard with purple-gradient charts.

Layout:
  Row 1 — Four compact stat cards
  Row 2 — 14-day attendance trend (left) + donut present/absent (right)
  Row 3 — Per-student bar chart (full width)
"""

import customtkinter as ctk
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.ticker
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from gui.theme import COLORS, RADIUS, PAD, CHART, FONT_FAMILY
from gui.components import font, ModernCard, StatCard, SectionHeader


class StatisticsPage(ctk.CTkFrame):
    """Analytics dashboard with dark-themed Matplotlib charts."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg"])
        self.app = app
        self._canvases = []
        self._build_ui()

    # ================================================================
    # UI
    # ================================================================

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Header
        SectionHeader(self, "Analytics", "Attendance insights & trends"
                      ).grid(row=0, column=0, columnspan=2,
                             padx=PAD["page"], pady=(PAD["page"], PAD["md"]), sticky="ew")

        # Stat cards
        cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        cards_frame.grid(row=1, column=0, columnspan=2,
                         padx=PAD["page"], pady=(0, PAD["sm"]), sticky="ew")
        for i in range(4):
            cards_frame.grid_columnconfigure(i, weight=1)

        self.cards = {}
        defs = [
            ("total",   "◆", "TOTAL STUDENTS",     "0", COLORS["purple"]),
            ("present", "▲", "PRESENT TODAY",       "0", COLORS["success"]),
            ("absent",  "▼", "ABSENT TODAY",        "0", COLORS["danger"]),
            ("rate",    "●", "ATTENDANCE RATE",     "0%", COLORS["cyan"]),
        ]
        for i, (key, icon, label, val, accent) in enumerate(defs):
            card = StatCard(cards_frame, icon=icon, label=label,
                            value=val, accent=accent)
            card.grid(row=0, column=i, padx=PAD["xs"], pady=PAD["xs"], sticky="nsew")
            self.cards[key] = card

        # Row 2 — Charts
        self.trend_card = ModernCard(self)
        self.trend_card.grid(row=2, column=0, padx=(PAD["page"], PAD["xs"]),
                             pady=PAD["xs"], sticky="nsew")
        self.grid_rowconfigure(2, weight=1)

        ctk.CTkLabel(self.trend_card, text="ATTENDANCE TREND",
                     font=font("small", "bold"),
                     text_color=COLORS["text_secondary"]).pack(
            padx=16, pady=(14, 0), anchor="w")
        ctk.CTkLabel(self.trend_card, text="Last 14 days",
                     font=font("tiny"), text_color=COLORS["muted"]).pack(
            padx=16, anchor="w")
        self.trend_frame = ctk.CTkFrame(self.trend_card, fg_color="transparent")
        self.trend_frame.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        self.pie_card = ModernCard(self)
        self.pie_card.grid(row=2, column=1, padx=(PAD["xs"], PAD["page"]),
                           pady=PAD["xs"], sticky="nsew")
        ctk.CTkLabel(self.pie_card, text="TODAY'S BREAKDOWN",
                     font=font("small", "bold"),
                     text_color=COLORS["text_secondary"]).pack(
            padx=16, pady=(14, 0), anchor="w")
        self.pie_frame = ctk.CTkFrame(self.pie_card, fg_color="transparent")
        self.pie_frame.pack(fill="both", expand=True, padx=8, pady=(4, 8))

        # Row 3 — Bar chart
        self.bar_card = ModernCard(self)
        self.bar_card.grid(row=3, column=0, columnspan=2,
                           padx=PAD["page"], pady=(PAD["xs"], PAD["page"]),
                           sticky="nsew")
        self.grid_rowconfigure(3, weight=1)

        ctk.CTkLabel(self.bar_card, text="STUDENT ATTENDANCE",
                     font=font("small", "bold"),
                     text_color=COLORS["text_secondary"]).pack(
            padx=16, pady=(14, 0), anchor="w")
        ctk.CTkLabel(self.bar_card, text="Days present per student",
                     font=font("tiny"), text_color=COLORS["muted"]).pack(
            padx=16, anchor="w")
        self.bar_frame = ctk.CTkFrame(self.bar_card, fg_color="transparent")
        self.bar_frame.pack(fill="both", expand=True, padx=8, pady=(4, 8))

    # ================================================================
    # Refresh
    # ================================================================

    def refresh(self):
        self._update_cards()
        self._clear_charts()
        self._draw_trend()
        self._draw_pie()
        self._draw_bar()

    def _update_cards(self):
        try:
            stats = self.app.attendance_mgr.get_today_stats()
            self.cards["total"].set_value(stats["total"])
            self.cards["present"].set_value(stats["present"])
            self.cards["absent"].set_value(stats["absent"])
            self.cards["rate"].set_value(f"{stats['percentage']}%")
        except Exception:
            pass

    def _clear_charts(self):
        for c in self._canvases:
            try:
                c.get_tk_widget().destroy()
            except Exception:
                pass
        self._canvases.clear()

    # ---- Trend ----

    def _draw_trend(self):
        fig = Figure(figsize=(5, 2.4), dpi=CHART["dpi"])
        fig.patch.set_facecolor(CHART["bg"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(CHART["axes_bg"])

        try:
            summary = self.app.attendance_mgr.get_daily_summary(days=14)
            if summary:
                dates = [s["date"][-5:] for s in reversed(summary)]
                counts = [s["present_count"] for s in reversed(summary)]
                ax.plot(dates, counts, color=CHART["line_color"],
                        linewidth=2.5, marker="o", markersize=4,
                        markerfacecolor=COLORS["purple"],
                        markeredgecolor="white", markeredgewidth=0.8)
                ax.fill_between(dates, counts, alpha=CHART["fill_alpha"],
                                color=CHART["fill_color"])
                ax.set_xticks(range(len(dates)))
                ax.set_xticklabels(dates, rotation=45, ha="right", fontsize=7)
            else:
                ax.text(0.5, 0.5, "No data yet", ha="center", va="center",
                        color=COLORS["muted"], fontsize=11,
                        transform=ax.transAxes, fontfamily=FONT_FAMILY)
        except Exception:
            pass

        self._style_axes(ax)
        ax.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
        fig.tight_layout(pad=1.0)
        self._embed(fig, self.trend_frame)

    # ---- Pie / Donut ----

    def _draw_pie(self):
        fig = Figure(figsize=(3, 2.4), dpi=CHART["dpi"])
        fig.patch.set_facecolor(CHART["bg"])
        ax = fig.add_subplot(111)

        try:
            stats = self.app.attendance_mgr.get_today_stats()
            p, a = stats["present"], stats["absent"]
            if p + a > 0:
                ax.pie([p, a],
                       colors=[COLORS["purple"], COLORS["border"]],
                       startangle=90,
                       wedgeprops=dict(width=0.35, edgecolor=CHART["bg"]))
                ax.text(0, 0, f"{stats['percentage']}%",
                        ha="center", va="center", fontsize=22,
                        color=COLORS["text"], fontweight="bold",
                        fontfamily=FONT_FAMILY)

                # Legend
                ax.text(0, -1.3, f"Present {p}    Absent {a}",
                        ha="center", fontsize=8, color=COLORS["muted"],
                        fontfamily=FONT_FAMILY)
            else:
                ax.pie([1], colors=[COLORS["border"]], startangle=90,
                       wedgeprops=dict(width=0.35, edgecolor=CHART["bg"]))
                ax.text(0, 0, "0%", ha="center", va="center",
                        fontsize=22, color=COLORS["muted"],
                        fontweight="bold", fontfamily=FONT_FAMILY)
        except Exception:
            pass

        fig.tight_layout(pad=0.5)
        self._embed(fig, self.pie_frame)

    # ---- Bar ----

    def _draw_bar(self):
        fig = Figure(figsize=(9, 2.2), dpi=CHART["dpi"])
        fig.patch.set_facecolor(CHART["bg"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(CHART["axes_bg"])

        try:
            student_stats = self.app.attendance_mgr.get_student_stats()
            if student_stats:
                data = student_stats[:15]
                names = [s["name"][:14] for s in data]
                days = [s["days_present"] for s in data]
                bars = ax.barh(names, days, color=COLORS["purple"],
                               edgecolor=COLORS["purple_dark"], height=0.55)
                for bar, val in zip(bars, days):
                    ax.text(bar.get_width() + 0.15,
                            bar.get_y() + bar.get_height() / 2,
                            str(val), va="center",
                            color=COLORS["text"], fontsize=8,
                            fontfamily=FONT_FAMILY)
                ax.invert_yaxis()
            else:
                ax.text(0.5, 0.5, "No data yet", ha="center", va="center",
                        color=COLORS["muted"], fontsize=11,
                        transform=ax.transAxes, fontfamily=FONT_FAMILY)
        except Exception:
            pass

        self._style_axes(ax)
        ax.grid(axis="x", alpha=CHART["grid_alpha"], color=CHART["grid_color"])
        fig.tight_layout(pad=1.0)
        self._embed(fig, self.bar_frame)

    # ================================================================
    # Helpers
    # ================================================================

    def _style_axes(self, ax):
        for spine in ax.spines.values():
            spine.set_color(CHART["spine_color"])
        ax.tick_params(colors=CHART["tick_color"], labelsize=8)
        ax.grid(axis="y", alpha=CHART["grid_alpha"], color=CHART["grid_color"])

    def _embed(self, fig, parent):
        canvas = FigureCanvasTkAgg(fig, master=parent)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)
        self._canvases.append(canvas)
