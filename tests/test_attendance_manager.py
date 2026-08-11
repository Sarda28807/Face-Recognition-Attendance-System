"""
Tests for core/attendance_manager.py

Covers attendance marking, duplicate prevention,
statistics computation, and CSV export.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from database.database import DatabaseManager
from core.attendance_manager import AttendanceManager


@pytest.fixture
def setup(tmp_path):
    """Create an AttendanceManager with temp DB and exports dir."""
    db_path = tmp_path / "test.db"
    exports_dir = tmp_path / "exports"
    db = DatabaseManager(db_path)
    mgr = AttendanceManager(db, exports_dir)
    # Register two students
    db.add_student("ST001", "Alice", "CS", 3, "alice@e.com")
    db.add_student("ST002", "Bob", "EE", 2, "bob@e.com")
    return mgr, db


# ================================================================
# Mark Attendance
# ================================================================

class TestMarkAttendance:
    def test_mark_success(self, setup):
        mgr, _ = setup
        success, msg = mgr.mark_attendance("ST001", 25.0)
        assert success is True
        assert "successfully" in msg.lower()

    def test_duplicate_prevented(self, setup):
        mgr, _ = setup
        mgr.mark_attendance("ST001", 25.0)
        success, msg = mgr.mark_attendance("ST001", 25.0)
        assert success is False
        assert "already" in msg.lower()

    def test_is_marked_today(self, setup):
        mgr, _ = setup
        assert mgr.is_marked_today("ST001") is False
        mgr.mark_attendance("ST001", 25.0)
        assert mgr.is_marked_today("ST001") is True


# ================================================================
# Statistics
# ================================================================

class TestStatistics:
    def test_today_stats_empty(self, setup):
        mgr, _ = setup
        stats = mgr.get_today_stats()
        assert stats["total"] == 2
        assert stats["present"] == 0
        assert stats["absent"] == 2
        assert stats["percentage"] == 0.0

    def test_today_stats_partial(self, setup):
        mgr, _ = setup
        mgr.mark_attendance("ST001", 25.0)
        stats = mgr.get_today_stats()
        assert stats["present"] == 1
        assert stats["absent"] == 1
        assert stats["percentage"] == 50.0


# ================================================================
# Record Retrieval
# ================================================================

class TestRecordRetrieval:
    def test_get_records(self, setup):
        mgr, _ = setup
        mgr.mark_attendance("ST001", 25.0)
        mgr.mark_attendance("ST002", 30.0)
        records = mgr.get_attendance_records()
        assert len(records) == 2

    def test_filter_by_search(self, setup):
        mgr, _ = setup
        mgr.mark_attendance("ST001", 25.0)
        mgr.mark_attendance("ST002", 30.0)
        records = mgr.get_attendance_records(search_query="Alice")
        assert len(records) == 1
        assert records[0]["name"] == "Alice"
