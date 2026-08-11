"""
Student management module for the Face Attendance System.

Handles student registration including:
- Input validation
- Duplicate ID detection
- Face image storage
- Database insertion
- Cleanup on failure
"""

import shutil
import cv2
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from database.database import DatabaseManager
from utils.validators import validate_student_data


class StudentManager:
    """Manages student registration, retrieval, and deletion."""

    def __init__(self, db: DatabaseManager, faces_dir: Path):
        """
        Parameters:
            db: DatabaseManager instance.
            faces_dir: root directory for storing face images
                       (each student gets a subfolder).
        """
        self.db = db
        self.faces_dir = faces_dir
        self.faces_dir.mkdir(parents=True, exist_ok=True)

    # ================================================================
    # Registration
    # ================================================================

    def register_student(
        self,
        data: Dict[str, str],
        face_images: list,
    ) -> Tuple[bool, str]:
        """
        Register a new student with their face images.

        Parameters:
            data: dict with keys — student_id, name, department, year,
                  email, phone.
            face_images: list of grayscale numpy arrays (captured faces).

        Returns:
            (success: bool, message: str)
        """
        # 1. Validate fields
        is_valid, errors = validate_student_data(data)
        if not is_valid:
            return False, "\n".join(errors)

        student_id = data["student_id"].strip()

        # 2. Check for duplicate student ID
        if self.db.student_exists(student_id):
            return False, "This Student ID is already registered."

        # 3. Check face images
        if not face_images:
            return False, "No face images captured. Please capture face images."

        # 4. Save face images to disk
        student_face_dir = self.faces_dir / student_id
        student_face_dir.mkdir(parents=True, exist_ok=True)

        for i, face_img in enumerate(face_images):
            img_path = student_face_dir / f"face_{i:03d}.jpg"
            cv2.imwrite(str(img_path), face_img)

        # 5. Insert into database
        try:
            self.db.add_student(
                student_id=student_id,
                name=data["name"].strip(),
                department=data["department"].strip(),
                year=data["year"].strip(),
                email=data["email"].strip(),
                phone=data.get("phone", "").strip(),
                face_image_path=str(student_face_dir),
            )
            return True, f"Student '{data['name'].strip()}' registered successfully!"

        except Exception as e:
            # Cleanup face images if DB insertion fails
            shutil.rmtree(student_face_dir, ignore_errors=True)
            return False, f"Database error: {e}"

    # ================================================================
    # Retrieval
    # ================================================================

    def get_all_students(self) -> List[Dict]:
        """Return all registered students."""
        return self.db.get_all_students()

    def get_student(self, student_id: str) -> Optional[Dict]:
        """Get a single student by student_id."""
        return self.db.get_student(student_id)

    def get_student_count(self) -> int:
        """Return total number of registered students."""
        return self.db.get_student_count()

    # ================================================================
    # Deletion
    # ================================================================

    def delete_student(self, student_id: str) -> Tuple[bool, str]:
        """
        Delete a student and their stored face images.

        Returns:
            (success: bool, message: str)
        """
        # Remove face images
        student_face_dir = self.faces_dir / student_id
        if student_face_dir.exists():
            shutil.rmtree(student_face_dir, ignore_errors=True)

        # Remove from database
        if self.db.delete_student(student_id):
            return True, f"Student '{student_id}' deleted successfully."
        return False, f"Student '{student_id}' not found."
