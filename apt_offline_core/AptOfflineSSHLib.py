import glob
import json
import os
import shlex
import shutil
import subprocess
import sys


def _run_quiet(cmd):
    result = subprocess.run(cmd, stderr=subprocess.PIPE)
    if result.returncode != 0:
        sys.stderr.buffer.write(result.stderr)
        raise subprocess.CalledProcessError(result.returncode, cmd)


def _ssh_run(host, cmd):
    remote_cmd_str = " ".join(shlex.quote(c) for c in cmd)
    _run_quiet(["ssh", "-o", "LogLevel=QUIET", host, remote_cmd_str])


def _detect_transfer_method(host):
    if shutil.which("rsync"):
        result = subprocess.run(
            ["ssh", "-o", "LogLevel=QUIET", host, "which rsync"],
            capture_output=True
        )
        if result.returncode == 0:
            return "rsync"
    return "scp"


def _transfer_get(method, host, remote_path, local_path):
    if method == "rsync":
        _run_quiet(["rsync", "-avP", "-e", "ssh -o LogLevel=QUIET", "%s:%s" % (host, remote_path), local_path])
    else:
        _run_quiet(["scp", "-o", "LogLevel=QUIET", "%s:%s" % (host, remote_path), local_path])


def _transfer_put(method, host, local_path, remote_path):
    if method == "rsync":
        _run_quiet(["rsync", "-avP", "-e", "ssh -o LogLevel=QUIET", local_path, "%s:%s" % (host, remote_path)])
    else:
        _run_quiet(["scp", "-o", "LogLevel=QUIET", local_path, "%s:%s" % (host, remote_path)])


def _latest_state(work_dir):
    state_files = glob.glob(os.path.join(work_dir, "*/state.json"))
    if not state_files:
        raise FileNotFoundError("no state files found in %s — run --fetch first" % work_dir)
    state_files = sorted(state_files)
    with open(state_files[-1]) as f:
        return json.load(f)
