"""
Face Recognition page — Premium Dark Theme
============================================

The most visually impressive page of the application.

Layout:
  LEFT  65 % — Large rounded webcam panel with purple/cyan bounding box
  RIGHT 35 % — AI analysis panel (name, ID, confidence bar, status)
"""

import cv2
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk

from gui.theme import COLORS, RADIUS, PAD, FONT_FAMILY
from gui.components import (
    font, ModernCard, ModernButton, StatusBadge, SectionHeader, Toast, darken,
)
from utils.config import CAMERA_WIDTH, CAMERA_HEIGHT
from utils.helpers import format_confidence, confidence_to_percentage, get_display_time


class RecognitionPage(ctk.CTkFrame):
    """Live face recognition with futuristic AI analysis panel."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg"])
        self.app = app

        self._camera = None
        self._camera_running = False
        self._after_id = None
        self._last_recognized_id = None
        self._cooldown_counter = 0

        self._build_ui()

    # ================================================================
    # UI
    # ================================================================

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        SectionHeader(self, "Live Recognition", "AI-powered face attendance"
                      ).grid(row=0, column=0, columnspan=2,
                             padx=PAD["page"], pady=(PAD["page"], PAD["md"]), sticky="ew")

        # Left — Camera
        self._build_camera_panel()

        # Right — Analysis
        self._build_analysis_panel()

        # Bottom — Controls
        self._build_controls()

    def _build_camera_panel(self):
        card = ModernCard(self)
        card.grid(row=1, column=0, padx=(PAD["page"], PAD["xs"]),
                  pady=(0, PAD["xs"]), sticky="nsew")

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(14, 4))

        ctk.CTkLabel(top, text="LIVE FACE RECOGNITION",
                     font=font("small", "bold"),
                     text_color=COLORS["text_secondary"]).pack(side="left")

        self.cam_indicator = StatusBadge(top, "Camera Off", COLORS["muted"])
        self.cam_indicator.pack(side="right")

        # Camera display
        self.camera_label = tk.Label(card, bg=COLORS["surface"],
                                     highlightthickness=0)
        self.camera_label.pack(padx=10, pady=(0, 10), fill="both", expand=True)
        self.camera_label.configure(
            text="Camera Off\n\nClick Start Camera to begin recognition",
            fg=COLORS["muted"], font=(FONT_FAMILY, 12),
        )

    def _build_analysis_panel(self):
        card = ModernCard(self)
        card.grid(row=1, column=1, padx=(PAD["xs"], PAD["page"]),
                  pady=(0, PAD["xs"]), sticky="nsew")

        ctk.CTkLabel(card, text="RECOGNITION",
                     font=font("small", "bold"),
                     text_color=COLORS["text_secondary"]).pack(
            padx=16, pady=(16, 8), anchor="w")

        # Status indicator
        self.status_dot = ctk.CTkLabel(card, text="●", font=font(36),
                                       text_color=COLORS["border"])
        self.status_dot.pack(pady=(4, 0))

        self.status_text = ctk.CTkLabel(card, text="Waiting...",
                                        font=font("heading", "bold"),
                                        text_color=COLORS["muted"])
        self.status_text.pack(pady=(0, 12))

        # Separator
        ctk.CTkFrame(card, height=1, fg_color=COLORS["border"]).pack(
            fill="x", padx=16, pady=4)

        # Result fields
        self.result_labels = {}
        fields = [
            ("name",       "Name"),
            ("student_id", "Student ID"),
            ("confidence", "Confidence"),
            ("attendance", "Attendance"),
            ("time",       "Time"),
        ]
        for key, label in fields:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=16, pady=4)
            ctk.CTkLabel(row, text=label, font=font("tiny"),
                         text_color=COLORS["muted"], width=80,
                         anchor="w").pack(side="left")
            val = ctk.CTkLabel(row, text="—", font=font("body", "bold"),
                               text_color=COLORS["text"], anchor="w")
            val.pack(side="left", fill="x", expand=True)
            self.result_labels[key] = val

        # Confidence bar
        self.conf_bar_frame = ctk.CTkFrame(card, fg_color="transparent")
        self.conf_bar_frame.pack(fill="x", padx=16, pady=(8, 0))
        ctk.CTkLabel(self.conf_bar_frame, text="CONFIDENCE",
                     font=font(9), text_color=COLORS["muted"]).pack(anchor="w")

        bar_bg = ctk.CTkFrame(self.conf_bar_frame, fg_color=COLORS["surface"],
                               corner_radius=4, height=10)
        bar_bg.pack(fill="x", pady=(2, 0))
        bar_bg.pack_propagate(False)
        self.conf_bar = ctk.CTkFrame(bar_bg, fg_color=COLORS["purple"],
                                      corner_radius=4, width=0)
        self.conf_bar.pack(side="left", fill="y")

        # Spacer
        ctk.CTkLabel(card, text="").pack(fill="both", expand=True)

        # Activity log
        ctk.CTkLabel(card, text="ACTIVITY LOG",
                     font=font("tiny", "bold"),
                     text_color=COLORS["muted"]).pack(padx=16, anchor="w")

        self.log_textbox = ctk.CTkTextbox(
            card, height=100, font=font("tiny"),
            fg_color=COLORS["surface"],
            text_color=COLORS["text_secondary"],
            border_width=0, corner_radius=RADIUS["sm"],
            state="disabled",
        )
        self.log_textbox.pack(padx=12, pady=(4, 12), fill="x")

    def _build_controls(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=2, column=0, columnspan=2,
                 padx=PAD["page"], pady=(0, PAD["page"]), sticky="ew")

        ModernButton(bar, text="▶  Start Camera", accent=COLORS["success"],
                     command=self._start_camera, width=180).pack(side="left", padx=3)
        ModernButton(bar, text="■  Stop Camera", accent=COLORS["danger"],
                     command=self._stop_camera_ui, width=180).pack(side="left", padx=3)

        self.fps_label = ctk.CTkLabel(bar, text="", font=font("tiny"),
                                      text_color=COLORS["muted"])
        self.fps_label.pack(side="right", padx=8)

    # ================================================================
    # Camera
    # ================================================================

    def _start_camera(self):
        if self._camera_running:
            return
        if not self.app.face_recognizer.is_trained:
            Toast.show(self.app, "No trained model. Register students first.", "warning")
            return

        idx = self.app.settings.get("camera_index", 0)
        try:
            idx = int(idx)
        except (ValueError, TypeError):
            idx = 0

        self._camera = cv2.VideoCapture(idx)
        if not self._camera.isOpened():
            Toast.show(self.app, "Unable to access camera.", "danger")
            return

        self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self._camera_running = True
        self.cam_indicator.set("Camera Active", COLORS["success"])
        self._update_frame()

    def _update_frame(self):
        if not self._camera_running or self._camera is None:
            return

        ret, frame = self._camera.read()
        if not ret:
            self._after_id = self.after(100, self._update_frame)
            return

        frame = cv2.flip(frame, 1)
        faces = self.app.face_detector.detect_faces(frame)

        if faces:
            for face_rect in faces:
                self._process_face(frame, face_rect)
        else:
            self._update_status("detecting")
            self.status_text.configure(text="Scanning...")

        # Display
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        lw = self.camera_label.winfo_width()
        lh = self.camera_label.winfo_height()
        if lw > 10 and lh > 10:
            img = img.resize((lw, lh), Image.LANCZOS)
        photo = ImageTk.PhotoImage(img)
        self.camera_label.configure(image=photo, text="")
        self.camera_label.image = photo

        self._after_id = self.after(33, self._update_frame)

    def _process_face(self, frame, face_rect):
        face_img = self.app.face_detector.extract_face(frame, face_rect)
        if face_img is None:
            return

        student_id, distance = self.app.face_recognizer.recognize(face_img)
        x, y, w, h = face_rect[:4]

        if student_id:
            student = self.app.db.get_student(student_id)
            name = student["name"] if student else student_id
            conf_pct = confidence_to_percentage(distance)

            # Purple corners + name label
            self._draw_corners(frame, x, y, w, h, (246, 92, 139))
            label = f"{name} ({conf_pct:.0f}%)"
            cv2.putText(frame, label, (x, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                        (246, 92, 139), 1, cv2.LINE_AA)

            self.result_labels["name"].configure(text=name)
            self.result_labels["student_id"].configure(text=student_id)
            self.result_labels["confidence"].configure(text=format_confidence(distance))
            self.result_labels["time"].configure(text=get_display_time())
            self._update_status("recognized")
            self.status_text.configure(text="RECOGNIZED")
            self._set_conf_bar(conf_pct)

            auto = self.app.settings.get("auto_attendance", True)
            if auto and self._should_process(student_id):
                success, msg = self.app.attendance_mgr.mark_attendance(student_id, distance)
                if success:
                    self.result_labels["attendance"].configure(
                        text="✓ MARKED PRESENT", text_color=COLORS["success"])
                    self._add_log(f"✓ {name} ({student_id}) — Marked Present")
                    Toast.show(self.app, f"Attendance marked: {name}", "success")
                else:
                    self.result_labels["attendance"].configure(
                        text="Already Marked", text_color=COLORS["cyan"])
        else:
            # Red corners for unknown
            self._draw_corners(frame, x, y, w, h, (68, 68, 239))
            cv2.putText(frame, "Unknown", (x, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                        (68, 68, 239), 1, cv2.LINE_AA)

            self._update_status("unknown")
            self.status_text.configure(text="UNKNOWN")
            self.result_labels["name"].configure(text="Unknown")
            self.result_labels["student_id"].configure(text="—")
            self.result_labels["confidence"].configure(text=format_confidence(distance))
            self.result_labels["attendance"].configure(
                text="Not recognized", text_color=COLORS["danger"])
            self._set_conf_bar(0)

    def _draw_corners(self, frame, x, y, w, h, color, length=22, thickness=2):
        cv2.line(frame, (x, y), (x + length, y), color, thickness)
        cv2.line(frame, (x, y), (x, y + length), color, thickness)
        cv2.line(frame, (x + w, y), (x + w - length, y), color, thickness)
        cv2.line(frame, (x + w, y), (x + w, y + length), color, thickness)
        cv2.line(frame, (x, y + h), (x + length, y + h), color, thickness)
        cv2.line(frame, (x, y + h), (x, y + h - length), color, thickness)
        cv2.line(frame, (x + w, y + h), (x + w - length, y + h), color, thickness)
        cv2.line(frame, (x + w, y + h), (x + w, y + h - length), color, thickness)

    def _should_process(self, student_id: str) -> bool:
        if student_id == self._last_recognized_id:
            self._cooldown_counter += 1
            if self._cooldown_counter < 30:
                return False
        self._last_recognized_id = student_id
        self._cooldown_counter = 0
        return True

    # ================================================================
    # UI Helpers
    # ================================================================

    def _update_status(self, state):
        colors = {
            "recognized": COLORS["success"],
            "unknown":    COLORS["danger"],
            "detecting":  COLORS["warning"],
        }
        self.status_dot.configure(text_color=colors.get(state, COLORS["muted"]))

    def _set_conf_bar(self, pct):
        try:
            parent_w = self.conf_bar.master.winfo_width()
            bar_w = max(0, int(parent_w * pct / 100))
            self.conf_bar.configure(width=bar_w)
            color = COLORS["success"] if pct > 50 else COLORS["warning"] if pct > 25 else COLORS["danger"]
            self.conf_bar.configure(fg_color=color)
        except Exception:
            pass

    def _add_log(self, message: str):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", f"{get_display_time()} — {message}\n")
        self.log_textbox.see("end")
        self.log_textbox.configure(state="disabled")

    def stop_camera(self):
        self._camera_running = False
        if self._after_id:
            self.after_cancel(self._after_id)
            self._after_id = None
        if self._camera and self._camera.isOpened():
            self._camera.release()
            self._camera = None

    def _stop_camera_ui(self):
        self.stop_camera()
        self.camera_label.configure(image="", text="Camera Off",
                                    fg=COLORS["muted"])
        self.camera_label.image = None
        self.cam_indicator.set("Camera Off", COLORS["muted"])
        self.status_dot.configure(text_color=COLORS["border"])
        self.status_text.configure(text="Waiting...")

    def refresh(self):
        pass
