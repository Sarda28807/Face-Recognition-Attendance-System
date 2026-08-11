"""
Attendance Records page — Premium Dark Theme
==============================================

Premium compact table using ttk.Treeview styled to match the navy theme.
Search, date filter, status filter, and CSV export.
"""

import tkinter as tk
from tkinter import ttk
import customtkinter as ctk

from gui.theme import COLORS, RADIUS, PAD, FONT_FAMILY
from gui.components import font, ModernCard, ModernButton, ModernEntry, SectionHeader, Toast
from utils.helpers import get_date_string, format_confidence


class AttendanceViewPage(ctk.CTkFrame):
    """Attendance records with premium dark table."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg"])
        self.app = app
        self._build_ui()

    # ================================================================
    # UI
    # ================================================================

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        SectionHeader(self, "Attendance Records", "Search and manage records"
                      ).grid(row=0, column=0,
                             padx=PAD["page"], pady=(PAD["page"], PAD["md"]), sticky="ew")

        # Filter bar
        self._build_filters()

        # Table
        self._build_table()

        # Footer
        self._build_footer()

    def _build_filters(self):
        bar = ModernCard(self, corner_radius=RADIUS["md"])
        bar.grid(row=1, column=0, padx=PAD["page"], pady=(0, PAD["sm"]), sticky="ew")

        inner = ctk.CTkFrame(bar, fg_color="transparent")
        inner.pack(fill="x", padx=14, pady=10)

        # Search
        self.search_var = ctk.StringVar()
        ModernEntry(inner, textvariable=self.search_var,
                    placeholder_text="Search by name or ID...",
                    width=200).pack(side="left", padx=(0, 8))

        # Date
        self.date_var = ctk.StringVar()
        ModernEntry(inner, textvariable=self.date_var,
                    placeholder_text="YYYY-MM-DD",
                    width=130).pack(side="left", padx=(0, 6))

        ModernButton(inner, text="Today", accent=COLORS["purple"],
                     command=self._set_today, width=70).pack(side="left", padx=3)
        ModernButton(inner, text="All", accent=COLORS["border"],
                     command=self._clear_filters, width=50).pack(side="left", padx=3)
        ModernButton(inner, text="Search", accent=COLORS["blue"],
                     command=self._load_records, width=80).pack(side="left", padx=3)

        # Right side
        ModernButton(inner, text="Export CSV", accent=COLORS["success"],
                     command=self._export_csv, width=110).pack(side="right", padx=3)

    def _build_table(self):
        card = ModernCard(self)
        card.grid(row=2, column=0, padx=PAD["page"], pady=(0, PAD["xs"]), sticky="nsew")
        card.grid_columnconfigure(0, weight=1)
        card.grid_rowconfigure(0, weight=1)

        # Style Treeview to match dark navy theme
        style = ttk.Style()
        style.theme_use("default")

        style.configure("Navy.Treeview",
                        background=COLORS["surface"],
                        foreground=COLORS["text"],
                        fieldbackground=COLORS["surface"],
                        rowheight=34,
                        font=(FONT_FAMILY, 11),
                        borderwidth=0)

        style.configure("Navy.Treeview.Heading",
                        background=COLORS["table_header"],
                        foreground=COLORS["text_secondary"],
                        font=(FONT_FAMILY, 11, "bold"),
                        relief="flat",
                        borderwidth=0)

        style.map("Navy.Treeview",
                  background=[("selected", COLORS["purple_dark"])],
                  foreground=[("selected", COLORS["text"])])

        style.map("Navy.Treeview.Heading",
                  background=[("active", COLORS["card_hover"])])

        # Remove borders from scrollbar
        style.configure("Navy.Vertical.TScrollbar",
                        background=COLORS["surface"],
                        troughcolor=COLORS["surface"],
                        borderwidth=0)

        columns = ("student_id", "name", "date", "time", "confidence", "status")
        self.tree = ttk.Treeview(card, columns=columns, show="headings",
                                 style="Navy.Treeview", selectmode="browse")

        headings = {
            "student_id":  ("Student ID", 110),
            "name":        ("Name",       180),
            "date":        ("Date",       100),
            "time":        ("Time",        90),
            "confidence":  ("Confidence",  90),
            "status":      ("Status",      90),
        }
        for col, (heading, width) in headings.items():
            self.tree.heading(col, text=heading, anchor="w")
            self.tree.column(col, width=width, anchor="w", minwidth=60)

        scrollbar = ttk.Scrollbar(card, orient="vertical",
                                  command=self.tree.yview,
                                  style="Navy.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew", padx=(8, 0), pady=8)
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(0, 4), pady=8)

        self.tree.tag_configure("even", background=COLORS["table_row_even"])
        self.tree.tag_configure("odd",  background=COLORS["table_row_odd"])

    def _build_footer(self):
        footer = ctk.CTkFrame(self, fg_color="transparent")
        footer.grid(row=3, column=0, padx=PAD["page"],
                    pady=(0, PAD["page"]), sticky="ew")

        self.row_count_label = ctk.CTkLabel(
            footer, text="0 records", font=font("tiny"),
            text_color=COLORS["muted"])
        self.row_count_label.pack(side="left")

    # ================================================================
    # Data
    # ================================================================

    def _load_records(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        date_f = self.date_var.get().strip() or None
        search_q = self.search_var.get().strip() or None

        try:
            records = self.app.attendance_mgr.get_attendance_records(
                date_filter=date_f, search_query=search_q)
        except Exception as e:
            Toast.show(self.app, f"Database error: {e}", "danger")
            return

        for i, rec in enumerate(records):
            tag = "even" if i % 2 == 0 else "odd"
            self.tree.insert("", "end", values=(
                rec.get("student_id", ""),
                rec.get("name", ""),
                rec.get("date", ""),
                rec.get("time", ""),
                format_confidence(rec.get("confidence", 0)),
                rec.get("status", ""),
            ), tags=(tag,))

        count = len(records)
        self.row_count_label.configure(
            text=f"{count} record{'s' if count != 1 else ''}")

    def _set_today(self):
        self.date_var.set(get_date_string())
        self._load_records()

    def _clear_filters(self):
        self.date_var.set("")
        self.search_var.set("")
        self._load_records()

    def _export_csv(self):
        date_f = self.date_var.get().strip() or None
        success, msg = self.app.attendance_mgr.export_csv(date_filter=date_f)
        Toast.show(self.app, msg, "success" if success else "danger")

    def refresh(self):
        self._load_records()
