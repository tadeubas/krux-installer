import os
from unittest.mock import patch, MagicMock, call
from kivy.base import EventLoop, EventLoopBase
from kivy.tests.common import GraphicUnitTest
from kivy.uix.screenmanager import ScreenManager
from src.app import KruxInstallerApp


class TestConfigKruxInstaller(GraphicUnitTest):

    @classmethod
    def teardown_class(cls):
        EventLoop.exit()

    @patch.object(EventLoopBase, "ensure_window", lambda x: None)
    @patch.dict(os.environ, {"LANG": "en-US.UTF-8"}, clear=True)
    def test_init(self):
        app = KruxInstallerApp()
        self.assertEqual(len(app.screens), 0)
        self.assertIsInstance(app.screen_manager, ScreenManager)

    @patch.object(EventLoopBase, "ensure_window", lambda x: None)
    @patch.dict(os.environ, {"LANG": "en-US.UTF-8"}, clear=True)
    def test_setup_screen_manager(self):
        mock_screen = MagicMock(name="MockScreen")

        app = KruxInstallerApp()
        app.screen_manager = MagicMock()
        app.screen_manager.add_widget = MagicMock()
        app.screens = [mock_screen]

        app.setup_screen_manager()

        # patch assertions
        app.screen_manager.add_widget.assert_has_calls(
            [
                call(mock_screen),
            ]
        )

    @patch.object(EventLoopBase, "ensure_window", lambda x: None)
    @patch.dict(os.environ, {"LANG": "en-US.UTF-8"}, clear=True)
    def test_fail_setup_screen_manager(self):
        app = KruxInstallerApp()
        with self.assertRaises(RuntimeError) as exc_info:
            app.setup_screen_manager()

        self.assertEqual(
            str(exc_info.exception), "Cannot setup screen_manager: screen list is empty"
        )

    @patch.object(EventLoopBase, "ensure_window", lambda x: None)
    @patch.dict(os.environ, {"LANG": "en-US.UTF-8"}, clear=True)
    @patch("sys.platform", "linux")
    @patch("src.app.screens.base_screen.App.get_running_app")
    def test_setup_screens(self, mock_get_running_app):
        app = KruxInstallerApp()
        app.setup_screens()

        allowed_screens = (
            "GreetingsScreen",
            "CheckPermissionsScreen",
            "MainScreen",
            "SelectDeviceScreen",
            "SelectVersionScreen",
            "SelectOldVersionScreen",
            "WarningBetaScreen",
            "AboutScreen",
            "DownloadStableZipScreen",
            "DownloadStableZipSha256Screen",
            "DownloadStableZipSigScreen",
            "DownloadSelfcustodyPemScreen",
            "VerifyStableZipScreen",
            "UnzipStableScreen",
            "DownloadBetaScreen",
            "WarningAlreadyDownloadedScreen",
            "FlashScreen",
        )
        for screen in app.screens:
            self.assertIn(screen.name, allowed_screens)

        mock_get_running_app.assert_has_calls(
            [call().config.get("locale", "lang")], any_order=True
        )

    @patch.object(EventLoopBase, "ensure_window", lambda x: None)
    @patch.dict(os.environ, {"LANG": "en-US.UTF-8"}, clear=True)
    @patch("sys.platform", "win32")
    @patch("src.app.screens.base_screen.App.get_running_app")
    def test_setup_screens_win32(self, mock_get_running_app):
        app = KruxInstallerApp()
        app.setup_screens()

        allowed_screens = (
            "GreetingsScreen",
            "MainScreen",
            "SelectDeviceScreen",
            "SelectVersionScreen",
            "SelectOldVersionScreen",
            "WarningBetaScreen",
            "AboutScreen",
            "DownloadStableZipScreen",
            "DownloadStableZipSha256Screen",
            "DownloadStableZipSigScreen",
            "DownloadSelfcustodyPemScreen",
            "VerifyStableZipScreen",
            "UnzipStableScreen",
            "DownloadBetaScreen",
            "WarningAlreadyDownloadedScreen",
            "FlashScreen",
        )
        for screen in app.screens:
            self.assertIn(screen.name, allowed_screens)

        mock_get_running_app.assert_has_calls(
            [call().config.get("locale", "lang")], any_order=True
        )

    @patch.object(EventLoopBase, "ensure_window", lambda x: None)
    @patch.dict(os.environ, {"LANG": "en-US.UTF-8"}, clear=True)
    @patch("sys.platform", "darwin")
    @patch("src.app.screens.base_screen.App.get_running_app")
    def test_setup_screens_darwin(self, mock_get_running_app):
        app = KruxInstallerApp()
        app.setup_screens()

        allowed_screens = (
            "GreetingsScreen",
            "MainScreen",
            "SelectDeviceScreen",
            "SelectVersionScreen",
            "SelectOldVersionScreen",
            "WarningBetaScreen",
            "AboutScreen",
            "DownloadStableZipScreen",
            "DownloadStableZipSha256Screen",
            "DownloadStableZipSigScreen",
            "DownloadSelfcustodyPemScreen",
            "VerifyStableZipScreen",
            "UnzipStableScreen",
            "DownloadBetaScreen",
            "WarningAlreadyDownloadedScreen",
            "FlashScreen",
        )
        for screen in app.screens:
            self.assertIn(screen.name, allowed_screens)

        mock_get_running_app.assert_has_calls(
            [call().config.get("locale", "lang")], any_order=True
        )

    @patch.object(EventLoopBase, "ensure_window", lambda x: None)
    @patch.dict(os.environ, {"LANG": "en-US.UTF-8"}, clear=True)
    @patch("src.app.KruxInstallerApp.setup_screens")
    @patch("src.app.KruxInstallerApp.setup_screen_manager")
    def test_build(self, mock_setup_screen_manager, mock_setup_screens):
        app = KruxInstallerApp()
        app.build()

        mock_setup_screens.assert_called_once()
        mock_setup_screen_manager.assert_called_once()
