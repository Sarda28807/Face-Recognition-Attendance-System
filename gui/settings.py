"""
Settings page — Premium Dark Theme
====================================

Clean settings dashboard with compact rounded panels for each section.
Settings persist to JSON via utils/config.
"""

import customtkinter as ctk
from gui.theme import COLORS, RADIUS, PAD
from gui.components import (
    font, ModernCard, ModernButton, ModernEntry, SectionHeader, StatusBadge, Toast,
)
from utils.config import (
    DEFAULT_SETTINGS, load_settings, save_settings, FACE_MATCH_THRESHOLD,
)


class SettingsPage(ctk.CTkFrame):
    """Application settings with grouped panels."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg"])
        self.app = app
        self._build_ui()

    # ================================================================
    # UI
    # ================================================================

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Header
        SectionHeader(self, "Settings", "Configure system preferences"
                      ).grid(row=0, column=0, columnspan=2,
                             padx=PAD["page"], pady=(PAD["page"], PAD["md"]), sticky="ew")

        # Left column
        left = ctk.CTkFrame(self, fg_color="transparent")
        left.grid(row=1, column=0, padx=(PAD["page"], PAD["xs"]),
                  pady=(0, PAD["xs"]), sticky="nsew")
        left.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Right column
        right = ctk.CTkFrame(self, fg_color="transparent")
        right.grid(row=1, column=1, padx=(PAD["xs"], PAD["page"]),
                   pady=(0, PAD["xs"]), sticky="nsew")
        right.grid_columnconfigure(0, weight=1)

        # ---- Camera ----
        self._build_camera_section(left)

        # ---- Recognition ----
        self._build_recognition_section(left)

        # ---- Database ----
        self._build_database_section(right)

        # ---- Export ----
        self._build_export_section(right)

        # ---- Buttons ----
        self._build_buttons()

    def _build_camera_section(self, parent):
        card = ModernCard(parent)
        card.pack(fill="x", pady=(0, PAD["sm"]))

        ctk.CTkLabel(card, text="CAMERA", font=font("small", "bold"),
                     text_color=COLORS["text_secondary"]).pack(
            padx=16, pady=(14, 8), anchor="w")

        # Camera index
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(row, text="Camera Index", font=font("body"),
                     text_color=COLORS["text"]).pack(side="left")
        self.camera_index_var = ctk.StringVar(
            value=str(self.app.settings.get("camera_index", 0)))
        ModernEntry(row, textvariable=self.camera_index_var,
                    width=60).pack(side="right")

        # Camera status
        row2 = ctk.CTkFrame(card, fg_color="transparent")
        row2.pack(fill="x", padx=16, pady=(4, 14))
        ctk.CTkLabel(row2, text="Camera Status", font=font("body"),
                     text_color=COLORS["text"]).pack(side="left")
        StatusBadge(row2, "Ready", COLORS["success"]).pack(side="right")

    def _build_recognition_section(self, parent):
        card = ModernCard(parent)
        card.pack(fill="x", pady=(0, PAD["sm"]))

        ctk.CTkLabel(card, text="RECOGNITION", font=font("small", "bold"),
                     text_color=COLORS["text_secondary"]).pack(
            padx=16, pady=(14, 8), anchor="w")

        # Threshold slider
        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(row, text="Recognition Threshold", font=font("body"),
                     text_color=COLORS["text"]).pack(side="left")
        self.threshold_label = ctk.CTkLabel(row, text="",
                                            font=font("body", "bold"),
                                            text_color=COLORS["purple"])
        self.threshold_label.pack(side="right")

        self.threshold_var = ctk.DoubleVar(
            value=self.app.settings.get("recognition_threshold", FACE_MATCH_THRESHOLD))
        self.threshold_slider = ctk.CTkSlider(
            card, from_=30, to=150, variable=self.threshold_var,
            width=280, button_color=COLORS["purple"],
            button_hover_color=COLORS["purple_dark"],
            progress_color=COLORS["purple"],
            fg_color=COLORS["surface"],
            command=self._on_threshold_change,
        )
        self.threshold_slider.pack(padx=16, pady=(0, 4))
        self._on_threshold_change(self.threshold_var.get())

        # Auto attendance toggle
        row2 = ctk.CTkFrame(card, fg_color="transparent")
        row2.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(row2, text="Auto-Mark Attendance", font=font("body"),
                     text_color=COLORS["text"]).pack(side="left")
        self.auto_attendance_var = ctk.BooleanVar(
            value=self.app.settings.get("auto_attendance", True))
        ctk.CTkSwitch(row2, text="", variable=self.auto_attendance_var,
                      onvalue=True, offvalue=False,
                      button_color=COLORS["purple"],
                      progress_color=COLORS["purple"],
                      fg_color=COLORS["surface"]).pack(side="right")

        # Detection method
        row3 = ctk.CTkFrame(card, fg_color="transparent")
        row3.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(row3, text="Detection Method", font=font("body"),
                     text_color=COLORS["text"]).pack(side="left")
        self.detection_var = ctk.StringVar(
            value=self.app.settings.get("detection_method", "haar"))
        ctk.CTkSegmentedButton(
            row3, values=["haar", "dnn"], variable=self.detection_var,
            font=font("tiny"),
            selected_color=COLORS["purple"],
            unselected_color=COLORS["surface"],
            fg_color=COLORS["surface"],
        ).pack(side="right")

        # Face samples
        row4 = ctk.CTkFrame(card, fg_color="transparent")
        row4.pack(fill="x", padx=16, pady=(4, 14))
        ctk.CTkLabel(row4, text="Face Samples per Registration",
                     font=font("body"),
                     text_color=COLORS["text"]).pack(side="left")
        self.samples_var = ctk.StringVar(
            value=str(self.app.settings.get("num_face_samples", 10)))
        ModernEntry(row4, textvariable=self.samples_var,
                    width=60).pack(side="right")

    def _build_database_section(self, parent):
        card = ModernCard(parent)
        card.pack(fill="x", pady=(0, PAD["sm"]))

        ctk.CTkLabel(card, text="DATABASE", font=font("small", "bold"),
                     text_color=COLORS["text_secondary"]).pack(
            padx=16, pady=(14, 8), anchor="w")

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=4)
        ctk.CTkLabel(row, text="Database Status", font=font("body"),
                     text_color=COLORS["text"]).pack(side="left")
        StatusBadge(row, "Connected", COLORS["success"]).pack(side="right")

        row2 = ctk.CTkFrame(card, fg_color="transparent")
        row2.pack(fill="x", padx=16, pady=(4, 14))
        ctk.CTkLabel(row2, text="Students Registered", font=font("body"),
                     text_color=COLORS["text"]).pack(side="left")
        self.student_count_label = ctk.CTkLabel(
            row2, text="0", font=font("body", "bold"),
            text_color=COLORS["purple"])
        self.student_count_label.pack(side="right")

    def _build_export_section(self, parent):
        card = ModernCard(parent)
        card.pack(fill="x", pady=(0, PAD["sm"]))

        ctk.CTkLabel(card, text="EXPORT", font=font("small", "bold"),
                     text_color=COLORS["text_secondary"]).pack(
            padx=16, pady=(14, 8), anchor="w")

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(4, 14))
        ctk.CTkLabel(row, text="Export Directory", font=font("body"),
                     text_color=COLORS["text"]).pack(anchor="w")
        self.export_dir_var = ctk.StringVar(
            value=str(self.app.settings.get("export_directory", "")))
        ModernEntry(row, textvariable=self.export_dir_var).pack(
            fill="x", pady=(4, 0))

    def _build_buttons(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=2, column=0, columnspan=2,
                 padx=PAD["page"], pady=(0, PAD["page"]), sticky="ew")

        ModernButton(bar, text="Save Settings", accent=COLORS["success"],
                     command=self._save, width=160).pack(side="left", padx=3)
        ModernButton(bar, text="Reset to Defaults", accent=COLORS["warning"],
                     command=self._reset, width=160).pack(side="left", padx=3)

    # ================================================================
    # Actions
    # ================================================================

    def _on_threshold_change(self, value):
        self.threshold_label.configure(text=f"{value:.0f}")

    def _save(self):
        try:
            camera_index = int(self.camera_index_var.get())
        except ValueError:
            Toast.show(self.app, "Camera index must be a number.", "danger")
            return
        try:
            num_samples = int(self.samples_var.get())
            if not 1 <= num_samples <= 50:
                raise ValueError
        except ValueError:
            Toast.show(self.app, "Samples must be between 1 and 50.", "danger")
            return

        settings = {
            "camera_index": camera_index,
            "recognition_threshold": self.threshold_var.get(),
            "auto_attendance": self.auto_attendance_var.get(),
            "detection_method": self.detection_var.get(),
            "num_face_samples": num_samples,
            "export_directory": self.export_dir_var.get(),
        }
        if save_settings(settings):
            self.app.settings.update(settings)
            self.app.face_recognizer.update_threshold(settings["recognition_threshold"])
            Toast.show(self.app, "Settings saved successfully!", "success")
        else:
            Toast.show(self.app, "Failed to save settings.", "danger")

    def _reset(self):
        d = DEFAULT_SETTINGS.copy()
        self.camera_index_var.set(str(d["camera_index"]))
        self.threshold_var.set(d["recognition_threshold"])
        self.auto_attendance_var.set(d["auto_attendance"])
        self.detection_var.set(d["detection_method"])
        self.samples_var.set(str(d["num_face_samples"]))
        self.export_dir_var.set(d["export_directory"])
        self._on_threshold_change(d["recognition_threshold"])
        Toast.show(self.app, "Reset to defaults (not saved yet).", "info")

    def refresh(self):
        try:
            count = self.app.db.get_student_count()
            self.student_count_label.configure(text=str(count))
        except Exception:
            pass
