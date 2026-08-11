"""
Tests for database/database.py

Uses a temporary in-memory (or temp-file) database for each test
to ensure isolation.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from database.database import DatabaseManager


@pytest.fixture
def db(tmp_path):
    """Create a fresh database for each test."""
    db_path = tmp_path / "test_attendance.db"
    return DatabaseManager(db_path)


# ================================================================
# Table Creation
# ================================================================

class TestTableCreation:
    def test_tables_created(self, db):
        """Tables should be created automatically on init."""
        with db.get_connection() as conn:
            tables = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
            table_names = {t["name"] for t in tables}
        assert "students" in table_names
        assert "attendance" in table_names
        assert "settings" in table_names


# ================================================================
# Student CRUD
# ================================================================

class TestStudentCRUD:
    def test_add_and_get_student(self, db):
        db.add_student("ST001", "John Doe", "CS", 3, "john@example.com")
        student = db.get_student("ST001")
        assert student is not None
        assert student["name"] == "John Doe"
        assert student["department"] == "CS"

    def test_student_exists(self, db):
        db.add_student("ST001", "John", "CS", 3, "j@e.com")
        assert db.student_exists("ST001") is True
        assert db.student_exists("ST999") is False

    def test_duplicate_student_id_raises(self, db):
        db.add_student("ST001", "John", "CS", 3, "j@e.com")
        with pytest.raises(Exception):
            db.add_student("ST001", "Jane", "EE", 2, "jane@e.com")

    def test_get_student_count(self, db):
        assert db.get_student_count() == 0
        db.add_student("ST001", "John", "CS", 3, "j@e.com")
        db.add_student("ST002", "Jane", "EE", 2, "jane@e.com")
        assert db.get_student_count() == 2

    def test_get_all_students(self, db):
        db.add_student("ST001", "Alice", "CS", 1, "a@e.com")
        db.add_student("ST002", "Bob", "EE", 2, "b@e.com")
        students = db.get_all_students()
        assert len(students) == 2
        # Ordered by name
        assert students[0]["name"] == "Alice"

    def test_delete_student(self, db):
        db.add_student("ST001", "John", "CS", 3, "j@e.com")
        assert db.delete_student("ST001") is True
        assert db.get_student("ST001") is None

    def test_delete_nonexistent_student(self, db):
        assert db.delete_student("NOPE") is False

    def test_get_student_by_internal_id(self, db):
        db.add_student("ST001", "John", "CS", 3, "j@e.com")
        student = db.get_student("ST001")
        fetched = db.get_student_by_internal_id(student["id"])
        assert fetched is not None
        assert fetched["student_id"] == "ST001"


# ================================================================
# Attendance Operations
# ================================================================

class TestAttendance:
    def _register_student(self, db):
        db.add_student("ST001", "John", "CS", 3, "j@e.com")

    def test_mark_attendance(self, db):
        self._register_student(db)
        success, msg = db.mark_attendance("ST001", "2026-08-11", "10:00:00")
        assert success is True

    def test_duplicate_attendance_rejected(self, db):
        self._register_student(db)
        db.mark_attendance("ST001", "2026-08-11", "10:00:00")
        success, msg = db.mark_attendance("ST001", "2026-08-11", "11:00:00")
        assert success is False
        assert "already" in msg.lower()

    def test_different_days_allowed(self, db):
        self._register_student(db)
        s1, _ = db.mark_attendance("ST001", "2026-08-11", "10:00:00")
        s2, _ = db.mark_attendance("ST001", "2026-08-12", "10:00:00")
        assert s1 is True
        assert s2 is True

    def test_is_attendance_marked(self, db):
        self._register_student(db)
        assert db.is_attendance_marked("ST001", "2026-08-11") is False
        db.mark_attendance("ST001", "2026-08-11", "10:00:00")
        assert db.is_attendance_marked("ST001", "2026-08-11") is True

    def test_get_today_present_count(self, db):
        db.add_student("ST001", "John", "CS", 3, "j@e.com")
        db.add_student("ST002", "Jane", "EE", 2, "jane@e.com")
        db.mark_attendance("ST001", "2026-08-11", "10:00:00")
        assert db.get_today_present_count("2026-08-11") == 1

    def test_get_attendance_with_filters(self, db):
        db.add_student("ST001", "John", "CS", 3, "j@e.com")
        db.add_student("ST002", "Jane", "EE", 2, "jane@e.com")
        db.mark_attendance("ST001", "2026-08-11", "10:00:00")
        db.mark_attendance("ST002", "2026-08-11", "10:05:00")
        db.mark_attendance("ST001", "2026-08-12", "10:00:00")

        # All records
        all_records = db.get_attendance()
        assert len(all_records) == 3

        # Filter by date
        today = db.get_attendance(date_filter="2026-08-11")
        assert len(today) == 2

        # Filter by student
        st1 = db.get_attendance(student_filter="ST001")
        assert len(st1) == 2

        # Search
        results = db.get_attendance(search_query="Jane")
        assert len(results) == 1


# ================================================================
# Settings
# ================================================================

class TestSettings:
    def test_save_and_get_setting(self, db):
        db.save_setting("theme", "dark")
        assert db.get_setting("theme") == "dark"

    def test_default_setting(self, db):
        assert db.get_setting("missing_key", "default") == "default"

    def test_update_setting(self, db):
        db.save_setting("theme", "dark")
        db.save_setting("theme", "light")
        assert db.get_setting("theme") == "light"
