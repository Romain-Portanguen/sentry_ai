from unittest.mock import patch, Mock
from app.core.system import SystemController


class TestSystemController:
    """Test suite for the SystemController class."""

    @patch("app.core.system.os")
    def test_lock_screen(self, mock_os):
        """Test screen locking functionality."""
        mock_os.system.return_value = 0

        result = SystemController.lock_screen()

        assert result is True
        mock_os.system.assert_called_once()
        assert "keystroke" in mock_os.system.call_args[0][0]
        assert "control down, command down" in mock_os.system.call_args[0][0]

    @patch("app.core.system.os")
    def test_is_sleep_mode_true(self, mock_os):
        """Test sleep mode detection when system is sleeping."""
        mock_os.popen.return_value.read.return_value = "Now sleeping"

        assert SystemController.is_sleep_mode() is True
        mock_os.popen.assert_called_once_with("pmset -g ps")

    @patch("app.core.system.os")
    def test_is_sleep_mode_false(self, mock_os):
        """Test sleep mode detection when system is awake."""
        mock_os.popen.return_value.read.return_value = "AC Power"

        assert SystemController.is_sleep_mode() is False
        mock_os.popen.assert_called_once_with("pmset -g ps")

    @patch("app.core.system.os")
    def test_is_sleep_mode_error(self, mock_os):
        """Test sleep mode detection when error occurs."""
        mock_os.popen.side_effect = Exception("Test error")

        assert SystemController.is_sleep_mode() is False
        mock_os.popen.assert_called_once_with("pmset -g ps")

    @patch("app.core.system.Quartz")
    def test_is_screen_locked_true(self, mock_quartz):
        """Test screen lock detection when screen is locked."""
        mock_dict = {"CGSSessionScreenIsLocked": True}
        mock_quartz.CGSessionCopyCurrentDictionary.return_value = mock_dict

        assert SystemController.is_screen_locked() is True
        mock_quartz.CGSessionCopyCurrentDictionary.assert_called_once()

    @patch("app.core.system.Quartz")
    def test_is_screen_locked_false(self, mock_quartz):
        """Test screen lock detection when screen is unlocked."""
        mock_dict = {"CGSSessionScreenIsLocked": False}
        mock_quartz.CGSessionCopyCurrentDictionary.return_value = mock_dict

        assert SystemController.is_screen_locked() is False
        mock_quartz.CGSessionCopyCurrentDictionary.assert_called_once()

    @patch("app.core.system.Quartz")
    def test_is_screen_locked_no_dict(self, mock_quartz):
        """Test screen lock detection when no dictionary is returned."""
        mock_quartz.CGSessionCopyCurrentDictionary.return_value = None

        assert SystemController.is_screen_locked() is False
        mock_quartz.CGSessionCopyCurrentDictionary.assert_called_once()

    @patch("app.core.system.Quartz")
    def test_is_screen_locked_error(self, mock_quartz):
        """Test screen lock detection when error occurs."""
        mock_quartz.CGSessionCopyCurrentDictionary.side_effect = Exception("Test error")

        assert SystemController.is_screen_locked() is False
        mock_quartz.CGSessionCopyCurrentDictionary.assert_called_once()

    @patch("app.core.system.os")
    def test_is_user_inactive_true(self, mock_os):
        """Test user inactivity detection when user is inactive."""
        mock_os.popen.return_value.read.return_value = "31000000000"

        assert SystemController.is_user_inactive() is True
        mock_os.popen.assert_called_once_with("ioreg -c IOHIDSystem | grep HIDIdleTime")

    @patch("app.core.system.os")
    def test_is_user_inactive_false(self, mock_os):
        """Test user inactivity detection when user is active."""
        mock_os.popen.return_value.read.return_value = "1000000000"

        assert SystemController.is_user_inactive() is False
        mock_os.popen.assert_called_once_with("ioreg -c IOHIDSystem | grep HIDIdleTime")

    @patch("app.core.system.os")
    def test_is_user_inactive_error(self, mock_os):
        """Test user inactivity detection when error occurs."""
        mock_os.popen.side_effect = Exception("Test error")

        assert SystemController.is_user_inactive() is False
        mock_os.popen.assert_called_once_with("ioreg -c IOHIDSystem | grep HIDIdleTime")
