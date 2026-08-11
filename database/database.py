"""
SQLite database manager for the Face Attendance System.

Handles all database operations with:
- Automatic table creation on first run
- Parameterized queries (no SQL injection)
- Context-managed connections (auto-commit/rollback)
- Foreign key enforcement
"""

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Dict, List, Optional


class DatabaseManager:
    """Manages the SQLite database for students and attendance records."""

    def __init__(self, db_path: Path):
        """
        Initialize the database manager.

        Parameters:
            db_path: Path to the SQLite database file.
                     The file and parent directories are created automatically.
        """
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._create_tables()

    # ================================================================
    # Connection Management
    # ================================================================

    @contextmanager
    def get_connection(self):
        """
        Context manager that provides a database connection.
        Commits on success, rolls back on error, always closes.
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row  # Access columns by name
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except sqlite3.Error:
            conn.rollback()
            raise
        finally:
            conn.close()

    # ================================================================
    # Table Creation
    # ================================================================

    def _create_tables(self) -> None:
        """Create the students, attendance, and settings tables if absent."""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS students (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id      TEXT    UNIQUE NOT NULL,
                    name            TEXT    NOT NULL,
                    department      TEXT    NOT NULL,
                    year            INTEGER NOT NULL,
                    email           TEXT    NOT NULL,
                    phone           TEXT    DEFAULT '',
                    face_image_path TEXT    DEFAULT '',
                    created_at      TEXT    DEFAULT CURRENT_TIMESTAMP
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS attendance (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id  TEXT    NOT NULL,
                    date        TEXT    NOT NULL,
                    time        TEXT    NOT NULL,
                    status      TEXT    DEFAULT 'Present',
                    confidence  REAL    DEFAULT 0.0,
                    FOREIGN KEY (student_id) REFERENCES students(student_id)
                        ON DELETE CASCADE,
                    UNIQUE(student_id, date)
                )
            """)

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key   TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)

    # ================================================================
    # Student CRUD
    # ================================================================

    def add_student(
        self,
        student_id: str,
        name: str,
        department: str,
        year: int,
        email: str,
        phone: str = "",
        face_image_path: str = "",
    ) -> None:
        """Insert a new student record."""
        with self.get_connection() as conn:
            conn.execute(
                """INSERT INTO students
                   (student_id, name, department, year, email, phone, face_image_path)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (student_id, name, department, int(year), email, phone, face_image_path),
            )

    def get_student(self, student_id: str) -> Optional[Dict]:
        """Fetch a single student by their student_id."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM students WHERE student_id = ?", (student_id,)
            ).fetchone()
            return dict(row) if row else None

    def get_student_by_internal_id(self, internal_id: int) -> Optional[Dict]:
        """Fetch a single student by their internal auto-increment id."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM students WHERE id = ?", (internal_id,)
            ).fetchone()
            return dict(row) if row else None

    def get_all_students(self) -> List[Dict]:
        """Return all students ordered by name."""
        with self.get_connection() as conn:
            rows = conn.execute(
                "SELECT * FROM students ORDER BY name"
            ).fetchall()
            return [dict(r) for r in rows]

    def student_exists(self, student_id: str) -> bool:
        """Check whether a student_id is already registered."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM students WHERE student_id = ?", (student_id,)
            ).fetchone()
            return row is not None

    def get_student_count(self) -> int:
        """Return the total number of registered students."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS count FROM students"
            ).fetchone()
            return row["count"]

    def delete_student(self, student_id: str) -> bool:
        """Delete a student and cascade-delete their attendance. Returns True if found."""
        with self.get_connection() as conn:
            # Delete attendance records first (manual cascade for safety)
            conn.execute(
                "DELETE FROM attendance WHERE student_id = ?", (student_id,)
            )
            cursor = conn.execute(
                "DELETE FROM students WHERE student_id = ?", (student_id,)
            )
            return cursor.rowcount > 0

    # ================================================================
    # Attendance Operations
    # ================================================================

    def mark_attendance(
        self,
        student_id: str,
        date: str,
        time: str,
        status: str = "Present",
        confidence: float = 0.0,
    ) -> tuple:
        """
        Insert an attendance record.

        Returns:
            (success: bool, message: str)
        """
        try:
            with self.get_connection() as conn:
                conn.execute(
                    """INSERT INTO attendance (student_id, date, time, status, confidence)
                       VALUES (?, ?, ?, ?, ?)""",
                    (student_id, date, time, status, confidence),
                )
            return True, "Attendance marked successfully."
        except sqlite3.IntegrityError:
            return False, "Attendance already marked for today."

    def is_attendance_marked(self, student_id: str, date: str) -> bool:
        """Check if a student already has an attendance record for the given date."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT 1 FROM attendance WHERE student_id = ? AND date = ?",
                (student_id, date),
            ).fetchone()
            return row is not None

    def get_attendance(
        self,
        date_filter: Optional[str] = None,
        student_filter: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> List[Dict]:
        """
        Retrieve attendance records with optional filters.

        Parameters:
            date_filter: 'YYYY-MM-DD' — show only this date.
            student_filter: student_id — show only this student.
            search_query: free-text search on student_id or name.
        """
        with self.get_connection() as conn:
            query = """
                SELECT a.student_id, s.name, a.date, a.time,
                       a.status, a.confidence
                FROM attendance a
                JOIN students s ON a.student_id = s.student_id
                WHERE 1 = 1
            """
            params: list = []

            if date_filter:
                query += " AND a.date = ?"
                params.append(date_filter)

            if student_filter:
                query += " AND a.student_id = ?"
                params.append(student_filter)

            if search_query:
                query += " AND (a.student_id LIKE ? OR s.name LIKE ?)"
                like = f"%{search_query}%"
                params.extend([like, like])

            query += " ORDER BY a.date DESC, a.time DESC"

            rows = conn.execute(query, params).fetchall()
            return [dict(r) for r in rows]

    def get_today_present_count(self, date: str) -> int:
        """Count how many students are marked present on the given date."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS count FROM attendance WHERE date = ?",
                (date,),
            ).fetchone()
            return row["count"]

    def get_attendance_by_date_range(
        self, start_date: str, end_date: str
    ) -> List[Dict]:
        """Return attendance records within a date range (inclusive)."""
        with self.get_connection() as conn:
            rows = conn.execute(
                """SELECT a.student_id, s.name, a.date, a.time,
                          a.status, a.confidence
                   FROM attendance a
                   JOIN students s ON a.student_id = s.student_id
                   WHERE a.date BETWEEN ? AND ?
                   ORDER BY a.date DESC, a.time DESC""",
                (start_date, end_date),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_daily_attendance_summary(self, days: int = 7) -> List[Dict]:
        """
        Return per-day attendance counts for the last N recorded days.

        Returns:
            List of {'date': str, 'present_count': int}
        """
        with self.get_connection() as conn:
            rows = conn.execute(
                """SELECT date, COUNT(*) AS present_count
                   FROM attendance
                   GROUP BY date
                   ORDER BY date DESC
                   LIMIT ?""",
                (days,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_student_attendance_stats(self) -> List[Dict]:
        """
        Return per-student attendance counts.

        Returns:
            List of {'student_id': str, 'name': str, 'days_present': int}
        """
        with self.get_connection() as conn:
            rows = conn.execute(
                """SELECT s.student_id, s.name,
                          COUNT(a.id) AS days_present
                   FROM students s
                   LEFT JOIN attendance a ON s.student_id = a.student_id
                   GROUP BY s.student_id, s.name
                   ORDER BY days_present DESC"""
            ).fetchall()
            return [dict(r) for r in rows]

    # ================================================================
    # Settings Key-Value Store
    # ================================================================

    def save_setting(self, key: str, value: str) -> None:
        """Insert or update a setting."""
        with self.get_connection() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)",
                (key, value),
            )

    def get_setting(self, key: str, default: str = "") -> str:
        """Read a setting value, returning *default* if not found."""
        with self.get_connection() as conn:
            row = conn.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            ).fetchone()
            return row["value"] if row else default
