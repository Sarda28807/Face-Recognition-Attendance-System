"""
Optional Demo Data Generator
=============================

Creates sample student records and simulated attendance data
for demonstration purposes. All records are clearly labeled
as demo data.

Usage:
    python scripts/create_demo_data.py

WARNING: This inserts records into the live database.
         Run only for demonstration/testing purposes.
"""

import sys
import random
from pathlib import Path
from datetime import datetime, timedelta

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from utils.config import DATABASE_PATH, ensure_directories
from database.database import DatabaseManager


def create_demo_students(db: DatabaseManager) -> list:
    """Insert demo student records."""
    demo_students = [
        ("DEMO-001", "Alice Johnson",   "Computer Science", 3, "alice@demo.com"),
        ("DEMO-002", "Bob Smith",       "Electronics",      2, "bob@demo.com"),
        ("DEMO-003", "Charlie Brown",   "Mechanical",       4, "charlie@demo.com"),
        ("DEMO-004", "Diana Prince",    "Computer Science", 1, "diana@demo.com"),
        ("DEMO-005", "Eve Williams",    "Civil",            3, "eve@demo.com"),
        ("DEMO-006", "Frank Miller",    "Computer Science", 2, "frank@demo.com"),
        ("DEMO-007", "Grace Lee",       "Electronics",      3, "grace@demo.com"),
        ("DEMO-008", "Henry Davis",     "Mechanical",       1, "henry@demo.com"),
    ]

    registered = []
    for sid, name, dept, year, email in demo_students:
        if not db.student_exists(sid):
            try:
                db.add_student(sid, name, dept, year, email, phone="DEMO")
                registered.append(sid)
                print(f"  ✅ Registered: {name} ({sid})")
            except Exception as e:
                print(f"  ❌ Failed: {name} — {e}")
        else:
            print(f"  ⏭  Already exists: {sid}")
            registered.append(sid)

    return registered


def create_demo_attendance(db: DatabaseManager, student_ids: list, days: int = 7):
    """Insert simulated attendance records for the last N days."""
    today = datetime.now().date()
    count = 0

    for day_offset in range(days):
        date = today - timedelta(days=day_offset)
        date_str = date.strftime("%Y-%m-%d")

        # Randomly select 50–80% of students to be "present"
        num_present = random.randint(
            max(1, len(student_ids) // 2),
            len(student_ids),
        )
        present = random.sample(student_ids, num_present)

        for sid in present:
            # Random time between 8:00 and 10:30
            hour = random.randint(8, 10)
            minute = random.randint(0, 59)
            second = random.randint(0, 59)
            time_str = f"{hour:02d}:{minute:02d}:{second:02d}"
            confidence = random.uniform(15.0, 55.0)  # LBPH distance

            success, _ = db.mark_attendance(
                sid, date_str, time_str, "Present", round(confidence, 1)
            )
            if success:
                count += 1

    return count


def main():
    print("=" * 50)
    print("DEMO DATA GENERATOR")
    print("=" * 50)
    print()
    print("⚠️  This will insert DEMO records into the database.")
    print("    Demo student IDs are prefixed with 'DEMO-'.")
    print()

    response = input("Continue? (y/n): ").strip().lower()
    if response != "y":
        print("Cancelled.")
        return

    ensure_directories()
    db = DatabaseManager(DATABASE_PATH)

    print("\n📝 Creating demo students...")
    student_ids = create_demo_students(db)

    print(f"\n📅 Creating demo attendance (last 7 days)...")
    att_count = create_demo_attendance(db, student_ids, days=7)

    print(f"\n✅ Done!")
    print(f"   Students: {len(student_ids)}")
    print(f"   Attendance records: {att_count}")
    print()
    print("NOTE: Demo students have no face images, so they")
    print("cannot be recognized via the camera. They are for")
    print("testing the attendance table and statistics views.")


if __name__ == "__main__":
    main()
