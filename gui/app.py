"""
Main application window — Premium Dark Theme
=============================================

Provides:
- Compact floating-style sidebar with purple active state
- Dark navy background
- Swappable content frames for each page
- Live clock in sidebar footer
- Proper resource cleanup on exit
"""

import customtkinter as ctk
from datetime import datetime

from gui.theme import COLORS, FONT_FAMILY, FONT_SIZES, RADIUS, PAD, SIDEBAR_WIDTH, NAV_ITEMS
from gui.components import font, StatusBadge


class App(ctk.CTk):
    """Root window with premium sidebar navigation."""

    def __init__(self, db, student_mgr, attendance_mgr, face_detector, face_recognizer, settings):
        super().__init__()

        # Shared services
        self.db = db
        self.student_mgr = student_mgr
        self.attendance_mgr = attendance_mgr
        self.face_detector = face_detector
        self.face_recognizer = face_recognizer
        self.settings = settings

        # Window config
        self.title("Face Attendance · AI Attendance System")
        self.geometry("1320x760")
        self.minsize(1080, 640)
        self.configure(fg_color=COLORS["bg"])

        ctk.set_appearance_mode("dark")

        self.current_page = "dashboard"

        # Build
        self._create_layout()
        self._create_sidebar()
        self._create_pages()
        self._show_page("dashboard")

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ================================================================
    # Layout
    # ================================================================

    def _create_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(
            self, width=SIDEBAR_WIDTH, corner_radius=0,
            fg_color=COLORS["sidebar_bg"],
        )
        self.sidebar.grid(row=0, column=0, sticky="nswe")
        self.sidebar.grid_propagate(False)
        self.sidebar.grid_columnconfigure(0, weight=1)

        # Content
        self.content = ctk.CTkFrame(self, corner_radius=0, fg_color=COLORS["bg"])
        self.content.grid(row=0, column=1, sticky="nswe")
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

    # ================================================================
    # Sidebar
    # ================================================================

    def _create_sidebar(self):
        # ---- Logo ----
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        logo_frame.grid(row=0, column=0, padx=16, pady=(22, 4), sticky="ew")

        # Camera/face icon
        ctk.CTkLabel(
            logo_frame, text="\u25C9",  # ◉
            font=font(28, "bold"),
            text_color=COLORS["purple"],
        ).pack(side="left")

        title_frame = ctk.CTkFrame(logo_frame, fg_color="transparent")
        title_frame.pack(side="left", padx=(10, 0))

        ctk.CTkLabel(
            title_frame, text="FACE", font=font(16, "bold"),
            text_color=COLORS["text"],
        ).pack(anchor="w")
        ctk.CTkLabel(
            title_frame, text="ATTENDANCE", font=font(10, "bold"),
            text_color=COLORS["purple"],
        ).pack(anchor="w")

        # Subtitle
        ctk.CTkLabel(
            self.sidebar, text="AI Attendance System",
            font=font("tiny"), text_color=COLORS["muted"],
        ).grid(row=1, column=0, padx=16, pady=(0, 16), sticky="w")

        # ---- Separator ----
        ctk.CTkFrame(
            self.sidebar, height=1, fg_color=COLORS["border"],
        ).grid(row=2, column=0, padx=16, sticky="ew")

        # ---- Navigation ----
        self.nav_buttons = {}
        for i, (icon, label, page_name) in enumerate(NAV_ITEMS):
            btn = ctk.CTkButton(
                self.sidebar,
                text=f"  {icon}   {label}",
                font=font("nav"),
                height=38,
                anchor="w",
                corner_radius=RADIUS["sm"],
                command=lambda p=page_name: self._show_page(p),
                fg_color="transparent",
                text_color=COLORS["muted"],
                hover_color=COLORS["sidebar_hover"],
            )
            btn.grid(row=i + 3, column=0, padx=10, pady=2, sticky="ew")
            self.nav_buttons[page_name] = btn

        # ---- Spacer ----
        self.sidebar.grid_rowconfigure(20, weight=1)

        # ---- Footer: Status ----
        footer = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        footer.grid(row=21, column=0, padx=16, pady=(0, 6), sticky="ew")

        ctk.CTkLabel(footer, text="System Status", font=font("tiny"),
                     text_color=COLORS["muted"]).pack(anchor="w")

        self.status_badge = StatusBadge(footer, "Online", COLORS["success"])
        self.status_badge.pack(anchor="w", pady=(2, 0))

        # ---- Footer: Clock + Version ----
        clock_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        clock_frame.grid(row=22, column=0, padx=16, pady=(4, 14), sticky="ew")

        self.clock_label = ctk.CTkLabel(
            clock_frame, text="", font=font("tiny"),
            text_color=COLORS["muted"],
        )
        self.clock_label.pack(anchor="w")

        ctk.CTkLabel(
            clock_frame, text="Version 1.0.0", font=font(9),
            text_color=COLORS["muted"],
        ).pack(anchor="w")

        self._update_clock()

    def _update_clock(self):
        now = datetime.now()
        self.clock_label.configure(text=now.strftime("%I:%M %p · %b %d, %Y"))
        self.after(1000, self._update_clock)

    # ================================================================
    # Pages
    # ================================================================

    def _create_pages(self):
        from gui.dashboard import DashboardPage
        from gui.registration import RegistrationPage
        from gui.recognition import RecognitionPage
        from gui.attendance_view import AttendanceViewPage
        from gui.statistics import StatisticsPage
        from gui.settings import SettingsPage
        from gui.about import AboutPage

        self.pages = {
            "dashboard":    DashboardPage(self.content, self),
            "registration": RegistrationPage(self.content, self),
            "recognition":  RecognitionPage(self.content, self),
            "attendance":   AttendanceViewPage(self.content, self),
            "statistics":   StatisticsPage(self.content, self),
            "settings":     SettingsPage(self.content, self),
            "about":        AboutPage(self.content, self),
        }

    def _show_page(self, page_name: str):
        # Stop cameras on other pages
        if hasattr(self, "pages"):
            for name, page in self.pages.items():
                if name != page_name and hasattr(page, "stop_camera"):
                    page.stop_camera()

            for page in self.pages.values():
                page.grid_forget()

        # Highlight active nav
        for name, btn in self.nav_buttons.items():
            if name == page_name:
                btn.configure(
                    fg_color=COLORS["sidebar_active"],
                    text_color=COLORS["text"],
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["muted"],
                )

        # Show page
        self.pages[page_name].grid(row=0, column=0, sticky="nswe")
        if hasattr(self.pages[page_name], "refresh"):
            self.pages[page_name].refresh()
        self.current_page = page_name

    # ================================================================
    # Public API
    # ================================================================

    def navigate_to(self, page_name: str):
        self._show_page(page_name)

    # ================================================================
    # Cleanup
    # ================================================================

    def _on_close(self):
        for page in self.pages.values():
            if hasattr(page, "stop_camera"):
                page.stop_camera()
            if hasattr(page, "cleanup"):
                page.cleanup()
        self.destroy()
