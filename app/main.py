import os
import rumps
import sys
import threading
import datetime

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import asyncio
from app.utils.config import Config
from app.services.monitor import SecurityMonitor
from app.utils.logger import logger
import subprocess


def get_resource_path(relative_path):
    """Get the correct path for resources, whether running as script or frozen app."""
    if getattr(sys, "frozen", False):
        bundle_dir = os.path.dirname(sys.executable)
        resource_dir = os.path.join(bundle_dir, "..", "Resources")
        return os.path.join(resource_dir, relative_path)
    return os.path.join(os.path.dirname(__file__), relative_path)


def run_async(coro):
    """Executes a coroutine synchronously."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def get_login_item_status():
    """Check if the application is configured to start at login."""
    cmd = [
        "osascript",
        "-e",
        'tell application "System Events" to get the name of every login item',
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return "Sentry AI" in result.stdout


def toggle_login_item(enable):
    """Enable or disable the automatic startup at login."""
    if getattr(sys, "frozen", False):
        app_path = os.path.abspath(
            os.path.join(os.path.dirname(sys.executable), "../../..")
        )
        if enable:
            cmd = [
                "osascript",
                "-e",
                f'tell application "System Events" to make login item at end with properties {{path:"{app_path}", hidden:false}}',
            ]
        else:
            cmd = [
                "osascript",
                "-e",
                'tell application "System Events" to delete login item "Sentry AI"',
            ]
        subprocess.run(cmd)


class SentryApp(rumps.App):
    def __init__(self):
        print("Starting Sentry AI application...")
        icon_path = get_resource_path("app/public/assets/MenuBarIcon.icns")
        print(f"Loading icon from: {icon_path}")
        if not os.path.exists(icon_path):
            logger.error(f"Icon file not found at: {icon_path}")
            raise FileNotFoundError(f"Icon file not found: {icon_path}")

        super().__init__(
            "SentryAI", icon=icon_path, quit_button=None, template=False, title=None
        )

        logger.info("SentryApp initialized successfully")

        self.menu = [
            rumps.MenuItem(
                "Toggle Monitoring", callback=self.toggle_monitoring, key="m"
            ),
            None,
            rumps.MenuItem(
                "Launch at Login", callback=self.toggle_launch_at_login, key="l"
            ),
            None,
            rumps.MenuItem("About", callback=self.about, key=","),
            rumps.MenuItem("Quit", callback=self.quit, key="q"),
        ]

        self.monitor = None
        self.monitor_thread = None
        self._monitoring = False

        self.update_monitoring_menu()
        self.menu["Launch at Login"].state = get_login_item_status()

    def update_monitoring_menu(self):
        """Updates the menu text based on monitoring state."""
        menu_item = self.menu["Toggle Monitoring"]
        menu_item.title = "Stop Monitoring" if self._monitoring else "Start Monitoring"

    def toggle_monitoring(self, sender):
        """Toggles between starting and stopping monitoring."""
        if self._monitoring:
            self._monitoring = False
            if self.monitor:
                run_async(self.monitor.stop())
        else:
            self._monitoring = True
            self.start_monitor_thread()

        self.update_monitoring_menu()

    def start_monitor_thread(self):
        """Starts the monitor in a separate thread."""

        def run_monitor():
            run_async(self._start_monitoring())

        self.monitor_thread = threading.Thread(target=run_monitor)
        self.monitor_thread.start()

    async def _start_monitoring(self):
        """Starts monitoring with current configuration."""
        try:
            config = Config()
            self.monitor = SecurityMonitor(config)
            await self.monitor.monitor()
        except Exception as e:
            logger.error(f"❌ Error during monitoring: {e}")
            self._monitoring = False
            self.menu["Start Monitoring"].state = False
            self.menu["Stop Monitoring"].state = True

    def toggle_launch_at_login(self, sender):
        """Toggles launch at login setting."""
        sender.state = not sender.state
        toggle_login_item(sender.state)

    def about(self, _):
        version = "1.0.0"
        github_url = "https://github.com/Romain-Portanguen/sentry_ai"
        about_text = f"""Sentry AI - Security Monitoring System
Version: {version}

A powerful AI-powered security monitoring system that uses computer vision to detect and track faces, providing real-time alerts and monitoring capabilities.

Features:
• Real-time face detection
• Menu bar integration
• Automatic startup option
• Keyboard shortcuts

Shortcuts:
⌘M - Toggle Monitoring
⌘L - Toggle Launch at Login
⌘, - About
⌘Q - Quit

© {datetime.datetime.now().year} Sentry AI. All rights reserved.
{github_url}
"""
        rumps.alert(title="About Sentry AI", message=about_text, ok="OK")

    def quit(self, _):
        if self._monitoring:
            run_async(self.cleanup())
        rumps.quit_application()

    async def cleanup(self):
        """Cleans up resources before quitting."""
        if self.monitor:
            await self.monitor.stop()
        logger.info("✨ Sentry shutdown complete - Goodbye!")


def main():
    try:
        logger.info("Starting Sentry AI application...")
        app = SentryApp()
        logger.info("Initialized SentryApp, starting main loop...")
        app.run()
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise


if __name__ == "__main__":
    main()
