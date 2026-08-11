# 📄 Project Report — Smart Face Recognition Attendance System

---

## Abstract

This project presents the design and implementation of a **Smart Face Recognition Attendance System** — a desktop application that automates attendance tracking using computer vision and face recognition technology. Built with Python, OpenCV, and CustomTkinter, the system allows authorized administrators to register students by capturing face images via webcam, recognize them in real-time, and automatically mark attendance. Data is stored in a local SQLite database with duplicate prevention, and attendance records can be searched, filtered, exported to CSV, and visualized with charts. The project demonstrates practical skills in Python, object-oriented programming, computer vision, database management, GUI development, and modular software architecture.

---

## 1. Introduction

Attendance tracking is a routine but essential task in educational institutions and workplaces. Traditional methods — roll calls, sign-in sheets, RFID cards — are time-consuming, error-prone, and susceptible to proxy attendance. Biometric solutions using face recognition offer a contactless, automated alternative that can improve accuracy and efficiency.

This project implements a face recognition-based attendance system as a portfolio demonstration. It is designed as a local desktop application that processes and stores all data on the user's machine, with explicit consent mechanisms and privacy safeguards.

---

## 2. Problem Statement

Manual attendance tracking suffers from:

- **Time consumption**: Roll calls for large classes take 5–10 minutes each session.
- **Human error**: Incorrectly marking students, missing names, illegible handwriting.
- **Proxy attendance**: Students signing in for absent peers.
- **Data management**: Paper records are difficult to search, filter, and analyze.
- **Reporting**: Generating attendance statistics requires manual compilation.

A software solution that automates face-based attendance can address all of these issues.

---

## 3. Objectives

1. Build a desktop application for face-based attendance management.
2. Implement face detection using OpenCV.
3. Implement face recognition using the LBPH algorithm.
4. Store student data and attendance records in SQLite.
5. Prevent duplicate attendance per day.
6. Create a modern, professional GUI.
7. Support search, filter, export, and statistics.
8. Handle errors gracefully.
9. Follow modular software architecture.
10. Document the project for portfolio use.

---

## 4. Existing System

| Method | Limitations |
|---|---|
| Manual Roll Call | Time-consuming, error-prone, proxy attendance |
| RFID Cards | Cards can be lost, shared, or forgotten |
| Fingerprint | Requires physical contact, hygiene concerns |
| QR Code | Easily shared or photographed |

---

## 5. Proposed System

The proposed system uses **face recognition** to provide:

- **Contactless** attendance (no physical interaction)
- **Automated** marking (no manual input)
- **Duplicate prevention** (one entry per student per day)
- **Real-time** processing (recognition in live video)
- **Local processing** (no cloud dependency)
- **Privacy-first** design (consent-based, local storage)

---

## 6. Requirements

### 6.1 Hardware Requirements

| Component | Minimum |
|---|---|
| Processor | Intel i3 or equivalent |
| RAM | 4 GB |
| Storage | 500 MB free space |
| Camera | Any USB or built-in webcam |

### 6.2 Software Requirements

| Software | Version |
|---|---|
| Python | 3.11+ |
| OpenCV | 4.8+ |
| CustomTkinter | 5.2+ |
| SQLite | 3 (built-in) |
| Operating System | Windows 10/11, macOS, Linux |

### 6.3 Python Dependencies

| Package | Purpose |
|---|---|
| opencv-contrib-python | Face detection & LBPH recognition |
| customtkinter | Modern GUI framework |
| numpy | Numerical processing |
| matplotlib | Charts |
| Pillow | Image format conversion |
| pytest | Testing |

---

## 7. Technologies Used

### 7.1 Python
General-purpose programming language. Chosen for its extensive library ecosystem, readability, and wide adoption in AI/ML and computer vision.

### 7.2 OpenCV (Open Source Computer Vision)
Library for real-time computer vision. Provides Haar Cascade classifiers for face detection and LBPH algorithm for face recognition.

### 7.3 LBPH (Local Binary Patterns Histograms)
A texture-based face recognition algorithm that:
1. Divides a face image into cells
2. Computes local binary patterns per cell
3. Builds histograms of LBP values
4. Compares histograms using chi-square distance

### 7.4 SQLite3
Embedded relational database. Requires no server, stores data in a single file, and supports ACID transactions.

### 7.5 CustomTkinter
Modern Python GUI framework built on tkinter. Provides a professional dark-mode appearance with minimal configuration.

### 7.6 Matplotlib
Plotting library for data visualization. Used to generate attendance trend, present/absent pie chart, and per-student bar chart.

---

## 8. System Architecture

```
┌─────────────────────────────────────┐
│          User Interface             │
│     (CustomTkinter GUI Pages)       │
├─────────────────────────────────────┤
│        Application Logic            │
│  StudentManager  AttendanceManager  │
├──────────────┬──────────────────────┤
│ Face         │ Face                 │
│ Detector     │ Recognizer           │
│ (Haar/DNN)   │ (LBPH)              │
├──────────────┴──────────────────────┤
│         Database Manager            │
│         (SQLite3)                   │
├─────────────────────────────────────┤
│  Reports │ Statistics │ CSV Export  │
└─────────────────────────────────────┘
```

---

## 9. Database Design

### 9.1 Students Table

```sql
CREATE TABLE students (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id      TEXT    UNIQUE NOT NULL,
    name            TEXT    NOT NULL,
    department      TEXT    NOT NULL,
    year            INTEGER NOT NULL,
    email           TEXT    NOT NULL,
    phone           TEXT    DEFAULT '',
    face_image_path TEXT    DEFAULT '',
    created_at      TEXT    DEFAULT CURRENT_TIMESTAMP
);
```

### 9.2 Attendance Table

```sql
CREATE TABLE attendance (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id  TEXT    NOT NULL,
    date        TEXT    NOT NULL,
    time        TEXT    NOT NULL,
    status      TEXT    DEFAULT 'Present',
    confidence  REAL    DEFAULT 0.0,
    FOREIGN KEY (student_id) REFERENCES students(student_id),
    UNIQUE(student_id, date)
);
```

### 9.3 ER Diagram

```
┌──────────────┐       ┌──────────────┐
│   STUDENTS   │       │  ATTENDANCE  │
├──────────────┤       ├──────────────┤
│ PK id        │       │ PK id        │
│ UK student_id│───1:N─│ FK student_id│
│    name      │       │    date      │
│    department│       │    time      │
│    year      │       │    status    │
│    email     │       │    confidence│
│    phone     │       └──────────────┘
│    created_at│
└──────────────┘
```

---

## 10. Algorithms

### 10.1 Haar Cascade Face Detection

```
Input: BGR image frame
1. Convert to grayscale
2. Apply histogram equalization
3. Slide detection window at multiple scales
4. For each window position:
   a. Apply cascade of weak classifiers
   b. If all stages pass → face detected
   c. If any stage fails → reject (not a face)
5. Return list of bounding boxes (x, y, w, h)
```

### 10.2 LBPH Face Recognition

```
Training:
1. For each registered student:
   a. Load grayscale face images (200×200)
   b. Assign integer label
2. Train LBPH model: recognizer.train(images, labels)
3. Save model to disk

Recognition:
1. Extract detected face region from frame
2. Convert to grayscale, resize to 200×200
3. label, distance = recognizer.predict(face)
4. If distance < threshold:
      → Return (student_id, distance)  [MATCH]
5. Else:
      → Return (None, distance)  [UNKNOWN]
```

---

## 11. Implementation

### 11.1 Modules

| Module | File | Responsibility |
|---|---|---|
| Config | `utils/config.py` | Centralized constants and settings |
| Validators | `utils/validators.py` | Input validation functions |
| Helpers | `utils/helpers.py` | Date/time, CSV export, file utilities |
| Database | `database/database.py` | SQLite CRUD operations |
| Face Detector | `core/face_detector.py` | Haar Cascade and DNN face detection |
| Face Recognizer | `core/face_recognizer.py` | LBPH training and prediction |
| Student Manager | `core/student_manager.py` | Registration workflow |
| Attendance Manager | `core/attendance_manager.py` | Attendance marking and statistics |
| GUI Pages | `gui/*.py` | Dashboard, Registration, Recognition, etc. |

### 11.2 Key Design Decisions

1. **LBPH over dlib/face_recognition**: Avoided complex C++ compilation on Windows.
2. **Haar over DNN by default**: Zero-config (bundled with OpenCV), DNN available as upgrade.
3. **10 face samples**: Multiple samples improve LBPH accuracy with varied angles.
4. **Context-managed DB connections**: Prevents connection leaks and ensures rollback on error.
5. **Cooldown mechanism**: Prevents repeated recognition of the same face in rapid succession.

---

## 12. Screens

1. **Dashboard** — Statistics cards, quick actions, privacy notice
2. **Registration** — Form + live camera + face capture
3. **Recognition** — Camera feed + result panel + activity log
4. **Attendance** — Searchable/filterable table + CSV export
5. **Statistics** — Line chart, pie chart, bar chart
6. **Settings** — Camera, threshold, auto-attendance, detection method
7. **About** — App info, tech stack, privacy notice

---

## 13. Testing

### 13.1 Unit Tests

| Test File | Covers |
|---|---|
| `test_validators.py` | Name, email, ID, phone, year validation |
| `test_database.py` | Table creation, CRUD, constraints |
| `test_student_manager.py` | Registration, duplicates, deletion |
| `test_attendance_manager.py` | Marking, duplicate prevention, stats |
| `test_csv_export.py` | File creation, content, edge cases |

### 13.2 Running Tests

```bash
python -m pytest tests/ -v
```

---

## 14. Results

The system successfully:

- Registers students with validated data and captured face images
- Detects faces in real-time at ~30 FPS
- Recognizes registered students with LBPH distance scores
- Marks attendance automatically with duplicate prevention
- Displays searchable attendance records
- Exports data to CSV
- Generates professional statistical charts
- Handles errors gracefully without crashing

---

## 15. Limitations

1. LBPH is less accurate than deep learning models (FaceNet, ArcFace)
2. Sensitive to significant lighting changes
3. Works best with frontal face views
4. Single webcam support only
5. No face liveness/anti-spoofing detection
6. No encryption of stored face images
7. No user authentication (admin login)

---

## 16. Future Scope

1. Deep learning face recognition (FaceNet/ArcFace) for production-grade accuracy
2. Face anti-spoofing / liveness detection
3. Admin login with password protection
4. Encrypted face data storage
5. Email/SMS attendance notifications
6. Mobile companion app
7. Multi-camera and network camera support
8. Cloud backup with end-to-end encryption
9. Integration with institutional ERP systems
10. Batch registration from ID photos

---

## 17. Conclusion

This project demonstrates the feasibility of using face recognition technology for automated attendance management. Built with Python and OpenCV, the system provides a complete workflow from student registration to attendance reporting. The modular architecture, comprehensive error handling, and professional GUI make it suitable as a portfolio project and foundation for further development.

The use of LBPH provides a balance between simplicity and effectiveness — it is easy to understand, install, and extend, making it ideal for educational purposes while remaining functional for small-scale deployments.

---

## References

1. Viola, P. & Jones, M. (2001). "Rapid Object Detection using a Boosted Cascade of Simple Features." *IEEE CVPR*.
2. Ahonen, T., Hadid, A., & Pietikäinen, M. (2006). "Face Description with Local Binary Patterns." *IEEE TPAMI*.
3. OpenCV Documentation — https://docs.opencv.org/
4. CustomTkinter Documentation — https://customtkinter.tomschimansky.com/
5. Python SQLite3 Documentation — https://docs.python.org/3/library/sqlite3.html
