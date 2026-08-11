"""
Tests for CSV export functionality.

Covers successful export, empty records, and file content verification.
"""

import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from database.database import DatabaseManager
from core.attendance_manager import AttendanceManager


@pytest.fixture
def setup(tmp_path):
    db_path = tmp_path / "test.db"
    exports_dir = tmp_path / "exports"
    db = DatabaseManager(db_path)
    mgr = AttendanceManager(db, exports_dir)
    # Register and mark attendance
    db.add_student("ST001", "Alice", "CS", 3, "alice@e.com")
    db.add_student("ST002", "Bob", "EE", 2, "bob@e.com")
    mgr.mark_attendance("ST001", 25.0)
    mgr.mark_attendance("ST002", 30.0)
    return mgr, exports_dir


class TestCSVExport:
    def test_export_creates_file(self, setup):
        mgr, exports_dir = setup
        success, msg = mgr.export_csv()
        assert success is True
        csv_files = list(exports_dir.glob("*.csv"))
        assert len(csv_files) == 1

    def test_export_content(self, setup):
        mgr, exports_dir = setup
        mgr.export_csv(filename="test_export.csv")
        filepath = exports_dir / "test_export.csv"

        with open(filepath, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

        assert len(rows) == 2
        assert rows[0]["Student ID"] in ("ST001", "ST002")
        assert "Name" in rows[0]
        assert "Date" in rows[0]
        assert "Time" in rows[0]

    def test_export_empty_records(self, tmp_path):
        db_path = tmp_path / "empty.db"
        exports_dir = tmp_path / "exports2"
        db = DatabaseManager(db_path)
        mgr = AttendanceManager(db, exports_dir)
        success, msg = mgr.export_csv()
        assert success is False
        assert "no records" in msg.lower()

    def test_export_with_date_filter(self, setup):
        mgr, exports_dir = setup
        success, msg = mgr.export_csv(date_filter="2000-01-01")
        # No records for year 2000
        assert success is False

    def test_custom_export_dir(self, setup, tmp_path):
        mgr, _ = setup
        custom_dir = tmp_path / "custom_exports"
        success, msg = mgr.export_csv(export_dir=custom_dir)
        assert success is True
        assert custom_dir.exists()
        csv_files = list(custom_dir.glob("*.csv"))
        assert len(csv_files) == 1
