"""
Tests for utils/validators.py

Covers all validation functions: name, student_id, email,
department, year, phone, and the combined validate_student_data.
"""

import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from utils.validators import (
    validate_name,
    validate_student_id,
    validate_email,
    validate_department,
    validate_year,
    validate_phone,
    validate_student_data,
)


# ================================================================
# validate_name
# ================================================================

class TestValidateName:
    def test_valid_name(self):
        assert validate_name("John Doe")[0] is True

    def test_empty_name(self):
        valid, msg = validate_name("")
        assert valid is False
        assert "required" in msg.lower()

    def test_whitespace_only(self):
        valid, _ = validate_name("   ")
        assert valid is False

    def test_too_short(self):
        valid, _ = validate_name("J")
        assert valid is False

    def test_name_with_special_chars(self):
        valid, _ = validate_name("O'Brien-Smith")
        assert valid is True

    def test_name_with_numbers(self):
        valid, _ = validate_name("John123")
        assert valid is False


# ================================================================
# validate_student_id
# ================================================================

class TestValidateStudentId:
    def test_valid_id(self):
        assert validate_student_id("CSE-2024-001")[0] is True

    def test_empty_id(self):
        valid, msg = validate_student_id("")
        assert valid is False
        assert "required" in msg.lower()

    def test_too_short(self):
        valid, _ = validate_student_id("A")
        assert valid is False

    def test_valid_alphanumeric(self):
        assert validate_student_id("ST001")[0] is True

    def test_invalid_chars(self):
        valid, _ = validate_student_id("ST@001")
        assert valid is False


# ================================================================
# validate_email
# ================================================================

class TestValidateEmail:
    def test_valid_email(self):
        assert validate_email("john@example.com")[0] is True

    def test_empty_email(self):
        valid, _ = validate_email("")
        assert valid is False

    def test_invalid_no_at(self):
        valid, _ = validate_email("john.example.com")
        assert valid is False

    def test_invalid_no_domain(self):
        valid, _ = validate_email("john@")
        assert valid is False

    def test_valid_with_dots(self):
        assert validate_email("john.doe@uni.edu.in")[0] is True


# ================================================================
# validate_department
# ================================================================

class TestValidateDepartment:
    def test_valid(self):
        assert validate_department("Computer Science")[0] is True

    def test_empty(self):
        valid, _ = validate_department("")
        assert valid is False

    def test_too_short(self):
        valid, _ = validate_department("A")
        assert valid is False


# ================================================================
# validate_year
# ================================================================

class TestValidateYear:
    def test_valid_year(self):
        assert validate_year("3")[0] is True

    def test_empty_year(self):
        valid, _ = validate_year("")
        assert valid is False

    def test_year_too_high(self):
        valid, _ = validate_year("7")
        assert valid is False

    def test_year_zero(self):
        valid, _ = validate_year("0")
        assert valid is False

    def test_non_numeric(self):
        valid, _ = validate_year("abc")
        assert valid is False


# ================================================================
# validate_phone
# ================================================================

class TestValidatePhone:
    def test_empty_is_valid(self):
        assert validate_phone("")[0] is True

    def test_valid_phone(self):
        assert validate_phone("+91 9876543210")[0] is True

    def test_too_short(self):
        valid, _ = validate_phone("123")
        assert valid is False

    def test_invalid_chars(self):
        valid, _ = validate_phone("abc123def")
        assert valid is False


# ================================================================
# validate_student_data
# ================================================================

class TestValidateStudentData:
    def test_all_valid(self):
        data = {
            "student_id": "CSE-001",
            "name": "John Doe",
            "department": "Computer Science",
            "year": "3",
            "email": "john@example.com",
            "phone": "",
        }
        valid, errors = validate_student_data(data)
        assert valid is True
        assert errors == []

    def test_multiple_errors(self):
        data = {
            "student_id": "",
            "name": "",
            "department": "",
            "year": "",
            "email": "",
            "phone": "",
        }
        valid, errors = validate_student_data(data)
        assert valid is False
        assert len(errors) >= 5  # At least 5 required fields fail

    def test_partial_errors(self):
        data = {
            "student_id": "CSE-001",
            "name": "John",
            "department": "CS",
            "year": "3",
            "email": "invalid",  # Bad email
            "phone": "",
        }
        valid, errors = validate_student_data(data)
        assert valid is False
        assert len(errors) == 1
