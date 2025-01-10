import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

import asyncio
import signal
from app.utils.config import Config
from app.services.monitor import SecurityMonitor
from app.utils.logger import logger


async def main():
    """Initialize and run the Sentry security monitoring system.

    This is the main entry point for the Sentry application. It:
    1. Initializes the security monitor with configuration
    2. Sets up signal handlers for graceful shutdown
    3. Manages the main application lifecycle
    4. Handles cleanup on exit

    The application will continue running until interrupted by a signal
    or an unhandled exception occurs.
    """
    logger.info("🚀 Initializing Sentry Security System...")
    config = Config()
    monitor = SecurityMonitor(config)

    def signal_handler():
        """Handle interrupt signals for graceful shutdown.

        This handler ensures that all resources are properly released
        and the application shuts down cleanly when interrupted.
        """
        logger.info("\n🛑 Interrupt received - Initiating graceful shutdown...")
        asyncio.create_task(monitor.stop())

    loop = asyncio.get_event_loop()
    loop.add_signal_handler(signal.SIGINT, signal_handler)

    try:
        await monitor.monitor()
    except Exception as e:
        logger.error(f"❌ Critical error encountered: {e}")
    finally:
        await monitor.stop()
        logger.info("✨ Sentry shutdown complete - Goodbye!")


if __name__ == "__main__":
    asyncio.run(main())
