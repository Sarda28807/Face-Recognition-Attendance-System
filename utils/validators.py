"""
Input validation functions for the Face Attendance System.

Each validator returns a tuple: (is_valid: bool, error_message: str).
An empty error_message means the input is valid.
"""

import re
from typing import Tuple, List


def validate_name(name: str) -> Tuple[bool, str]:
    """Validate a student's full name."""
    if not name or not name.strip():
        return False, "Name is required."
    name = name.strip()
    if len(name) < 2:
        return False, "Name must be at least 2 characters long."
    if len(name) > 100:
        return False, "Name must be less than 100 characters."
    if not re.match(r"^[a-zA-Z\s.\-']+$", name):
        return False, "Name can only contain letters, spaces, dots, hyphens, and apostrophes."
    return True, ""


def validate_student_id(student_id: str) -> Tuple[bool, str]:
    """Validate a student ID (e.g., ST001, CSE-2024-001)."""
    if not student_id or not student_id.strip():
        return False, "Student ID is required."
    student_id = student_id.strip()
    if len(student_id) < 2:
        return False, "Student ID must be at least 2 characters long."
    if len(student_id) > 20:
        return False, "Student ID must be less than 20 characters."
    if not re.match(r"^[a-zA-Z0-9\-_]+$", student_id):
        return False, "Student ID can only contain letters, numbers, hyphens, and underscores."
    return True, ""


def validate_email(email: str) -> Tuple[bool, str]:
    """Validate an email address format."""
    if not email or not email.strip():
        return False, "Email is required."
    email = email.strip()
    pattern = r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False, "Please enter a valid email address."
    return True, ""


def validate_department(department: str) -> Tuple[bool, str]:
    """Validate department name."""
    if not department or not department.strip():
        return False, "Department is required."
    department = department.strip()
    if len(department) < 2:
        return False, "Department name must be at least 2 characters long."
    if len(department) > 50:
        return False, "Department name must be less than 50 characters."
    return True, ""


def validate_year(year: str) -> Tuple[bool, str]:
    """Validate year of study (1–6)."""
    if not year or not str(year).strip():
        return False, "Year is required."
    try:
        y = int(str(year).strip())
        if y < 1 or y > 6:
            return False, "Year must be between 1 and 6."
    except ValueError:
        return False, "Year must be a number between 1 and 6."
    return True, ""


def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Validate a phone number (optional field).
    Returns valid if empty, since phone is not required.
    """
    if not phone or not phone.strip():
        return True, ""  # Phone is optional
    phone = phone.strip()
    # Strip formatting characters for digit-length check
    cleaned = re.sub(r"[\s\-\(\)\+]", "", phone)
    if not cleaned.isdigit():
        return False, "Phone number can only contain digits, spaces, hyphens, +, and parentheses."
    if len(cleaned) < 7 or len(cleaned) > 15:
        return False, "Phone number must be between 7 and 15 digits."
    return True, ""


def validate_student_data(data: dict) -> Tuple[bool, List[str]]:
    """
    Validate all student registration fields at once.

    Parameters:
        data: dict with keys: student_id, name, department, year, email, phone

    Returns:
        (all_valid: bool, list_of_error_messages: list[str])
    """
    errors: List[str] = []

    validations = [
        validate_student_id(data.get("student_id", "")),
        validate_name(data.get("name", "")),
        validate_department(data.get("department", "")),
        validate_year(data.get("year", "")),
        validate_email(data.get("email", "")),
        validate_phone(data.get("phone", "")),
    ]

    for is_valid, error in validations:
        if not is_valid:
            errors.append(error)

    return len(errors) == 0, errors
