import pytest
from unittest.mock import Mock, patch, AsyncMock
import asyncio
from app.main import main


@pytest.fixture
def mock_monitor():
    with patch("app.main.SecurityMonitor") as mock:
        monitor_instance = AsyncMock()
        mock.return_value = monitor_instance
        yield monitor_instance


@pytest.fixture
def mock_config():
    with patch("app.main.Config") as mock:
        config_instance = Mock()
        mock.return_value = config_instance
        yield config_instance


@pytest.fixture
def mock_logger():
    with patch("app.main.logger") as mock:
        yield mock


class TestMain:
    @pytest.mark.asyncio
    async def test_main_normal_execution(self, mock_monitor, mock_config, mock_logger):
        """Test normal execution of main function."""

        def trigger_interrupt():
            loop = asyncio.get_event_loop()
            for handler in loop._signal_handlers.values():
                handler()

        mock_monitor.monitor.side_effect = lambda: asyncio.get_event_loop().call_later(
            0.1, trigger_interrupt
        )

        await main()

        mock_monitor.monitor.assert_called_once()
        mock_monitor.stop.assert_called()
        assert mock_logger.info.call_count >= 2

    @pytest.mark.asyncio
    async def test_main_monitor_exception(self, mock_monitor, mock_config, mock_logger):
        """Test main function when monitor raises an exception."""
        test_error = Exception("Test error")
        mock_monitor.monitor.side_effect = test_error

        await main()

        mock_monitor.monitor.assert_called_once()
        mock_monitor.stop.assert_called_once()
        mock_logger.error.assert_called_once()
        assert str(test_error) in str(mock_logger.error.call_args)

    @pytest.mark.asyncio
    async def test_main_cleanup_on_keyboard_interrupt(
        self, mock_monitor, mock_config, mock_logger
    ):
        """Test cleanup when keyboard interrupt is received."""

        def trigger_interrupt():
            loop = asyncio.get_event_loop()
            for handler in loop._signal_handlers.values():
                handler()

        mock_monitor.monitor.side_effect = lambda: asyncio.get_event_loop().call_later(
            0.1, trigger_interrupt
        )

        await main()

        mock_monitor.stop.assert_called_once()
        assert "shutdown complete" in str(mock_logger.info.call_args_list).lower()
