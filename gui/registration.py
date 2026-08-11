"""
Student Registration page — Premium Dark Theme
================================================

Two-column floating-panel layout:
  LEFT  — Student information form (dark card)
  RIGHT — Face registration camera preview (dark card)
  BOTTOM — Action buttons + status
"""

import cv2
import tkinter as tk
import customtkinter as ctk
from PIL import Image, ImageTk
from typing import List

from gui.theme import COLORS, RADIUS, PAD, FONT_FAMILY
from gui.components import (
    font, ModernCard, ModernButton, ModernEntry, SectionHeader, Toast,
)
from utils.config import NUM_FACE_SAMPLES, FACE_IMAGE_SIZE, CAMERA_WIDTH, CAMERA_HEIGHT


class RegistrationPage(ctk.CTkFrame):
    """Student registration with live camera face capture."""

    def __init__(self, parent, app):
        super().__init__(parent, fg_color=COLORS["bg"])
        self.app = app

        self._camera = None
        self._camera_running = False
        self._after_id = None
        self._captured_faces: List = []
        self._latest_frame = None
        self._latest_faces = []

        self._build_ui()

    # ================================================================
    # UI
    # ================================================================

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        SectionHeader(self, "Register Student", "Add a new student to the system"
                      ).grid(row=0, column=0, columnspan=2,
                             padx=PAD["page"], pady=(PAD["page"], PAD["md"]), sticky="ew")

        # Left — Form
        self._build_form()

        # Right — Camera
        self._build_camera()

        # Bottom — Buttons
        self._build_buttons()

    def _build_form(self):
        card = ModernCard(self)
        card.grid(row=1, column=0, padx=(PAD["page"], PAD["xs"]),
                  pady=(0, PAD["xs"]), sticky="nsew")

        ctk.CTkLabel(card, text="STUDENT INFORMATION",
                     font=font("small", "bold"),
                     text_color=COLORS["text_secondary"]).pack(
            padx=18, pady=(16, 12), anchor="w")

        self.entries = {}
        fields = [
            ("student_id",  "Student ID",   "e.g. CSE-2024-001"),
            ("name",        "Full Name",    "e.g. Rahul Sharma"),
            ("department",  "Department",   "e.g. Computer Science"),
            ("year",        "Year",         "e.g. 3"),
            ("email",       "Email",        "e.g. rahul@example.com"),
            ("phone",       "Phone",        "Optional"),
        ]

        for key, label, placeholder in fields:
            ctk.CTkLabel(card, text=label, font=font("tiny"),
                         text_color=COLORS["muted"]).pack(
                padx=18, pady=(6, 0), anchor="w")
            entry = ModernEntry(card, placeholder_text=placeholder)
            entry.pack(padx=18, pady=(2, 0), fill="x")
            self.entries[key] = entry

    def _build_camera(self):
        card = ModernCard(self)
        card.grid(row=1, column=1, padx=(PAD["xs"], PAD["page"]),
                  pady=(0, PAD["xs"]), sticky="nsew")

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(16, 6))

        ctk.CTkLabel(top, text="FACE REGISTRATION",
                     font=font("small", "bold"),
                     text_color=COLORS["text_secondary"]).pack(side="left")

        self.cam_status = ctk.CTkLabel(top, text="● Ready",
                                       font=font("tiny"),
                                       text_color=COLORS["muted"])
        self.cam_status.pack(side="right")

        # Camera display
        self.camera_label = tk.Label(card, bg=COLORS["surface"],
                                     highlightthickness=0)
        self.camera_label.pack(padx=12, pady=4, fill="both", expand=True)
        self.camera_label.configure(
            text="Camera Off\n\nClick Start Camera to begin",
            fg=COLORS["muted"], font=(FONT_FAMILY, 11),
        )

        # Capture counter
        self.capture_label = ctk.CTkLabel(
            card, text=f"Captured: 0 / {NUM_FACE_SAMPLES}",
            font=font("tiny"), text_color=COLORS["muted"],
        )
        self.capture_label.pack(padx=18, pady=(4, 12))

    def _build_buttons(self):
        bar = ctk.CTkFrame(self, fg_color="transparent")
        bar.grid(row=2, column=0, columnspan=2,
                 padx=PAD["page"], pady=(0, PAD["sm"]), sticky="ew")

        btns = [
            ("Start Camera",   self._start_camera,  COLORS["blue"]),
            ("Stop Camera",    self._stop_camera_ui, COLORS["border"]),
            ("Capture Face",   self._capture_face,  COLORS["purple"]),
            ("Register Student", self._save_student, COLORS["success"]),
            ("Clear",          self._clear_form,    COLORS["danger"]),
        ]
        for text, cmd, accent in btns:
            ModernButton(bar, text=text, accent=accent, command=cmd,
                         width=140).pack(side="left", padx=3)

        self.status_label = ctk.CTkLabel(
            bar, text="", font=font("small"),
            text_color=COLORS["text_secondary"],
        )
        self.status_label.pack(side="right", padx=8)

    # ================================================================
    # Camera
    # ================================================================

    def _start_camera(self):
        if self._camera_running:
            return
        idx = self.app.settings.get("camera_index", 0)
        try:
            idx = int(idx)
        except (ValueError, TypeError):
            idx = 0

        self._camera = cv2.VideoCapture(idx)
        if not self._camera.isOpened():
            Toast.show(self.app, "Unable to access camera. Check camera index.", "danger")
            return

        self._camera.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
        self._camera.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
        self._camera_running = True
        self.cam_status.configure(text="● Active", text_color=COLORS["success"])
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

        # Draw purple corner indicators
        for (x, y, w, h, conf) in faces:
            self._draw_corners(frame, x, y, w, h)

        self._latest_frame = frame
        self._latest_faces = faces

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

    def _draw_corners(self, frame, x, y, w, h, length=22, thickness=2):
        """Draw stylish corner indicators instead of full rectangle."""
        color = (246, 92, 139)  # Purple #8B5CF6 in BGR
        # Top-left
        cv2.line(frame, (x, y), (x + length, y), color, thickness)
        cv2.line(frame, (x, y), (x, y + length), color, thickness)
        # Top-right
        cv2.line(frame, (x + w, y), (x + w - length, y), color, thickness)
        cv2.line(frame, (x + w, y), (x + w, y + length), color, thickness)
        # Bottom-left
        cv2.line(frame, (x, y + h), (x + length, y + h), color, thickness)
        cv2.line(frame, (x, y + h), (x, y + h - length), color, thickness)
        # Bottom-right
        cv2.line(frame, (x + w, y + h), (x + w - length, y + h), color, thickness)
        cv2.line(frame, (x + w, y + h), (x + w, y + h - length), color, thickness)

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
        self.cam_status.configure(text="● Ready", text_color=COLORS["muted"])

    # ================================================================
    # Capture
    # ================================================================

    def _capture_face(self):
        if not self._camera_running:
            Toast.show(self.app, "Start the camera first.", "warning")
            return
        if not self._latest_faces:
            Toast.show(self.app, "No face detected. Position face clearly.", "warning")
            return
        if len(self._latest_faces) > 1:
            Toast.show(self.app, "Multiple faces detected. Ensure only one person.", "warning")
            return
        if len(self._captured_faces) >= NUM_FACE_SAMPLES:
            Toast.show(self.app, f"Already captured {NUM_FACE_SAMPLES} samples.", "info")
            return

        face_img = self.app.face_detector.extract_face(
            self._latest_frame, self._latest_faces[0], FACE_IMAGE_SIZE)
        if face_img is None:
            Toast.show(self.app, "Could not extract face. Try again.", "warning")
            return

        self._captured_faces.append(face_img)
        count = len(self._captured_faces)
        self.capture_label.configure(text=f"Captured: {count} / {NUM_FACE_SAMPLES}")

        if count >= NUM_FACE_SAMPLES:
            Toast.show(self.app, "All samples captured! Click Register Student.", "success")
        else:
            Toast.show(self.app, f"Sample {count}/{NUM_FACE_SAMPLES} captured.", "info")

    # ================================================================
    # Save
    # ================================================================

    def _save_student(self):
        data = {key: entry.get() for key, entry in self.entries.items()}
        if not self._captured_faces:
            Toast.show(self.app, "Capture face images first.", "warning")
            return

        success, message = self.app.student_mgr.register_student(data, self._captured_faces)
        if success:
            Toast.show(self.app, message, "success")
            from utils.config import FACES_DIR
            self.app.face_recognizer.train(FACES_DIR, self.app.db)
            self._clear_form()
        else:
            Toast.show(self.app, message, "danger")

    def _clear_form(self):
        for entry in self.entries.values():
            entry.delete(0, "end")
        self._captured_faces.clear()
        self.capture_label.configure(text=f"Captured: 0 / {NUM_FACE_SAMPLES}")

    def refresh(self):
        pass
