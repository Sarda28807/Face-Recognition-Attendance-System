"""
Smart Face Recognition Attendance System
=========================================

Entry point for the application.
Initializes all components and launches the GUI.

Usage:
    python main.py

Author: Portfolio Project
License: MIT
"""

import sys
from pathlib import Path

# Ensure the project root is on the Python path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def check_dependencies() -> bool:
    """Verify that all required packages are installed."""
    missing = []
    packages = {
        "cv2": "opencv-contrib-python",
        "numpy": "numpy",
        "customtkinter": "customtkinter",
        "PIL": "Pillow",
        "matplotlib": "matplotlib",
    }
    for module, pip_name in packages.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(pip_name)

    if missing:
        print("=" * 60)
        print("MISSING DEPENDENCIES")
        print("=" * 60)
        print(f"The following packages are not installed:\n")
        for pkg in missing:
            print(f"  - {pkg}")
        print(f"\nInstall them with:\n")
        print(f"  pip install {' '.join(missing)}")
        print("=" * 60)
        return False
    return True


def main():
    """Initialize all components and launch the application."""
    # 1. Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # 2. Import after dependency check
    from utils.config import (
        DATABASE_PATH, FACES_DIR, EXPORTS_DIR, MODELS_DIR,
        DNN_MODELS_DIR, load_settings, ensure_directories,
    )
    from database.database import DatabaseManager
    from core.face_detector import FaceDetector
    from core.face_recognizer import FaceRecognizer
    from core.student_manager import StudentManager
    from core.attendance_manager import AttendanceManager
    from gui.app import App

    # 3. Create required directories
    print("📁 Ensuring directories exist...")
    ensure_directories()

    # 4. Initialize database
    print("🗃️  Initializing database...")
    try:
        db = DatabaseManager(DATABASE_PATH)
    except Exception as e:
        print(f"❌ Unable to access attendance database: {e}")
        sys.exit(1)

    # 5. Load settings
    settings = load_settings()

    # 6. Initialize face detector
    print("👁️  Initializing face detector...")
    detection_method = settings.get("detection_method", "haar")
    try:
        face_detector = FaceDetector(
            method=detection_method,
            dnn_models_dir=DNN_MODELS_DIR,
        )
        print(f"   Using {face_detector.method.upper()} detection.")
    except RuntimeError as e:
        print(f"⚠️  Face detector warning: {e}")
        print("   Falling back to Haar Cascade...")
        face_detector = FaceDetector(method="haar")

    # 7. Initialize face recognizer
    print("🧠 Initializing face recognizer...")
    threshold = settings.get("recognition_threshold", 85.0)
    face_recognizer = FaceRecognizer(
        model_path=MODELS_DIR,
        threshold=float(threshold),
    )
    if face_recognizer.is_trained:
        print(f"   Loaded trained model ({len(face_recognizer.label_map)} students).")
    else:
        print("   No trained model found. Register students to begin.")

    # 8. Initialize managers
    student_mgr = StudentManager(db, FACES_DIR)
    attendance_mgr = AttendanceManager(db, EXPORTS_DIR)

    # 9. Launch GUI
    print("🚀 Launching application...")
    print("=" * 50)
    app = App(
        db=db,
        student_mgr=student_mgr,
        attendance_mgr=attendance_mgr,
        face_detector=face_detector,
        face_recognizer=face_recognizer,
        settings=settings,
    )
    app.mainloop()
    print("👋 Application closed.")


if __name__ == "__main__":
    main()
