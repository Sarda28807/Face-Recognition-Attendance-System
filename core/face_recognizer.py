"""
Face recognition module using OpenCV LBPH (Local Binary Patterns Histograms).

LBPH is a texture-based recognizer that:
  1. Divides each face into small regions.
  2. Extracts a histogram of local binary patterns per region.
  3. Compares histograms to find the closest match.

It returns a *distance* score — **lower distance = better match**.
A configurable threshold determines when to accept or reject a match.

Usage:
    recognizer = FaceRecognizer(model_path, threshold=85)
    recognizer.train(faces_dir, db_manager)
    student_id, distance = recognizer.recognize(gray_face_image)
"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple

from utils.config import FACE_IMAGE_SIZE


class FaceRecognizer:
    """Recognizes registered faces using the LBPH algorithm."""

    def __init__(self, model_path: Path, threshold: float = 85.0):
        """
        Parameters:
            model_path: directory to save/load the trained LBPH model.
            threshold: LBPH distance threshold. Matches with distance
                       above this value are rejected as 'Unknown'.
        """
        self.model_path = model_path
        self.model_path.mkdir(parents=True, exist_ok=True)

        self.threshold = threshold

        # Create a fresh recognizer instance
        self.recognizer = cv2.face.LBPHFaceRecognizer_create(
            radius=1, neighbors=8, grid_x=8, grid_y=8
        )

        # Maps internal integer labels → student_id strings
        self.label_map: Dict[int, str] = {}
        self.is_trained: bool = False

        # Attempt to load a previously trained model
        self._load_model()

    # ================================================================
    # Model Persistence
    # ================================================================

    def _model_file(self) -> Path:
        return self.model_path / "face_model.yml"

    def _label_file(self) -> Path:
        return self.model_path / "label_map.npy"

    def _load_model(self) -> None:
        """Load a trained LBPH model and label map from disk."""
        model_f = self._model_file()
        label_f = self._label_file()

        if model_f.exists() and label_f.exists():
            try:
                self.recognizer.read(str(model_f))
                self.label_map = np.load(
                    str(label_f), allow_pickle=True
                ).item()
                self.is_trained = True
            except Exception:
                self.is_trained = False

    def _save_model(self) -> None:
        """Persist the trained model and label map to disk."""
        self.recognizer.save(str(self._model_file()))
        np.save(str(self._label_file()), self.label_map)

    # ================================================================
    # Training
    # ================================================================

    def train(self, faces_dir: Path, db_manager) -> Tuple[bool, str]:
        """
        Train (or retrain) the LBPH model from stored face images.

        Folder structure expected:
            faces_dir/
                <student_id_1>/
                    face_000.jpg
                    face_001.jpg
                    ...
                <student_id_2>/
                    ...

        Parameters:
            faces_dir: root directory containing per-student face folders.
            db_manager: DatabaseManager instance for student look-up.

        Returns:
            (success: bool, message: str)
        """
        faces = []
        labels = []
        self.label_map = {}

        students = db_manager.get_all_students()
        if not students:
            self.is_trained = False
            return False, "No registered students found."

        students_with_faces = 0

        for student in students:
            student_face_dir = faces_dir / student["student_id"]
            if not student_face_dir.exists():
                continue

            internal_id = student["id"]  # Integer label for LBPH
            self.label_map[internal_id] = student["student_id"]

            img_count = 0
            for img_file in sorted(student_face_dir.glob("*.jpg")):
                img = cv2.imread(str(img_file), cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    img = cv2.resize(img, FACE_IMAGE_SIZE, interpolation=cv2.INTER_AREA)
                    faces.append(img)
                    labels.append(internal_id)
                    img_count += 1

            if img_count > 0:
                students_with_faces += 1

        if not faces:
            self.is_trained = False
            return False, "No face images found for training."

        # Train LBPH
        labels_array = np.array(labels, dtype=np.int32)
        self.recognizer = cv2.face.LBPHFaceRecognizer_create(
            radius=1, neighbors=8, grid_x=8, grid_y=8
        )
        self.recognizer.train(faces, labels_array)
        self.is_trained = True
        self._save_model()

        return True, (
            f"Model trained with {len(faces)} images "
            f"from {students_with_faces} student(s)."
        )

    # ================================================================
    # Recognition
    # ================================================================

    def recognize(
        self, face_image: np.ndarray
    ) -> Tuple[Optional[str], float]:
        """
        Recognize a face.

        Parameters:
            face_image: grayscale or BGR face image (will be converted).

        Returns:
            (student_id, distance) if the distance is below the threshold,
            otherwise (None, distance).
            Lower distance = better match.
        """
        if not self.is_trained:
            return None, 999.0

        # Ensure grayscale
        if len(face_image.shape) == 3:
            face_image = cv2.cvtColor(face_image, cv2.COLOR_BGR2GRAY)

        face_image = cv2.resize(
            face_image, FACE_IMAGE_SIZE, interpolation=cv2.INTER_AREA
        )

        try:
            label, distance = self.recognizer.predict(face_image)
        except cv2.error:
            return None, 999.0

        if distance < self.threshold:
            student_id = self.label_map.get(label)
            if student_id is not None:
                return student_id, distance

        return None, distance

    # ================================================================
    # Configuration
    # ================================================================

    def update_threshold(self, new_threshold: float) -> None:
        """Change the recognition threshold at runtime."""
        self.threshold = new_threshold
