import pytest
from unittest.mock import Mock, patch, call
import numpy as np
from app.core.camera import Camera, Frame
from app.utils.config import Config


@pytest.fixture
def config():
    """Fixture providing a test configuration."""
    return Config()


@pytest.fixture
def mock_camera():
    """Fixture providing a Camera instance with mocked cv2."""
    with patch("app.core.camera.cv2") as mock_cv2:
        camera = Camera(Config())

        mock_device = Mock()
        mock_cv2.VideoCapture.return_value = mock_device
        camera.device = mock_device
        yield camera, mock_cv2


class TestCamera:
    """Test suite for the Camera class."""

    def test_camera_initialization(self, config):
        """Test camera instance creation."""
        camera = Camera(config)
        assert camera.config == config
        assert camera.device is None

    def test_start_success(self, mock_camera):
        """Test successful camera start."""
        camera, mock_cv2 = mock_camera
        camera.device.isOpened.return_value = True

        assert camera.start() is True
        mock_cv2.VideoCapture.assert_called_once_with(0)
        camera.device.set.assert_called()
        assert camera.device.set.call_count == 3

    def test_start_failure(self, mock_camera):
        """Test camera start failure."""
        camera, mock_cv2 = mock_camera
        camera.device.isOpened.return_value = False

        assert camera.start() is False
        mock_cv2.VideoCapture.assert_called_once_with(0)
        camera.device.set.assert_not_called()

    def test_configure_camera(self, mock_camera):
        """Test camera configuration."""
        camera, mock_cv2 = mock_camera
        camera._configure()

        expected_calls = [
            call(mock_cv2.CAP_PROP_FRAME_WIDTH, camera.config.CAMERA_WIDTH),
            call(mock_cv2.CAP_PROP_FRAME_HEIGHT, camera.config.CAMERA_HEIGHT),
            call(mock_cv2.CAP_PROP_FPS, camera.config.CAMERA_FPS),
        ]

        assert camera.device.set.call_count == 3
        camera.device.set.assert_has_calls(expected_calls, any_order=True)

    def test_read_success(self, mock_camera):
        """Test successful frame read."""
        camera, _ = mock_camera
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        camera.device.read.return_value = (True, test_frame)

        frame = camera.read()
        assert isinstance(frame, Frame)
        assert frame.success is True
        assert np.array_equal(frame.image, test_frame)
        camera.device.read.assert_called_once()

    def test_read_failure(self, mock_camera):
        """Test frame read failure."""
        camera, _ = mock_camera
        camera.device.read.return_value = (False, None)

        frame = camera.read()
        assert isinstance(frame, Frame)
        assert frame.success is False
        assert frame.image is None
        camera.device.read.assert_called_once()

    def test_read_uninitialized(self, config):
        """Test read attempt with uninitialized camera."""
        camera = Camera(config)
        frame = camera.read()
        assert isinstance(frame, Frame)
        assert frame.success is False
        assert frame.image is None

    def test_release(self, mock_camera):
        """Test camera release."""
        camera, mock_cv2 = mock_camera
        camera.device.isOpened.return_value = True

        camera.release()
        camera.device.release.assert_called_once()
        mock_cv2.destroyAllWindows.assert_called_once()

    def test_release_not_opened(self, mock_camera):
        """Test release when camera is not opened."""
        camera, mock_cv2 = mock_camera
        camera.device.isOpened.return_value = False

        camera.release()
        camera.device.release.assert_not_called()
        mock_cv2.destroyAllWindows.assert_not_called()

    def test_context_manager(self, mock_camera):
        """Test camera cleanup on exception."""
        camera, _ = mock_camera
        camera.device.isOpened.return_value = True

        with pytest.raises(Exception):
            with camera:
                raise Exception("Test exception")

        camera.device.release.assert_called_once()

    def test_frame_dataclass(self):
        """Test Frame dataclass initialization."""
        frame = Frame(success=True, image=np.zeros((480, 640, 3)))
        assert frame.success is True
        assert isinstance(frame.image, np.ndarray)

        frame = Frame(success=False)
        assert frame.success is False
        assert frame.image is None
