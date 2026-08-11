"""
Tests for core/student_manager.py

Covers registration validation, duplicate detection, and deletion.
Face images are simulated with numpy arrays.
"""

import sys
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from database.database import DatabaseManager
from core.student_manager import StudentManager


@pytest.fixture
def setup(tmp_path):
    """Create a StudentManager with temp DB and faces dir."""
    db_path = tmp_path / "test.db"
    faces_dir = tmp_path / "faces"
    db = DatabaseManager(db_path)
    mgr = StudentManager(db, faces_dir)
    return mgr, db


def _valid_data():
    return {
        "student_id": "CSE-001",
        "name": "John Doe",
        "department": "Computer Science",
        "year": "3",
        "email": "john@example.com",
        "phone": "",
    }


def _fake_faces(count=5):
    """Generate fake grayscale face images."""
    return [np.random.randint(0, 255, (200, 200), dtype=np.uint8) for _ in range(count)]


# ================================================================
# Registration
# ================================================================

class TestRegistration:
    def test_successful_registration(self, setup):
        mgr, db = setup
        success, msg = mgr.register_student(_valid_data(), _fake_faces())
        assert success is True
        assert "successfully" in msg.lower()
        assert db.student_exists("CSE-001")

    def test_registration_without_faces(self, setup):
        mgr, _ = setup
        success, msg = mgr.register_student(_valid_data(), [])
        assert success is False
        assert "face" in msg.lower()

    def test_duplicate_student_id(self, setup):
        mgr, _ = setup
        mgr.register_student(_valid_data(), _fake_faces())
        success, msg = mgr.register_student(_valid_data(), _fake_faces())
        assert success is False
        assert "already registered" in msg.lower()

    def test_invalid_data(self, setup):
        mgr, _ = setup
        bad_data = _valid_data()
        bad_data["email"] = "not-an-email"
        success, msg = mgr.register_student(bad_data, _fake_faces())
        assert success is False

    def test_face_images_saved(self, setup):
        mgr, _ = setup
        mgr.register_student(_valid_data(), _fake_faces(3))
        face_dir = mgr.faces_dir / "CSE-001"
        assert face_dir.exists()
        assert len(list(face_dir.glob("*.jpg"))) == 3


# ================================================================
# Retrieval
# ================================================================

class TestRetrieval:
    def test_get_all_students(self, setup):
        mgr, _ = setup
        d1 = _valid_data()
        d2 = _valid_data()
        d2["student_id"] = "CSE-002"
        d2["email"] = "jane@example.com"
        mgr.register_student(d1, _fake_faces())
        mgr.register_student(d2, _fake_faces())
        assert len(mgr.get_all_students()) == 2

    def test_get_student_count(self, setup):
        mgr, _ = setup
        assert mgr.get_student_count() == 0
        mgr.register_student(_valid_data(), _fake_faces())
        assert mgr.get_student_count() == 1


# ================================================================
# Deletion
# ================================================================

class TestDeletion:
    def test_delete_existing_student(self, setup):
        mgr, db = setup
        mgr.register_student(_valid_data(), _fake_faces())
        success, _ = mgr.delete_student("CSE-001")
        assert success is True
        assert not db.student_exists("CSE-001")

    def test_delete_nonexistent(self, setup):
        mgr, _ = setup
        success, _ = mgr.delete_student("NOPE")
        assert success is False

    def test_face_images_deleted(self, setup):
        mgr, _ = setup
        mgr.register_student(_valid_data(), _fake_faces())
        mgr.delete_student("CSE-001")
        assert not (mgr.faces_dir / "CSE-001").exists()
