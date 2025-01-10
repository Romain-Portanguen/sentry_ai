import os
import Quartz
from app.utils.logger import logger


class SystemController:
    """Controls and monitors system state and security actions.

    This class provides an interface for:
    - Monitoring system states (sleep, lock, user activity)
    - Controlling system security actions (screen locking)
    - Interfacing with macOS system APIs

    It uses PyObjC bindings and system commands to interact with macOS,
    providing a reliable way to monitor and control system security states.
    """

    @staticmethod
    def lock_screen():
        """Lock the user session using macOS security features.

        Simulates the standard macOS lock screen shortcut (Control + Command + Q)
        using AppleScript. This provides a secure way to lock the system when
        security conditions are met.

        Returns:
            bool: True if the lock command was executed successfully
        """
        logger.info("🔐 Initiating system lock sequence...")
        applescript = """
        tell application "System Events" to keystroke "q" using {control down, command down}
        """
        os.system(f"osascript -e '{applescript}'")
        logger.info("🔒 System lock engaged successfully")
        return True

    @staticmethod
    def is_sleep_mode():
        """Check if the system is in sleep mode.

        Queries the system power management status using pmset to determine
        if the system is currently in or transitioning to sleep mode.

        Returns:
            bool: True if system is in sleep mode, False otherwise
        """
        try:
            power_status = os.popen("pmset -g ps").read()
            is_sleeping = (
                "sleep" in power_status.lower() or "sleeping" in power_status.lower()
            )
            if is_sleeping:
                logger.debug("💤 System sleep state detected")
            return is_sleeping
        except Exception as e:
            logger.error(f"⚠️ Failed to check sleep state: {e}")
            return False

    @staticmethod
    def is_screen_locked():
        """Check if the screen is currently locked.

        Uses the Quartz framework to query the current session state
        and determine if the screen is locked.

        Returns:
            bool: True if screen is locked, False otherwise
        """
        try:
            current_dict = Quartz.CGSessionCopyCurrentDictionary()
            if current_dict:
                is_locked = current_dict.get("CGSSessionScreenIsLocked", False)
                if is_locked:
                    logger.debug("🔒 Screen lock state detected")
                return is_locked
            return False
        except Exception as e:
            logger.error(f"⚠️ Failed to check screen lock state: {e}")
            return False

    @staticmethod
    def is_user_inactive():
        """Check if the user is currently inactive.

        Monitors system idle time using IOKit's HIDIdleTime.
        User is considered inactive after the configured threshold
        (default: 30 seconds).

        Returns:
            bool: True if user is inactive, False otherwise
        """
        try:
            idle_time = int(
                os.popen("ioreg -c IOHIDSystem | grep HIDIdleTime").read().split()[-1]
            )
            is_inactive = idle_time > 30_000_000_000  # 30 seconds
            if is_inactive:
                logger.debug("💤 User inactivity detected")
            return is_inactive
        except Exception as e:
            logger.error(f"⚠️ Failed to check user activity state: {e}")
            return False
