from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import app  # noqa: E402


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
