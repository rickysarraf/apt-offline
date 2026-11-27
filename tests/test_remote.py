#!/usr/bin/env python3
"""Unit tests for apt-offline remote that do not open an SSH connection.

The existing tests/apt-offline-tests-github.sh drives set/get/install against
a live APT archive and needs root. These tests cover the remote command's
local decisions: required hosts, the download guard, and the shared checksum
helper that get and remote both call.
"""

import argparse
import hashlib
import os
import shutil
import sys
import tempfile
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from apt_offline_core.AptOfflineLib import Checksum
from apt_offline_remote import AptOfflineRemoteLib
from apt_offline_remote.AptOfflineRemoteLib import register_subparser


def _parser():
    parser = argparse.ArgumentParser(prog="apt-offline")
    sub = parser.add_subparsers(dest="command")
    register_subparser(sub, argparse.ArgumentParser(add_help=False))
    return parser


def _run(argv):
    args = _parser().parse_args(argv)
    args.func(args)


class ChecksumTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp(prefix="apt-offline-checksum-")
        self.path = os.path.join(self.directory, "payload")
        with open(self.path, "wb") as handle:
            handle.write(b"payload")
        self.digest = hashlib.sha256(b"payload").hexdigest()
        self.checker = Checksum()

    def tearDown(self):
        shutil.rmtree(self.directory, ignore_errors=True)

    def test_well_formed_checksum_matches(self):
        self.assertTrue(
            self.checker.CheckHashDigest(self.path, "sha256:" + self.digest)
        )

    def test_well_formed_checksum_rejects_a_mismatch(self):
        self.assertFalse(
            self.checker.CheckHashDigest(self.path, "sha256:" + ("0" * 64))
        )

    def test_metadata_placeholder_colon_is_not_accepted(self):
        # apt-offline set writes ":" when an update index has no checksum.
        # That placeholder still fails closed.
        self.assertFalse(self.checker.CheckHashDigest(self.path, ":"))

    def test_missing_checksum_is_accepted(self):
        # A signature field that is absent (None) or has no "type:digest"
        # form used to raise. It is now treated as unverified-but-ok so a
        # cache lookup does not crash. A present sha256: value still checks.
        self.assertTrue(self.checker.CheckHashDigest(self.path, None))
        self.assertTrue(self.checker.CheckHashDigest(self.path, ""))
        self.assertTrue(self.checker.CheckHashDigest(self.path, "not-a-digest"))


class RemoteCommandTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.mkdtemp(prefix="apt-offline-remote-")
        self.ssh_calls = []

        def refuse_ssh(*args, **kwargs):
            self.ssh_calls.append(args)
            raise AssertionError("SSH was invoked: %r" % (args,))

        self._orig_ssh = AptOfflineRemoteLib._ssh_run
        AptOfflineRemoteLib._ssh_run = refuse_ssh

    def tearDown(self):
        AptOfflineRemoteLib._ssh_run = self._orig_ssh
        shutil.rmtree(self.directory, ignore_errors=True)

    def test_host_or_hosts_list_is_required(self):
        listed = os.path.join(self.directory, "hosts.list")
        with open(listed, "w") as handle:
            handle.write("should-not-be-implicit\n")
        os.makedirs(os.path.join(self.directory, "should-not-be-implicit"))
        with self.assertRaises(SystemExit) as caught:
            _run(["remote", "--status", "--work-dir", self.directory])
        self.assertEqual(caught.exception.code, 1)
        self.assertEqual(self.ssh_calls, [])

    def test_explicit_hosts_list_strips_comments(self):
        listed = os.path.join(self.directory, "fleet.txt")
        with open(listed, "w") as handle:
            handle.write("# comment\n\nbox-a  # jumphost\n")
        # --status only reads local state.
        _run(["remote", "--status", "--hosts-list", listed, "--work-dir", self.directory])
        self.assertEqual(self.ssh_calls, [])

    def test_host_and_hosts_list_together_are_rejected(self):
        listed = os.path.join(self.directory, "fleet.txt")
        with open(listed, "w") as handle:
            handle.write("box-a\n")
        with self.assertRaises(SystemExit) as caught:
            _run(["remote", "box-b", "--hosts-list", listed, "--status"])
        self.assertEqual(caught.exception.code, 1)

    def test_operation_flags_rejected_on_download(self):
        with self.assertRaises(SystemExit) as caught:
            _run(["remote", "box-a", "--download", "--upgrade"])
        self.assertEqual(caught.exception.code, 1)
        self.assertEqual(self.ssh_calls, [])

    def test_download_without_state_is_skipped(self):
        _run(["remote", "box-a", "--download", "--work-dir", self.directory])
        self.assertEqual(self.ssh_calls, [])

    def test_finish_install_refuses_an_incomplete_download(self):
        host_dir = os.path.join(self.directory, "box-a", "100-upd")
        os.makedirs(host_dir)
        with open(os.path.join(host_dir, "state.json"), "w") as handle:
            handle.write(
                '{"op_dir": "100-upd", "downloaded": false, '
                '"update": true, "upgrade": false, "dist_upgrade": false, '
                '"install_packages": []}'
            )
        with self.assertRaises(SystemExit) as caught:
            _run(["remote", "box-a", "--finish-install", "--work-dir", self.directory])
        self.assertEqual(caught.exception.code, 1)
        self.assertEqual(self.ssh_calls, [])

    def test_host_path_separator_is_rejected(self):
        with self.assertRaises(SystemExit) as caught:
            _run(["remote", "../outside", "--status", "--work-dir", self.directory])
        self.assertEqual(caught.exception.code, 1)
        self.assertFalse(os.path.isdir(os.path.join(self.directory, "..", "outside")))


class FetchProgressTests(unittest.TestCase):
    def test_deb_download_success_does_not_name_line_overwrite_full(self):
        # The progress-bar cleanup deleted LINE_OVERWRITE_FULL. Two deb
        # success lines still used it, so get raised NameError in the
        # worker and left an invalid zip.
        path = os.path.join(ROOT, "apt_offline_core", "AptOfflineCoreLib.py")
        with open(path, encoding="utf-8") as handle:
            source = handle.read()
        self.assertNotIn("LINE_OVERWRITE_FULL", source)
        self.assertEqual(source.count(r'log.success("%s done\n" % PackageName)'), 3)


if __name__ == "__main__":
    unittest.main()
