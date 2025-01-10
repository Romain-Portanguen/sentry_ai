import pytest
from unittest.mock import Mock, patch
import numpy as np
from app.core.face_detector import FaceDetector
from app.utils.config import Config


@pytest.fixture
def config():
    """Fixture providing a test configuration."""
    return Config()


@pytest.fixture
def mock_detector():
    """Fixture providing a FaceDetector instance with mocked mediapipe."""
    with patch("app.core.face_detector.mp") as mock_mp:
        detector = FaceDetector(Config())
        yield detector, mock_mp


class TestFaceDetector:
    """Test suite for the FaceDetector class."""

    def test_detector_initialization(self, mock_detector, config):
        """Test face detector instance creation."""
        detector, mock_mp = mock_detector
        mock_mp.solutions.face_detection.FaceDetection.assert_called_once_with(
            min_detection_confidence=config.FACE_CONFIDENCE,
            model_selection=config.MODEL_SELECTION,
        )

    @patch("app.core.face_detector.cv2")
    def test_detect_face_present(self, mock_cv2, mock_detector):
        """Test face detection when a face is present."""
        detector, _ = mock_detector
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cv2.resize.return_value = test_frame
        mock_cv2.cvtColor.return_value = test_frame

        mock_detections = Mock()
        mock_detections.detections = [Mock()]
        detector.detector.process.return_value = mock_detections

        assert detector.detect(test_frame) is True
        mock_cv2.resize.assert_called_once()
        mock_cv2.cvtColor.assert_called_once()
        detector.detector.process.assert_called_once()

    @patch("app.core.face_detector.cv2")
    def test_detect_no_face(self, mock_cv2, mock_detector):
        """Test face detection when no face is present."""
        detector, _ = mock_detector
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cv2.resize.return_value = test_frame
        mock_cv2.cvtColor.return_value = test_frame

        mock_detections = Mock()
        mock_detections.detections = None
        detector.detector.process.return_value = mock_detections

        assert detector.detect(test_frame) is False
        mock_cv2.resize.assert_called_once()
        mock_cv2.cvtColor.assert_called_once()
        detector.detector.process.assert_called_once()

    @patch("app.core.face_detector.cv2")
    def test_detect_empty_detections(self, mock_cv2, mock_detector):
        """Test face detection with empty detections list."""
        detector, _ = mock_detector
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        mock_cv2.resize.return_value = test_frame
        mock_cv2.cvtColor.return_value = test_frame

        mock_detections = Mock()
        mock_detections.detections = []
        detector.detector.process.return_value = mock_detections

        assert detector.detect(test_frame) is False
        mock_cv2.resize.assert_called_once()
        mock_cv2.cvtColor.assert_called_once()
        detector.detector.process.assert_called_once()

    @patch("app.core.face_detector.cv2")
    def test_detect_image_preprocessing(self, mock_cv2, mock_detector):
        """Test image preprocessing in face detection."""
        detector, _ = mock_detector

        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)

        mock_cv2.resize.return_value = test_frame
        mock_cv2.cvtColor.return_value = test_frame
        mock_cv2.COLOR_BGR2RGB = 4

        mock_detections = Mock()
        mock_detections.detections = [Mock()]
        detector.detector.process.return_value = mock_detections

        detector.detect(test_frame)

        mock_cv2.resize.assert_called_once_with(test_frame, (0, 0), fx=0.5, fy=0.5)
        mock_cv2.cvtColor.assert_called_once_with(test_frame, mock_cv2.COLOR_BGR2RGB)

        mock_cv2.cvtColor.assert_called_once_with(test_frame, mock_cv2.COLOR_BGR2RGB)
