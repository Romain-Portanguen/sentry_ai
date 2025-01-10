import asyncio
import time
from app.core.camera import Camera
from app.core.face_detector import FaceDetector
from app.core.system import SystemController
from app.utils.config import Config
from app.utils.logger import logger

class SecurityMonitor:
    """Main security monitoring service that coordinates camera, face detection, and system control.

    This class orchestrates the security monitoring process by:
    - Managing the camera feed and face detection
    - Monitoring system state (sleep, lock, user activity)
    - Handling security actions (screen locking, surveillance pausing)
    - Coordinating the interaction between all components

    Attributes:
        config (Config): Application configuration
        camera (Camera): Camera management instance
        detector (FaceDetector): Face detection service
        system (SystemController): System state controller
        absence_timer (int): Counter for frames without face detection
        frame_count (int): Total processed frames counter
        running (bool): Monitor's operational state flag
    """

    def __init__(self, config: Config):
        """Initialize the security monitor with required components.

        Args:
            config (Config): Application configuration object
        """
        self.config = config
        self.camera = Camera(config)
        self.detector = FaceDetector(config)
        self.system = SystemController()
        self.absence_timer = 0
        self.frame_count = 0
        self.running = True

    async def stop(self):
        """Stop the monitor gracefully and cleanup resources."""
        logger.info("🛑 Initiating graceful shutdown...")
        self.running = False
        self.camera.release()

    async def monitor(self):
        """Main monitoring loop that coordinates security operations.

        This method implements the core security monitoring logic:
        1. Checks system state (lock, sleep, activity)
        2. Manages camera operations
        3. Processes frames for face detection
        4. Triggers security actions when needed
        """
        while self.running:
            if self.system.is_screen_locked():
                await self._wait_for_unlock()
                if not self.running:
                    break
                continue

            if not self.camera.start():
                logger.error("🔄 Camera initialization failed, retrying in 5 seconds...")
                await asyncio.sleep(5)
                if not self.running:
                    break
                continue

            logger.info("👀 Sentry active - Monitoring for presence...")
            
            try:
                while self.running:
                    if self.system.is_sleep_mode():
                        await self._handle_sleep_mode()
                        break

                    frame = self.camera.read()
                    if not frame.success:
                        break

                    self.frame_count += 1
                    if self.frame_count % self.config.FRAME_SKIP != 0:
                        continue

                    if self.detector.detect(frame.image):
                        self.absence_timer = 0
                    else:
                        self.absence_timer += 1
                        if self.absence_timer >= self.config.ABSENCE_THRESHOLD:
                            await self._handle_absence()
                            break

                    if self.system.is_user_inactive():
                        logger.info("💤 User inactivity detected - Engaging security measures...")
                        self.camera.release()
                        self.system.lock_screen()
                        while self.running and self.system.is_user_inactive():
                            await asyncio.sleep(1)
                        break

                    await asyncio.sleep(self.config.CHECK_INTERVAL)

            finally:
                self.camera.release()

    async def _handle_sleep_mode(self):
        """Handle system sleep mode transitions.

        Manages the monitor's behavior when the system enters or exits sleep mode,
        ensuring proper resource management and state transitions.
        """
        logger.info("💤 System entering sleep mode - Pausing operations...")
        self.camera.release()
        
        while self.running and self.system.is_sleep_mode():
            await asyncio.sleep(1)
        
        logger.info("⚡ System resumed from sleep - Reactivating surveillance...")

    async def _handle_absence(self):
        """Handle user absence detection.

        Implements security measures when user absence is detected,
        including screen locking and resource cleanup.
        """
        logger.info("🚨 Extended absence detected - Engaging security protocol...")
        self.camera.release()
        self.system.lock_screen()

    async def _wait_for_unlock(self):
        """Wait for system unlock event.

        Monitors the system lock state and manages the transition
        back to active surveillance when the system is unlocked.
        """
        logger.info("🔒 System locked - Awaiting unlock event...")
        while self.running and self.system.is_screen_locked():
            await asyncio.sleep(1)
        logger.info("🔓 System unlocked - Resuming surveillance...")
