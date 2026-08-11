"""
Configuration constants for the Face Attendance System.
All configurable values are centralized here to avoid hard-coded values
scattered throughout the codebase.
"""

from pathlib import Path
import json

# ============================================================
# Directory Paths
# ============================================================

# Base directory of the project (parent of utils/)
BASE_DIR = Path(__file__).resolve().parent.parent

# Database
DATABASE_DIR = BASE_DIR / "database"
DATABASE_PATH = DATABASE_DIR / "attendance.db"

# Data directories
DATA_DIR = BASE_DIR / "data"
FACES_DIR = DATA_DIR / "faces"
EXPORTS_DIR = DATA_DIR / "exports"

# Trained model storage
MODELS_DIR = BASE_DIR / "models"

# Assets (DNN model files, icons, etc.)
ASSETS_DIR = BASE_DIR / "assets"
DNN_MODELS_DIR = ASSETS_DIR / "models"

# Settings persistence file
SETTINGS_FILE = BASE_DIR / "settings.json"

# ============================================================
# Face Detection Configuration
# ============================================================

# Minimum detection confidence for the DNN face detector (0.0 - 1.0)
FACE_DETECTION_CONFIDENCE = 0.5

# DNN model download URLs (official OpenCV repository)
DNN_PROTOTXT_URL = (
    "https://raw.githubusercontent.com/opencv/opencv/master/"
    "samples/dnn/face_detector/deploy.prototxt"
)
DNN_MODEL_URL = (
    "https://raw.githubusercontent.com/opencv/opencv_3rdparty/"
    "dnn_samples_face_detector_20170830/"
    "res10_300x300_ssd_iter_140000.caffemodel"
)

# ============================================================
# Face Recognition Configuration
# ============================================================

# LBPH distance threshold — lower = stricter matching.
# A detected face is considered a match only if the LBPH distance
# is below this value. Typical range: 50 (strict) to 120 (lenient).
FACE_MATCH_THRESHOLD = 85.0

# All face images are resized to this size before training/prediction.
FACE_IMAGE_SIZE = (200, 200)

# Number of face samples to capture during registration.
# More samples improve recognition accuracy.
NUM_FACE_SAMPLES = 10

# ============================================================
# Camera Configuration
# ============================================================

CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480
CAMERA_FPS = 30

# ============================================================
# Application Window
# ============================================================

APP_NAME = "Smart Face Recognition Attendance System"
APP_VERSION = "1.0.0"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
MIN_WINDOW_WIDTH = 1050
MIN_WINDOW_HEIGHT = 620

# ============================================================
# Theme & Colors
# ============================================================

THEME_MODE = "dark"  # "dark" or "light"
COLOR_THEME = "blue"  # CustomTkinter color theme

# Custom accent colors used across the GUI
COLORS = {
    "success": "#00b894",
    "warning": "#fdcb6e",
    "error": "#e74c3c",
    "info": "#74b9ff",
    "card_bg_dark": "#2b2b2b",
    "card_bg_light": "#f0f0f0",
    "accent": "#1f6aa5",
    "sidebar_bg": "#1a1a2e",
    "sidebar_hover": "#16213e",
    "text_primary": "#ffffff",
    "text_secondary": "#a0a0a0",
}

# ============================================================
# Default Settings (saved/loaded from settings.json)
# ============================================================

DEFAULT_SETTINGS = {
    "camera_index": CAMERA_INDEX,
    "recognition_threshold": FACE_MATCH_THRESHOLD,
    "auto_attendance": True,
    "export_directory": str(EXPORTS_DIR),
    "theme_mode": THEME_MODE,
    "detection_method": "haar",  # "haar" or "dnn"
    "num_face_samples": NUM_FACE_SAMPLES,
}

# ============================================================
# Privacy Notice
# ============================================================

PRIVACY_NOTICE = (
    "This application is designed for authorized attendance use only.\n\n"
    "• Face data is processed and stored locally on this device.\n"
    "• No images or biometric data are uploaded to external servers.\n"
    "• Camera activates only when you explicitly start it.\n"
    "• Obtain appropriate consent before registering or recognizing individuals.\n\n"
    "This is an educational/portfolio project demonstrating face recognition "
    "technology. It is not intended for covert surveillance or unauthorized monitoring."
)


# ============================================================
# Helper Functions
# ============================================================

def ensure_directories() -> None:
    """Create all required project directories if they do not exist."""
    directories = [
        DATABASE_DIR, FACES_DIR, EXPORTS_DIR,
        MODELS_DIR, DNN_MODELS_DIR,
        ASSETS_DIR / "icons",
    ]
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


def load_settings() -> dict:
    """
    Load user settings from the JSON file.
    Falls back to DEFAULT_SETTINGS for missing keys.
    """
    settings = DEFAULT_SETTINGS.copy()
    if SETTINGS_FILE.exists():
        try:
            with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            settings.update(saved)
        except (json.JSONDecodeError, IOError):
            pass  # Use defaults if file is corrupted
    return settings


def save_settings(settings: dict) -> bool:
    """Save user settings to the JSON file. Returns True on success."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
        return True
    except IOError:
        return False
