import pytest
import cv2
import numpy as np
from unittest.mock import patch, MagicMock
from threading import Timer

from sentry import (
    detect_face,
    is_screen_locked,
    is_user_inactive,
    is_sleep_mode,
    ResourceManager,
    start_camera,
    lock_screen,
    wait_for_unlock,
    main,
)

# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def sample_frame():
    """Create a sample frame with a face-like pattern."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    cv2.circle(frame, (320, 240), 100, (255, 255, 255), -1)
    return frame


@pytest.fixture
def resource_manager():
    """Create a ResourceManager instance."""
    return ResourceManager()


@pytest.fixture
def mock_camera():
    """Create a mock camera with basic configuration for testing."""
    camera = MagicMock()
    camera.isOpened.return_value = True
    camera.read.return_value = (True, np.zeros((480, 640, 3)))
    return camera


# ============================================================================
# Face Detection Tests
# ============================================================================


def test_detect_face_with_face(sample_frame):
    """Test face detection with a frame containing a face."""
    result = detect_face(sample_frame)
    assert isinstance(result, bool)


def test_detect_face_without_face():
    """Test face detection with an empty frame."""
    empty_frame = np.zeros((480, 640, 3), dtype=np.uint8)
    result = detect_face(empty_frame)
    assert result is False


@patch("cv2.resize")
@patch("cv2.cvtColor")
def test_detect_face_processing(mock_cvtColor, mock_resize):
    """Test the image processing pipeline for face detection."""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    mock_resize.return_value = frame
    mock_cvtColor.return_value = frame
    detect_face(frame)
    mock_resize.assert_called_once()
    mock_cvtColor.assert_called_once()


# ============================================================================
# System State Tests
# ============================================================================


@patch("Quartz.CGSessionCopyCurrentDictionary")
def test_is_screen_locked(mock_quartz):
    """Test screen lock state detection with various scenarios."""
    mock_quartz.return_value = {"CGSSessionScreenIsLocked": True}
    assert is_screen_locked() is True

    mock_quartz.return_value = {"CGSSessionScreenIsLocked": False}
    assert is_screen_locked() is False

    mock_quartz.return_value = None
    assert is_screen_locked() is False


@patch("os.popen")
def test_is_user_inactive(mock_popen):
    """Test user inactivity detection based on system idle time."""
    mock_popen.return_value.read.return_value = "50000000000"
    assert is_user_inactive() is True

    mock_popen.return_value.read.return_value = "1000000000"
    assert is_user_inactive() is False


@patch("os.popen")
def test_is_sleep_mode(mock_popen):
    """Test sleep mode detection."""
    mock_popen.return_value.read.return_value = "Entering Sleep"
    assert is_sleep_mode() is True

    mock_popen.return_value.read.return_value = ""
    assert is_sleep_mode() is False


# ============================================================================
# Camera Management Tests
# ============================================================================


@patch("cv2.VideoCapture")
def test_start_camera_success(mock_video_capture, mock_camera):
    """Test successful camera initialization."""
    mock_video_capture.return_value = mock_camera
    cap = start_camera()
    assert cap.isOpened()


@patch("cv2.VideoCapture")
def test_start_camera_failure(mock_video_capture):
    """Test camera initialization failure."""
    mock_camera = MagicMock()
    mock_camera.isOpened.return_value = False
    mock_video_capture.return_value = mock_camera

    with pytest.raises(SystemExit):
        start_camera()


# ============================================================================
# Resource Manager Tests
# ============================================================================


def test_resource_manager_init():
    """Test ResourceManager initialization."""
    manager = ResourceManager()
    assert manager.inactive_timer is None
    assert manager.camera_active is True


def test_resource_manager_camera_lifecycle(resource_manager, mock_camera):
    """Test the complete lifecycle of camera management in ResourceManager."""
    resource_manager.shutdown_camera(mock_camera)
    mock_camera.release.assert_called_once()


def test_resource_manager_schedule_shutdown(resource_manager, mock_camera):
    """Test camera shutdown scheduling."""
    resource_manager.schedule_camera_shutdown(mock_camera)
    assert not resource_manager.camera_active
    mock_camera.release.assert_called_once()


def test_resource_manager_restart_camera(resource_manager):
    """Test camera restart."""
    resource_manager.camera_active = False

    with patch("cv2.VideoCapture") as mock_capture:
        mock_camera = MagicMock()
        mock_camera.isOpened.return_value = True
        mock_capture.return_value = mock_camera

        cap = resource_manager.restart_camera()
        assert resource_manager.camera_active
        assert cap.isOpened()


def test_resource_manager_cleanup():
    """Test resource cleanup."""
    manager = ResourceManager()
    manager.inactive_timer = Timer(1.0, lambda: None)
    manager.cleanup()
    assert not manager.inactive_timer.is_alive()


# ============================================================================
# System Control Tests
# ============================================================================


@patch("os.system")
def test_lock_screen(mock_system):
    """Test screen locking function."""
    assert lock_screen() is True
    mock_system.assert_called_once()


@patch("time.sleep")
def test_wait_for_unlock(mock_sleep, mock_camera):
    """Test wait for unlock function."""
    with patch("sentry.is_screen_locked") as mock_locked:
        mock_locked.side_effect = [True, True, False]
        assert wait_for_unlock(mock_camera) is True
        mock_camera.release.assert_called_once()


# ============================================================================
# Main Loop Tests
# ============================================================================


@patch("cv2.VideoCapture")
@patch("sentry.detect_face")
@patch("sentry.is_sleep_mode")
@patch("sentry.is_user_inactive")
def test_main_loop(mock_inactive, mock_sleep, mock_detect, mock_capture, mock_camera):
    """Test the main application loop."""
    mock_capture.return_value = mock_camera
    mock_sleep.return_value = False
    mock_inactive.return_value = False
    mock_detect.side_effect = [True, False, False, False]

    with patch("time.time", return_value=0), patch("time.sleep"), patch(
        "sentry.lock_screen", return_value=True
    ):
        try:
            main()
        except KeyboardInterrupt:
            pass


@patch("cv2.VideoCapture")
def test_main_cleanup_on_exit(mock_capture, mock_camera):
    """Test proper resource cleanup when main loop exits with KeyboardInterrupt."""
    mock_capture.return_value = mock_camera

    with patch("time.sleep"), patch(
        "sentry.is_sleep_mode", side_effect=KeyboardInterrupt
    ), patch("cv2.destroyAllWindows"):
        try:
            main()
        except KeyboardInterrupt:
            assert mock_camera.release.called
