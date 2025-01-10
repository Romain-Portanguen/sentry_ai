import pytest
import pytest_asyncio
from unittest.mock import Mock, patch
import numpy as np
import asyncio
from app.services.monitor import SecurityMonitor
from app.utils.config import Config
from typing import AsyncGenerator


@pytest.fixture
def config():
    """Fixture providing a test configuration."""
    return Config()


@pytest.fixture
def mock_dependencies():
    """Fixture providing mocked dependencies for SecurityMonitor."""
    with patch("app.services.monitor.Camera") as mock_camera, patch(
        "app.services.monitor.FaceDetector"
    ) as mock_detector, patch("app.services.monitor.SystemController") as mock_system:

        mock_camera_instance = Mock()
        mock_detector_instance = Mock()
        mock_system_instance = Mock()

        mock_camera.return_value = mock_camera_instance
        mock_detector.return_value = mock_detector_instance
        mock_system.return_value = mock_system_instance

        yield {
            "camera": mock_camera_instance,
            "detector": mock_detector_instance,
            "system": mock_system_instance,
            "camera_class": mock_camera,
            "detector_class": mock_detector,
            "system_class": mock_system,
        }


@pytest.fixture
async def monitor(mock_dependencies):
    """Fixture providing a SecurityMonitor instance."""
    monitor = SecurityMonitor(Config())
    yield monitor
    await monitor.stop()


class TestSecurityMonitor:
    """Test suite for the SecurityMonitor class."""

    def test_initialization(self, config, mock_dependencies):
        """Test monitor initialization."""
        monitor = SecurityMonitor(config)
        assert monitor.config == config
        assert monitor.absence_timer == 0
        assert monitor.frame_count == 0
        assert monitor.running is True

    @pytest.mark.asyncio
    async def test_stop(self, monitor, mock_dependencies):
        """Test monitor stop functionality."""
        await monitor.stop()
        assert monitor.running is False
        mock_dependencies["camera"].release.assert_called_once()

    @pytest.mark.asyncio
    async def test_monitor_screen_locked(self, monitor, mock_dependencies):
        """Test monitoring behavior when screen is locked."""
        mock_dependencies["system"].is_screen_locked.return_value = True

        async def stop_after_delay():
            await asyncio.sleep(0.1)
            monitor.running = False

        task = asyncio.create_task(stop_after_delay())
        try:
            await asyncio.wait_for(monitor.monitor(), timeout=1.0)
        except asyncio.TimeoutError:
            monitor.running = False
        finally:
            await task

        mock_dependencies["system"].is_screen_locked.assert_called()

    @pytest.mark.asyncio
    async def test_monitor_camera_failure(self, monitor, mock_dependencies):
        """Test monitoring behavior when camera fails to start."""
        mock_dependencies["system"].is_screen_locked.return_value = False
        mock_dependencies["camera"].start.return_value = False

        async def stop_after_delay():
            await asyncio.sleep(0.1)
            monitor.running = False

        task = asyncio.create_task(stop_after_delay())
        try:
            await asyncio.wait_for(monitor.monitor(), timeout=1.0)
        except asyncio.TimeoutError:
            monitor.running = False
        finally:
            await task

        mock_dependencies["camera"].start.assert_called()

    @pytest.mark.asyncio
    async def test_monitor_face_detection(self, monitor, mock_dependencies):
        """Test face detection during monitoring."""
        mock_dependencies["system"].is_screen_locked.return_value = False
        mock_dependencies["camera"].start.return_value = True
        mock_dependencies["system"].is_sleep_mode.return_value = False

        mock_frame = Mock()
        mock_frame.success = True
        mock_frame.image = np.zeros((480, 640, 3))
        mock_dependencies["camera"].read.return_value = mock_frame

        mock_dependencies["detector"].detect.return_value = True

        async def stop_after_delay():
            await asyncio.sleep(0.1)
            monitor.running = False

        task = asyncio.create_task(stop_after_delay())
        try:
            await asyncio.wait_for(monitor.monitor(), timeout=1.0)
        except asyncio.TimeoutError:
            monitor.running = False
        finally:
            await task

        mock_dependencies["detector"].detect.assert_called()
        assert monitor.absence_timer == 0

    @pytest.mark.asyncio
    async def test_monitor_absence_detection(self, monitor, mock_dependencies):
        """Test absence detection during monitoring."""
        mock_dependencies["system"].is_screen_locked.return_value = False
        mock_dependencies["camera"].start.return_value = True
        mock_dependencies["system"].is_sleep_mode.return_value = False
        mock_dependencies["system"].is_user_inactive.return_value = False

        mock_frame = Mock()
        mock_frame.success = True
        mock_frame.image = np.zeros((480, 640, 3))
        mock_dependencies["camera"].read.return_value = mock_frame

        detections = [True] + [False] * 18

        def detect_side_effect(*args, **kwargs):
            return detections.pop(0) if detections else True

        mock_dependencies["detector"].detect.side_effect = detect_side_effect

        async def monitor_task():
            await monitor.monitor()

        async def check_lock_screen():
            start_time = asyncio.get_event_loop().time()
            while not mock_dependencies["system"].lock_screen.called:
                if asyncio.get_event_loop().time() - start_time > 2.0:
                    break
                await asyncio.sleep(0.1)
            monitor.running = False

        await asyncio.gather(monitor_task(), check_lock_screen())

        mock_dependencies["system"].lock_screen.assert_called_once()
        mock_dependencies["camera"].release.assert_called()

    @pytest.mark.asyncio
    async def test_monitor_sleep_mode(self, monitor, mock_dependencies):
        """Test monitoring behavior during sleep mode."""
        mock_dependencies["system"].is_screen_locked.return_value = False
        mock_dependencies["camera"].start.return_value = True
        mock_dependencies["system"].is_sleep_mode.return_value = True

        async def stop_after_delay():
            await asyncio.sleep(0.1)
            monitor.running = False

        task = asyncio.create_task(stop_after_delay())
        try:
            await asyncio.wait_for(monitor.monitor(), timeout=1.0)
        except asyncio.TimeoutError:
            monitor.running = False
        finally:
            await task

        mock_dependencies["camera"].release.assert_called()

    @pytest.mark.asyncio
    async def test_monitor_user_inactivity(self, monitor, mock_dependencies):
        """Test monitoring behavior during user inactivity."""
        mock_dependencies["system"].is_screen_locked.return_value = False
        mock_dependencies["camera"].start.return_value = True
        mock_dependencies["system"].is_sleep_mode.return_value = False
        mock_dependencies["system"].is_user_inactive.return_value = True

        mock_frame = Mock()
        mock_frame.success = True
        mock_frame.image = np.zeros((480, 640, 3))
        mock_dependencies["camera"].read.return_value = mock_frame

        async def stop_after_delay():
            await asyncio.sleep(0.1)
            monitor.running = False

        task = asyncio.create_task(stop_after_delay())
        try:
            await asyncio.wait_for(monitor.monitor(), timeout=1.0)
        except asyncio.TimeoutError:
            monitor.running = False
        finally:
            await task

        mock_dependencies["system"].lock_screen.assert_called()
        mock_dependencies["camera"].release.assert_called()
