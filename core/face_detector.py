"""
Face detection module using OpenCV.

Supports two detection backends:
  1. Haar Cascade (default) — bundled with OpenCV, no extra downloads.
  2. DNN SSD Detector — higher accuracy, requires model files.

Usage:
    detector = FaceDetector(method='haar')
    faces = detector.detect_faces(frame)
    # faces → list of (x, y, w, h, confidence)
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional


class FaceDetector:
    """Detects faces in images or video frames."""

    def __init__(
        self,
        method: str = "haar",
        confidence_threshold: float = 0.5,
        dnn_models_dir: Optional[Path] = None,
    ):
        """
        Parameters:
            method: 'haar' or 'dnn'.
            confidence_threshold: minimum confidence for DNN detections.
            dnn_models_dir: directory containing DNN model files.
        """
        self.method = method
        self.confidence_threshold = confidence_threshold
        self._haar_cascade: Optional[cv2.CascadeClassifier] = None
        self._dnn_net = None
        self._dnn_models_dir = dnn_models_dir

        self._initialize_detector()

    # ================================================================
    # Initialisation
    # ================================================================

    def _initialize_detector(self) -> None:
        """Load the chosen face-detection model."""
        if self.method == "dnn":
            if not self._try_load_dnn():
                # Fall back to Haar if DNN models are missing
                self.method = "haar"
                self._load_haar()
        else:
            self._load_haar()

    def _load_haar(self) -> None:
        """Load the Haar Cascade classifier bundled with OpenCV."""
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self._haar_cascade = cv2.CascadeClassifier(cascade_path)
        if self._haar_cascade.empty():
            raise RuntimeError(
                "Failed to load Haar Cascade classifier. "
                "Verify that opencv-contrib-python is installed correctly."
            )

    def _try_load_dnn(self) -> bool:
        """Attempt to load the Caffe DNN face detector. Returns True on success."""
        if self._dnn_models_dir is None:
            return False

        prototxt = self._dnn_models_dir / "deploy.prototxt"
        caffemodel = self._dnn_models_dir / "res10_300x300_ssd_iter_140000.caffemodel"

        if not prototxt.exists() or not caffemodel.exists():
            return False

        try:
            self._dnn_net = cv2.dnn.readNetFromCaffe(str(prototxt), str(caffemodel))
            return True
        except cv2.error:
            return False

    # ================================================================
    # Detection
    # ================================================================

    def detect_faces(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """
        Detect faces in a BGR frame.

        Returns:
            List of (x, y, width, height, confidence) tuples.
        """
        if frame is None or frame.size == 0:
            return []

        if self.method == "dnn" and self._dnn_net is not None:
            return self._detect_dnn(frame)
        return self._detect_haar(frame)

    def _detect_haar(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """Haar Cascade detection (returns confidence = 1.0 for all detections)."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)  # Improve detection in varied lighting

        faces = self._haar_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(60, 60),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )

        return [(int(x), int(y), int(w), int(h), 1.0) for (x, y, w, h) in faces]

    def _detect_dnn(self, frame: np.ndarray) -> List[Tuple[int, int, int, int, float]]:
        """DNN SSD detection with confidence filtering."""
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame, (300, 300)),
            scalefactor=1.0,
            size=(300, 300),
            mean=(104.0, 177.0, 123.0),
        )
        self._dnn_net.setInput(blob)
        detections = self._dnn_net.forward()

        faces: List[Tuple[int, int, int, int, float]] = []
        for i in range(detections.shape[2]):
            confidence = float(detections[0, 0, i, 2])
            if confidence < self.confidence_threshold:
                continue

            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
            x1, y1, x2, y2 = box.astype(int)

            # Clamp to frame boundaries
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(w, x2)
            y2 = min(h, y2)

            face_w = x2 - x1
            face_h = y2 - y1
            if face_w > 20 and face_h > 20:
                faces.append((x1, y1, face_w, face_h, confidence))

        return faces

    # ================================================================
    # Drawing Helpers
    # ================================================================

    @staticmethod
    def draw_faces(
        frame: np.ndarray,
        faces: List[Tuple],
        names: Optional[List[str]] = None,
        color: Tuple[int, int, int] = (0, 255, 0),
        thickness: int = 2,
    ) -> np.ndarray:
        """
        Draw bounding boxes and optional name labels on a frame.

        Parameters:
            frame: BGR image (modified in-place).
            faces: list of (x, y, w, h, confidence).
            names: optional list of labels (same length as faces).
            color: BGR color for the rectangle.
            thickness: line thickness.
        """
        for i, (x, y, w, h, conf) in enumerate(faces):
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)

            if names and i < len(names):
                label = names[i]
            else:
                label = f"Face ({conf:.0%})"

            # Draw label background
            (tw, th), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1
            )
            cv2.rectangle(
                frame, (x, y - th - 10), (x + tw + 4, y), color, cv2.FILLED
            )
            cv2.putText(
                frame, label, (x + 2, y - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA,
            )

        return frame

    # ================================================================
    # Face Extraction
    # ================================================================

    @staticmethod
    def extract_face(
        frame: np.ndarray,
        face_rect: Tuple[int, int, int, int, float],
        size: Tuple[int, int] = (200, 200),
    ) -> Optional[np.ndarray]:
        """
        Extract, convert to grayscale, and resize a face region.

        Parameters:
            frame: original BGR frame.
            face_rect: (x, y, w, h, confidence).
            size: target size for the extracted face.

        Returns:
            Grayscale face image resized to *size*, or None on error.
        """
        x, y, w, h = face_rect[:4]

        # Clamp to frame boundaries
        x = max(0, x)
        y = max(0, y)
        w = min(w, frame.shape[1] - x)
        h = min(h, frame.shape[0] - y)

        if w <= 0 or h <= 0:
            return None

        face_roi = frame[y : y + h, x : x + w]
        gray = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
        resized = cv2.resize(gray, size, interpolation=cv2.INTER_AREA)
        return resized
