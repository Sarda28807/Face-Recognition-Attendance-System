"""
Attendance management module for the Face Attendance System.

Responsibilities:
- Mark attendance (with duplicate-per-day prevention)
- Retrieve and filter attendance records
- Compute attendance statistics
- Export records to CSV
"""

from pathlib import Path
from typing import Dict, List, Optional, Tuple

from database.database import DatabaseManager
from utils.helpers import export_attendance_to_csv, get_date_string, get_time_string


class AttendanceManager:
    """Manages attendance marking, retrieval, statistics, and CSV export."""

    def __init__(self, db: DatabaseManager, exports_dir: Path):
        """
        Parameters:
            db: DatabaseManager instance.
            exports_dir: directory for CSV exports.
        """
        self.db = db
        self.exports_dir = exports_dir
        self.exports_dir.mkdir(parents=True, exist_ok=True)

    # ================================================================
    # Mark Attendance
    # ================================================================

    def mark_attendance(
        self, student_id: str, confidence: float
    ) -> Tuple[bool, str]:
        """
        Mark a student as present for today.

        Prevents duplicate attendance for the same student on the same day
        via a UNIQUE constraint in the database.

        Parameters:
            student_id: the student's unique identifier.
            confidence: LBPH distance score at the time of recognition.

        Returns:
            (success: bool, message: str)
        """
        today = get_date_string()
        now = get_time_string()

        # Check for duplicate before attempting insert
        if self.db.is_attendance_marked(student_id, today):
            return False, "Attendance already marked for today."

        return self.db.mark_attendance(
            student_id, today, now, "Present", confidence
        )

    def is_marked_today(self, student_id: str) -> bool:
        """Check if a student already has attendance for today."""
        return self.db.is_attendance_marked(student_id, get_date_string())

    # ================================================================
    # Statistics
    # ================================================================

    def get_today_stats(self) -> Dict[str, object]:
        """
        Compute today's attendance summary.

        Returns:
            {
                'total': int,       # total registered students
                'present': int,     # students marked present today
                'absent': int,      # students not yet marked
                'percentage': float  # attendance percentage
            }
        """
        today = get_date_string()
        total_students = self.db.get_student_count()
        present_today = self.db.get_today_present_count(today)
        absent_today = max(0, total_students - present_today)
        percentage = (
            round(present_today / total_students * 100, 1)
            if total_students > 0
            else 0.0
        )

        return {
            "total": total_students,
            "present": present_today,
            "absent": absent_today,
            "percentage": percentage,
        }

    def get_daily_summary(self, days: int = 7) -> List[Dict]:
        """Per-day attendance counts for the last N recorded days."""
        return self.db.get_daily_attendance_summary(days)

    def get_student_stats(self) -> List[Dict]:
        """Per-student attendance counts across all dates."""
        return self.db.get_student_attendance_stats()

    # ================================================================
    # Record Retrieval
    # ================================================================

    def get_attendance_records(
        self,
        date_filter: Optional[str] = None,
        student_filter: Optional[str] = None,
        search_query: Optional[str] = None,
    ) -> List[Dict]:
        """
        Retrieve attendance records with optional filtering.

        Parameters:
            date_filter: 'YYYY-MM-DD' to filter by date.
            student_filter: student_id to filter by student.
            search_query: free-text search on student_id or name.
        """
        return self.db.get_attendance(
            date_filter=date_filter,
            student_filter=student_filter,
            search_query=search_query,
        )

    # ================================================================
    # CSV Export
    # ================================================================

    def export_csv(
        self,
        date_filter: Optional[str] = None,
        filename: Optional[str] = None,
        export_dir: Optional[Path] = None,
    ) -> Tuple[bool, str]:
        """
        Export attendance records to a CSV file.

        Parameters:
            date_filter: optional date to export.
            filename: custom filename (auto-generated if None).
            export_dir: override the default exports directory.

        Returns:
            (success: bool, message: str)
        """
        records = self.get_attendance_records(date_filter=date_filter)

        if not filename:
            date_str = date_filter or get_date_string()
            filename = f"attendance_{date_str}.csv"

        target_dir = export_dir or self.exports_dir
        filepath = Path(target_dir) / filename

        return export_attendance_to_csv(records, filepath)
