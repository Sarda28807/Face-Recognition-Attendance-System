"""
About page — Premium Dark Theme
=================================

Compact info cards: app branding, technology stack,
privacy notice, and developer section.
"""

import customtkinter as ctk
from gui.theme import COLORS, RADIUS, PAD
from gui.components import font, ModernCard, SectionHeader
from utils.config import APP_NAME, APP_VERSION, PRIVACY_NOTICE


class AboutPage(ctk.CTkFrame):
    """About, tech stack, and privacy information."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg"])
        self.app = app
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Header
        SectionHeader(self, "About", "System information"
                      ).grid(row=0, column=0, columnspan=2,
                             padx=PAD["page"], pady=(PAD["page"], PAD["md"]), sticky="ew")

        # ---- App Info (left) ----
        info_card = ModernCard(self, border_color=COLORS["purple"])
        info_card.grid(row=1, column=0, padx=(PAD["page"], PAD["xs"]),
                       pady=PAD["xs"], sticky="nsew")

        ctk.CTkLabel(info_card, text="\u25C9", font=font(42),
                     text_color=COLORS["purple"]).pack(pady=(20, 4))
        ctk.CTkLabel(info_card, text="FACE ATTENDANCE",
                     font=font(18, "bold"),
                     text_color=COLORS["text"]).pack()
        ctk.CTkLabel(info_card, text=f"Version {APP_VERSION}",
                     font=font("small"),
                     text_color=COLORS["muted"]).pack(pady=(2, 4))
        ctk.CTkLabel(info_card, text="AI Attendance System",
                     font=font("tiny"),
                     text_color=COLORS["text_secondary"]).pack(pady=(0, 16))

        # ---- Tech Stack (right) ----
        tech_card = ModernCard(self)
        tech_card.grid(row=1, column=1, padx=(PAD["xs"], PAD["page"]),
                       pady=PAD["xs"], sticky="nsew")

        ctk.CTkLabel(tech_card, text="TECHNOLOGY STACK",
                     font=font("small", "bold"),
                     text_color=COLORS["text_secondary"]).pack(
            padx=16, pady=(14, 8), anchor="w")

        techs = [
            ("Python 3.11+",             "Core language",             COLORS["purple"]),
            ("CustomTkinter",            "GUI framework",             COLORS["blue"]),
            ("OpenCV",                   "Computer vision",           COLORS["cyan"]),
            ("LBPH Algorithm",           "Face recognition",          COLORS["success"]),
            ("SQLite3",                  "Database",                  COLORS["warning"]),
            ("Matplotlib",               "Charts",                   COLORS["purple"]),
            ("NumPy",                    "Numerical processing",      COLORS["blue"]),
            ("Pillow",                   "Image processing",          COLORS["cyan"]),
        ]

        for name, desc, accent in techs:
            row = ctk.CTkFrame(tech_card, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=2)
            ctk.CTkLabel(row, text="●", font=font(7),
                         text_color=accent).pack(side="left", padx=(0, 6))
            ctk.CTkLabel(row, text=name, font=font("small", "bold"),
                         text_color=COLORS["text"]).pack(side="left")
            ctk.CTkLabel(row, text=desc, font=font("tiny"),
                         text_color=COLORS["muted"]).pack(side="left", padx=(8, 0))

        ctk.CTkLabel(tech_card, text="").pack(pady=4)

        # ---- Privacy (full width) ----
        privacy_card = ModernCard(self, border_color=COLORS["warning"])
        privacy_card.grid(row=2, column=0, columnspan=2,
                          padx=PAD["page"], pady=PAD["xs"], sticky="ew")

        ctk.CTkLabel(privacy_card, text="PRIVACY & DATA NOTICE",
                     font=font("small", "bold"),
                     text_color=COLORS["warning"]).pack(
            padx=16, pady=(14, 4), anchor="w")
        ctk.CTkLabel(privacy_card, text=PRIVACY_NOTICE,
                     font=font("small"),
                     text_color=COLORS["text_secondary"],
                     wraplength=800, justify="left").pack(
            padx=16, pady=(0, 14), anchor="w")

        # ---- Developer (full width) ----
        dev_card = ModernCard(self)
        dev_card.grid(row=3, column=0, columnspan=2,
                      padx=PAD["page"], pady=(PAD["xs"], PAD["page"]), sticky="ew")

        ctk.CTkLabel(dev_card, text="DEVELOPER",
                     font=font("small", "bold"),
                     text_color=COLORS["text_secondary"]).pack(
            padx=16, pady=(14, 4), anchor="w")
        ctk.CTkLabel(
            dev_card,
            text=(
                "This project demonstrates Python, OpenCV, face recognition,\n"
                "and desktop GUI development. Built as a portfolio project\n"
                "using open-source technologies."
            ),
            font=font("small"),
            text_color=COLORS["muted"],
            justify="left",
        ).pack(padx=16, pady=(0, 14), anchor="w")

    def refresh(self):
        pass
