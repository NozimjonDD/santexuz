"""Ubuntu-only unit tests. External commands and ownership changes are mocked."""
import importlib.util
import os
from pathlib import Path
import stat
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


spec = importlib.util.spec_from_file_location("ubuntu_deployment", Path(__file__).with_name("deploy.py"))
deploy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(deploy)


class EnvironmentTests(unittest.TestCase):
    def test_values_are_literal_and_do_not_expand_shell_variables(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "production.env"
            path.write_text("# comment\nDB_PASSWORD=literal$HOME;token\nEMPTY=\n", encoding="utf-8")
            with patch.object(Path, "stat", return_value=SimpleNamespace(st_uid=0, st_mode=0o100640)):
                self.assertEqual(deploy.read_env(path), {"DB_PASSWORD": "literal$HOME;token", "EMPTY": ""})

    def test_unsafe_permissions_and_ambiguous_syntax_fail_without_echoing_secret(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "production.env"
            for mode, text in (
                (0o100644, "DB_PASSWORD=private-value\n"),
                (0o100660, "DB_PASSWORD=private-value\n"),
                (0o100640, 'DB_PASSWORD="private-value"\n'),
                (0o100640, "DB_PASSWORD=private-value\nDB_PASSWORD=other\n"),
            ):
                with self.subTest(mode=mode, syntax=text.split("=")[0]):
                    path.write_text(text, encoding="utf-8")
                    with patch.object(Path, "stat", return_value=SimpleNamespace(st_uid=0, st_mode=mode)):
                        with self.assertRaises(ValueError) as error:
                            deploy.read_env(path)
                    self.assertNotIn("private-value", str(error.exception))


class ReleaseSafetyTests(unittest.TestCase):
    def test_code_is_readable_after_secure_extraction_and_external_symlinks_are_not_followed(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            release = base / "release"
            requirements = release / "requirements"
            requirements.mkdir(parents=True, mode=0o700)
            source = requirements / "production.txt"
            source.write_text("Django\n")
            source.chmod(0o600)
            executable = release / "runner"
            executable.write_text("#!/bin/sh\n")
            executable.chmod(0o700)
            outside = base / "outside"
            outside.mkdir()
            private = outside / "secret"
            private.write_text("private")
            private.chmod(0o600)
            (release / "external").symlink_to(outside, target_is_directory=True)
            with patch.object(deploy.os, "chown") as ownership:
                deploy.seal_release(release, 123)
            self.assertEqual(stat.S_IMODE(requirements.stat().st_mode), 0o755)
            self.assertEqual(stat.S_IMODE(source.stat().st_mode), 0o644)
            self.assertEqual(stat.S_IMODE(executable.stat().st_mode), 0o755)
            self.assertEqual(stat.S_IMODE(private.stat().st_mode), 0o600)
            for call in ownership.call_args_list:
                self.assertFalse(call.kwargs["follow_symlinks"])
                self.assertNotEqual(call.args[0], private)

    def test_failed_readiness_keeps_maintenance_and_does_not_start_background_writers(self):
        with tempfile.TemporaryDirectory() as directory:
            instance = deploy.Deployment.__new__(deploy.Deployment)
            instance.name = "santex"
            instance.shared = Path(directory)
            flag = instance.shared / "maintenance.flag"
            flag.write_text("deploying")
            with patch.object(deploy, "run") as command, patch.object(instance, "probe", side_effect=RuntimeError("not ready")):
                with self.assertRaises(RuntimeError):
                    instance.resume()
            self.assertTrue(flag.exists())
            for call in command.call_args_list:
                args = call.args[0]
                if args[1] == "start":
                    self.assertNotIn("santex-notifications.timer", args)
                    self.assertNotIn("santex-deadlines.timer", args)


if __name__ == "__main__":
    unittest.main()
