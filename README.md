# 📸 Smart Face Recognition Attendance System

A professional desktop application built with Python that uses **face recognition** to automatically mark attendance. Designed as a portfolio project demonstrating practical skills in computer vision, database management, GUI development, and software architecture.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8+-green?logo=opencv)
![SQLite](https://img.shields.io/badge/Database-SQLite3-lightgrey?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📋 Overview

This application allows an authorized user to:

1. **Register** students/employees with their face data (captured via webcam with consent).
2. **Recognize** registered individuals in real-time through the webcam.
3. **Automatically mark attendance** when a face is recognized.
4. **Prevent duplicate** attendance entries for the same person on the same day.
5. **View, search, and filter** attendance records.
6. **Export** attendance data to CSV.
7. **Visualize** attendance statistics with professional charts.

> **Privacy First**: All face data is processed and stored locally. No images or biometric data are uploaded to external servers. Camera activates only after explicit user action.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧑 Student Registration | Form-based registration with field validation |
| 📷 Face Capture | Multi-sample face capture (10 images) with live preview |
| 👁️ Face Detection | Real-time face detection with bounding boxes |
| 🧠 Face Recognition | LBPH-based recognition with configurable threshold |
| ✅ Attendance Marking | Automatic attendance with duplicate-per-day prevention |
| 📋 Attendance Records | Searchable, filterable table with date/student filters |
| 📊 Statistics Dashboard | Charts: daily trend, present/absent pie, per-student bar |
| 💾 CSV Export | Export filtered attendance data to CSV files |
| ⚙️ Settings | Camera index, threshold, auto-attendance, detection method |
| 🔒 Privacy Notice | Built-in consent/privacy notice |
| 🎨 Modern Dark UI | Professional CustomTkinter interface with sidebar navigation |

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **Python 3.11+** | Core programming language |
| **CustomTkinter** | Modern desktop GUI framework |
| **OpenCV** | Face detection and recognition |
| **LBPH Algorithm** | Local Binary Patterns Histograms for face matching |
| **NumPy** | Numerical processing for image arrays |
| **SQLite3** | Local relational database |
| **Matplotlib** | Charts and data visualization |
| **Pillow** | Image format conversion for GUI display |
| **pathlib** | Cross-platform file path handling |

---

## 🏗️ System Architecture

```
User Interface (CustomTkinter)
        ↓
Application Logic (Managers)
        ↓
┌───────┴────────┐
│                │
Face Detection   Face Recognition
(OpenCV DNN/     (LBPH Algorithm)
 Haar Cascade)
        ↓
Attendance Manager
        ↓
SQLite Database
        ↓
Reports / Statistics / CSV Export
```

Each layer has clear responsibilities and communicates through well-defined interfaces.

---

## 📁 Project Structure

```
Face Recognition Attendance System/
│
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── README.md                   # This file
├── PROJECT_REPORT.md           # Academic project report
├── INTERVIEW_GUIDE.md          # Interview preparation guide
├── .gitignore                  # Git ignore rules
│
├── database/
│   ├── __init__.py
│   └── database.py             # SQLite database manager
│
├── core/
│   ├── __init__.py
│   ├── face_detector.py        # Face detection (Haar + DNN)
│   ├── face_recognizer.py      # LBPH face recognition
│   ├── attendance_manager.py   # Attendance logic
│   └── student_manager.py      # Student CRUD operations
│
├── gui/
│   ├── __init__.py
│   ├── app.py                  # Main window + sidebar
│   ├── dashboard.py            # Dashboard with stat cards
│   ├── registration.py         # Student registration + face capture
│   ├── recognition.py          # Live face recognition
│   ├── attendance_view.py      # Attendance table
│   ├── statistics.py           # Charts and analytics
│   ├── settings.py             # Application settings
│   └── about.py                # About + privacy notice
│
├── utils/
│   ├── __init__.py
│   ├── config.py               # Configuration constants
│   ├── validators.py           # Input validation
│   └── helpers.py              # Utility functions
│
├── tests/
│   ├── __init__.py
│   ├── test_validators.py
│   ├── test_database.py
│   ├── test_student_manager.py
│   ├── test_attendance_manager.py
│   └── test_csv_export.py
│
├── scripts/
│   └── create_demo_data.py     # Optional demo data generator
│
├── data/
│   ├── faces/                  # Stored face images (per student)
│   └── exports/                # CSV exports
│
├── models/                     # Trained LBPH model files
└── assets/
    └── models/                 # DNN model files (optional)
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.11+** (download from [python.org](https://www.python.org/downloads/))
- **Webcam** (built-in or USB)
- **Windows 10/11** (also works on macOS/Linux)

### Setup Steps

```bash
# 1. Clone or download the project
cd "Face Recognition Attendance System"

# 2. Create a virtual environment
python -m venv venv

# 3. Activate the virtual environment
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS/Linux

# 4. Install dependencies
pip install -r requirements.txt

# 5. Run the application
python main.py
```

### Windows-Specific Notes

- If `opencv-contrib-python` fails to install, try:
  ```bash
  pip install --upgrade pip
  pip install opencv-contrib-python
  ```
- If you get a `DLL not found` error, install the [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe).

---

## ⚙️ Configuration

All settings are configurable from the **Settings** page in the application or by editing `utils/config.py`:

| Setting | Default | Description |
|---|---|---|
| `CAMERA_INDEX` | `0` | Webcam device index |
| `FACE_MATCH_THRESHOLD` | `85` | LBPH distance threshold (lower = stricter) |
| `NUM_FACE_SAMPLES` | `10` | Face images captured per registration |
| `FACE_IMAGE_SIZE` | `(200, 200)` | Standardized face image dimensions |

---

## 📖 How to Use

### Registering a Student

1. Navigate to **Register** from the sidebar.
2. Fill in student details (ID, Name, Department, Year, Email).
3. Click **Start Camera** to open the webcam.
4. Position your face clearly in front of the camera.
5. Click **Capture Face** 10 times (slight head movement between captures).
6. Click **Save Student** to register.

### Marking Attendance

1. Navigate to **Recognition** from the sidebar.
2. Click **Start Camera**.
3. Look at the camera — recognized faces are automatically marked.
4. The result panel shows name, ID, confidence, and attendance status.
5. Duplicate attendance for the same day is automatically prevented.

### Viewing Attendance

1. Navigate to **Attendance** from the sidebar.
2. Use the search bar to find specific students.
3. Use the date filter or click **Today** to filter by date.
4. Click **Export CSV** to download the records.

### Exporting Attendance

- Click **Export CSV** on the Attendance page or Dashboard.
- Files are saved to `data/exports/` as `attendance_YYYY-MM-DD.csv`.

---

## 🗃️ Database Design

### Students Table

| Column | Type | Description |
|---|---|---|
| id | INTEGER | Auto-increment primary key |
| student_id | TEXT (UNIQUE) | User-defined student identifier |
| name | TEXT | Full name |
| department | TEXT | Department/course |
| year | INTEGER | Year of study |
| email | TEXT | Email address |
| phone | TEXT | Phone number (optional) |
| face_image_path | TEXT | Path to stored face images |
| created_at | TEXT | Registration timestamp |

### Attendance Table

| Column | Type | Description |
|---|---|---|
| id | INTEGER | Auto-increment primary key |
| student_id | TEXT (FK) | References students.student_id |
| date | TEXT | Date (YYYY-MM-DD) |
| time | TEXT | Time (HH:MM:SS) |
| status | TEXT | "Present" |
| confidence | REAL | LBPH distance score |

**Constraint**: `UNIQUE(student_id, date)` prevents duplicate daily entries.

---

## 🧠 Face Recognition Workflow

```
Registration:
  Capture Face → Convert to Grayscale → Resize to 200×200 →
  Store in data/faces/{student_id}/ → Retrain LBPH Model

Recognition:
  Capture Frame → Detect Face (Haar/DNN) → Extract Face ROI →
  Grayscale → Resize to 200×200 → LBPH predict() →
  If distance < threshold → Match → Mark Attendance
  If distance ≥ threshold → "Unknown Person"
```

---

## ⚠️ Limitations

- **LBPH accuracy**: Works best in consistent lighting. Not as accurate as deep-learning models (but simpler to install and understand).
- **Single camera**: Only one webcam at a time.
- **Frontal faces**: Best with frontal face views (profile/angled faces may not be detected).
- **No encryption**: Face images are stored as plain JPEG files (suitable for a portfolio project, not production).

---

## 🔒 Privacy Considerations

- All face data is processed and stored **locally on this device**.
- No images or biometric data are uploaded to external servers.
- Camera activates **only** when the user explicitly clicks "Start Camera".
- This is an **educational/portfolio project** — not intended for covert surveillance.
- Obtain appropriate consent before registering or recognizing individuals.

---

## 🔮 Future Improvements

- [ ] Deep learning face recognition (FaceNet, ArcFace) for higher accuracy
- [ ] Multi-camera support
- [ ] Face anti-spoofing (liveness detection)
- [ ] Email notifications for attendance reports
- [ ] Admin authentication/login
- [ ] Cloud backup (opt-in, encrypted)
- [ ] Mobile companion app
- [ ] Batch registration from photos
- [ ] Face data encryption at rest

---

## 🔧 Troubleshooting

| Problem | Solution |
|---|---|
| `ModuleNotFoundError: cv2` | Run `pip install opencv-contrib-python` |
| Camera not opening | Try changing Camera Index in Settings (0, 1, 2...) |
| "No face detected" | Ensure good lighting and face the camera directly |
| Low recognition accuracy | Capture more face samples, adjust threshold in Settings |
| `DLL load failed` (Windows) | Install [Visual C++ Redistributable](https://aka.ms/vs/17/release/vc_redist.x64.exe) |
| Database locked | Close other instances of the application |

---

## 🧪 Running Tests

```bash
cd "Face Recognition Attendance System"
python -m pytest tests/ -v
```

---

## 📄 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 👨‍💻 Author

*Replace with your name and contact information.*

---

*Built with ❤️ using Python, OpenCV, and open-source technologies.*
