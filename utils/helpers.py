"""
General-purpose helper functions for the Face Attendance System.

Includes file handling, date/time formatting, CSV export,
and network download utilities.
"""

import csv
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Callable, List, Optional, Tuple


# ============================================================
# Date & Time Helpers
# ============================================================

def get_timestamp() -> str:
    """Return current date-time as 'YYYY-MM-DD HH:MM:SS'."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def get_date_string() -> str:
    """Return current date as 'YYYY-MM-DD'."""
    return datetime.now().strftime("%Y-%m-%d")


def get_time_string() -> str:
    """Return current time as 'HH:MM:SS'."""
    return datetime.now().strftime("%H:%M:%S")


def get_display_date() -> str:
    """Return a human-readable date string (e.g., 'August 11, 2026')."""
    return datetime.now().strftime("%B %d, %Y")


def get_display_time() -> str:
    """Return a human-readable time string (e.g., '10:30:15 AM')."""
    return datetime.now().strftime("%I:%M:%S %p")


# ============================================================
# File Helpers
# ============================================================

def safe_filename(name: str) -> str:
    """Convert an arbitrary string into a filesystem-safe filename."""
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in name)


def ensure_directories(directories: List[Path]) -> None:
    """Create multiple directories if they do not already exist."""
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)


# ============================================================
# CSV Export
# ============================================================

def export_attendance_to_csv(
    records: List[dict],
    filepath: Path,
) -> Tuple[bool, str]:
    """
    Export attendance records to a CSV file.

    Parameters:
        records: list of dicts with keys matching the CSV columns.
        filepath: destination CSV file path.

    Returns:
        (success: bool, message: str)
    """
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)

        if not records:
            return False, "No records to export."

        fieldnames = [
            "Student ID", "Name", "Date", "Time", "Status", "Confidence"
        ]

        with open(filepath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for record in records:
                writer.writerow({
                    "Student ID": record.get("student_id", ""),
                    "Name": record.get("name", ""),
                    "Date": record.get("date", ""),
                    "Time": record.get("time", ""),
                    "Status": record.get("status", ""),
                    "Confidence": f"{record.get('confidence', 0):.1f}",
                })

        return True, f"Exported {len(records)} records to {filepath.name}"

    except PermissionError:
        return False, f"Permission denied: cannot write to {filepath}"
    except IOError as e:
        return False, f"File error: {e}"


# ============================================================
# Network Helpers
# ============================================================

def download_file(
    url: str,
    destination: Path,
    callback: Optional[Callable[[float], None]] = None,
) -> Tuple[bool, str]:
    """
    Download a file from a URL.

    Parameters:
        url: source URL.
        destination: local file path.
        callback: optional function(progress_percent) for progress updates.

    Returns:
        (success: bool, message: str)
    """
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)

        def _reporthook(block_num, block_size, total_size):
            if callback and total_size > 0:
                progress = min(block_num * block_size / total_size * 100, 100)
                callback(progress)

        urllib.request.urlretrieve(url, str(destination), reporthook=_reporthook)
        return True, "Download complete."

    except Exception as e:
        return False, f"Download failed: {e}"


# ============================================================
# Confidence Formatting
# ============================================================

def format_confidence(distance: float) -> str:
    """
    Convert LBPH distance to a human-readable percentage.

    LBPH returns a *distance* score where lower = better match.
    This function maps it to a 0–100 % scale for user display:
        distance  0 → 100 %  (perfect match)
        distance 100 →   0 %
    """
    if distance <= 0:
        return "100.0%"
    percentage = max(0.0, min(100.0, 100.0 - distance))
    return f"{percentage:.1f}%"


def confidence_to_percentage(distance: float) -> float:
    """Return the numeric percentage value (0–100) from LBPH distance."""
    if distance <= 0:
        return 100.0
    return max(0.0, min(100.0, 100.0 - distance))
