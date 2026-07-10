from pathlib import Path
import socket
import sys
import tempfile
import unittest
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import app  # noqa: E402
import launcher  # noqa: E402


class DesktopPackageTests(unittest.TestCase):
    def test_build_command_never_relaunches_the_frozen_desktop_executable(self):
        command = app.build_command(
            mode="visible",
            source=Path("input.png"),
            output=Path("output.png"),
            options={"inpaint_method": "telea", "strip_metadata": False},
        )

        self.assertEqual(command[0], "visible")
        self.assertNotIn(sys.executable, command)
        self.assertIn("--inpaint-method", command)
        self.assertIn("telea", command)
        self.assertIn("--keep-metadata", command)

    def test_runtime_paths_are_writable_outside_the_installation_folder(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch.object(app, "user_data_dir", return_value=Path(temp_dir)):
                upload_dir = app.get_upload_dir()
                self.assertEqual(upload_dir, Path(temp_dir) / "uploads")
                self.assertTrue(upload_dir.exists())

    def test_xiaohongshu_profile_link_is_configurable(self):
        self.assertTrue(app.XIAOHONGSHU_URL.startswith("https://"))

    def test_homepage_is_available(self):
        response = app.app.test_client().get("/")
        self.assertEqual(response.status_code, 200)

    def test_launcher_avoids_an_occupied_port(self):
        choose_port = getattr(launcher, "choose_available_port", None)
        self.assertIsNotNone(choose_port)
        if choose_port is None:
            return
        with socket.socket() as occupied:
            occupied.bind(("127.0.0.1", 0))
            occupied.listen(1)
            occupied_port = occupied.getsockname()[1]
            selected_port = choose_port(occupied_port)
        self.assertNotEqual(selected_port, occupied_port)
        self.assertGreater(selected_port, 0)
