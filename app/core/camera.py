from dataclasses import dataclass
import cv2
import numpy as np
from app.utils.config import Config
from app.utils.logger import logger


@dataclass
class Frame:
    """Represents a single frame captured from the camera.

    Attributes:
        success (bool): Whether the frame was successfully captured
        image (np.ndarray): The actual image data, None if capture failed
    """

    success: bool
    image: np.ndarray = None


class Camera:
    """Manages camera operations including initialization, capture, and cleanup.

    This class handles all camera-related operations, including device initialization,
    frame capture, and proper resource cleanup. It uses OpenCV for camera operations
    and supports configuration of camera parameters.

    Attributes:
        config (Config): Configuration object containing camera settings
        device (cv2.VideoCapture): OpenCV video capture device
    """

    def __init__(self, config: Config):
        """Initialize the camera manager.

        Args:
            config (Config): Configuration object containing camera settings
        """
        self.config = config
        self.device = None

    def __enter__(self):
        """Context manager entry.

        Returns:
            Camera: self for context manager usage
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit.

        Ensures camera resources are properly released when exiting context.

        Args:
            exc_type: Exception type if an error occurred
            exc_val: Exception value if an error occurred
            exc_tb: Exception traceback if an error occurred
        """
        self.release()

    def start(self) -> bool:
        """Initialize and configure the camera device.

        Attempts to open the default camera (index 0) and configure it with
        the settings specified in the config. If the camera is in use by
        another application or lacks proper permissions, initialization will fail.

        Returns:
            bool: True if camera was successfully initialized, False otherwise
        """
        self.device = cv2.VideoCapture(0)
        if not self.device.isOpened():
            logger.error("⚠️ Camera access failed - Please verify:")
            logger.error("  • Camera permissions in System Settings")
            logger.error("  • No other application is using the camera")
            logger.error("  • Camera is properly connected and functional")
            return False

        self._configure()
        logger.info("📸 Camera initialized successfully")
        return True

    def _configure(self):
        """Configure camera properties according to settings.

        Sets resolution and frame rate according to the configuration.
        These settings affect the quality and performance of the capture.
        """
        self.device.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.CAMERA_WIDTH)
        self.device.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.CAMERA_HEIGHT)
        self.device.set(cv2.CAP_PROP_FPS, self.config.CAMERA_FPS)

    def read(self) -> Frame:
        """Capture a single frame from the camera.

        Returns:
            Frame: A Frame object containing the capture status and image data
        """
        if not self.device or not self.device.isOpened():
            logger.warning("⚠️ Attempted to read from uninitialized camera")
            return Frame(success=False)
        success, image = self.device.read()
        if not success:
            logger.warning("⚠️ Failed to capture frame from camera")
        return Frame(success=success, image=image)

    def release(self):
        """Release camera resources and cleanup.

        This method should be called when the camera is no longer needed
        to ensure proper resource cleanup and allow other applications
        to access the camera.
        """
        if self.device and self.device.isOpened():
            self.device.release()
            cv2.destroyAllWindows()
            logger.info("📸 Camera resources released")
