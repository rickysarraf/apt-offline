import argparse
import datetime
import glob
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

from apt_offline_core.AptOfflineCoreLib import fetcher
from apt_offline_core.AptOfflineSSHLib import (
    _detect_transfer_method,
    _latest_state,
    _ssh_run,
    _transfer_get,
    _transfer_put,
)

_REMOTE_CACHE = ".cache/apt-offline-remote"
_OP_LABELS = {"upd": "update", "upg": "upgrade", "dup": "dist-upgrade", "ipk": "install-pkgs"}
_GREEN = "\033[32m"
_RED = "\033[31m"
_DIM = "\033[2m"
_RESET = "\033[0m"


def _phase_str(label, done, use_color):
    tick = (_GREEN + "✓" + _RESET) if (done and use_color) else ("✓" if done else (_DIM + "✗" + _RESET) if use_color else "✗")
    return "  %s %s" % (label, tick)


def _show_status(host, work_dir, log):
    use_color = sys.stdout.isatty()
    op_dirs = sorted(
        [d for d in glob.glob(os.path.join(work_dir, "*-*")) if os.path.isdir(d)]
    )
    if not op_dirs:
        log.msg("  (no runs)\n")
        return
    for op_dir in op_dirs:
        run_name = os.path.basename(op_dir)
        parts = run_name.split("-", 1)
        tag = parts[1] if len(parts) > 1 else "?"
        op_label = _OP_LABELS.get(tag, tag)
        try:
            ts = datetime.datetime.fromtimestamp(int(parts[0])).strftime("%Y-%m-%d %H:%M")
        except (ValueError, OSError):
            ts = parts[0]
        fetch_done = os.path.exists(os.path.join(op_dir, "apt-offline.sig")) and \
                     os.path.getsize(os.path.join(op_dir, "apt-offline.sig")) > 0
        state_path = os.path.join(op_dir, "state.json")
        try:
            with open(state_path) as f:
                state = json.load(f)
            download_done = state.get("downloaded", False)
            install_done = state.get("installed", False)
        except (OSError, ValueError):
            download_done = False
            install_done = False
        line = "  %-16s  %-14s%s%s%s%s\n" % (
            ts, op_label,
            _phase_str("fetch", fetch_done, use_color),
            _phase_str("download", download_done, use_color),
            _phase_str("install", install_done, use_color),
            ("  [%s]" % run_name) if not use_color else ("  " + _DIM + run_name + _RESET),
        )
        sys.stdout.write(line)
    sys.stdout.flush()



def _run_fetcher(sig_path, bundle_path, cache_dir=None, metadata_cache_dir=None):
    if cache_dir:
        os.makedirs(cache_dir, exist_ok=True)
    if metadata_cache_dir:
        os.makedirs(metadata_cache_dir, exist_ok=True)
    tmpdir = tempfile.mkdtemp(prefix="apt-offline-")
    saved_cwd = os.getcwd()
    try:
        try:
            fetcher(argparse.Namespace(
                get=sig_path,
                bundle_file=bundle_path,
                socket_timeout=30,
                download_dir=tmpdir,
                cache_dir=cache_dir,
                metadata_cache_dir=metadata_cache_dir,
                disable_md5check=False,
                num_of_threads=1,
                proxy_host=None,
                proxy_port=None,
                https_cert_file=None,
                https_key_file=None,
                http_basicauth=[],
                disable_cert_check=False,
                deb_bugs=False,
                quiet=False,
            ))
        except SystemExit as e:
            if e.code not in (0, None):
                raise RuntimeError("apt-offline get failed (exit %s)" % e.code)
    finally:
        os.chdir(saved_cwd)
        shutil.rmtree(tmpdir, ignore_errors=True)


def _detect_sudo(host):
    result = subprocess.run(
        ["ssh", "-o", "LogLevel=QUIET", host, "id -u"],
        capture_output=True, text=True
    )
    if result.returncode == 0 and result.stdout.strip().splitlines()[-1] == "0":
        return []
    if result.returncode == 255:
        raise RuntimeError("Cannot connect to %s" % host)
    probe = subprocess.run(
        ["ssh", "-o", "LogLevel=QUIET", host, "sudo -n true"],
        capture_output=True
    )
    if probe.returncode != 0:
        raise RuntimeError(
            "Remote user on %s is not root and sudo requires a password.\n"
            "Add a sudoers entry for the commands apt-offline needs, e.g.:\n"
            "  your_user ALL=(ALL) NOPASSWD: /usr/bin/apt-offline, /usr/bin/apt-get, /sbin/reboot, /bin/mkdir"
            % host
        )
    return ["sudo"]


def _check_remote_prereqs(host):
    result = subprocess.run(
        ["ssh", "-o", "LogLevel=QUIET", host,
         "which apt-offline && echo OK || echo MISSING"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        msg = "Cannot connect to %s" % host
        if stderr:
            msg += ": %s" % stderr
        raise RuntimeError(msg)
    last_line = result.stdout.strip().splitlines()[-1] if result.stdout.strip() else ""
    if last_line != "OK":
        raise RuntimeError(
            "apt-offline is not installed on %s.\n"
            "Install it with: sudo apt-get install apt-offline" % host
        )


def _mark_state(op_dir, **kwargs):
    state_path = os.path.join(op_dir, "state.json")
    with open(state_path) as f:
        state = json.load(f)
    state.update(kwargs)
    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)


def _mark_installed(op_dir):
    _mark_state(op_dir, installed=True)


def _mark_downloaded(op_dir):
    _mark_state(op_dir, downloaded=True)


def _cleanup_host(work_dir, keep):
    op_dirs = sorted(
        [d for d in glob.glob(os.path.join(work_dir, "*-*")) if os.path.isdir(d)]
    )
    to_remove = op_dirs[:-keep] if keep > 0 else op_dirs
    for op_dir in to_remove:
        shutil.rmtree(op_dir, ignore_errors=True)


def _op_tag(args):
    if args.op_dist_upgrade:
        return "dup"
    if args.op_upgrade:
        return "upg"
    if args.op_update:
        return "upd"
    return "ipk"


def _remote_single(host, args, log):
    if args.work_dir:
        base_dir = args.work_dir
    elif args.temp:
        base_dir = "/tmp/apt-offline-remote"
    else:
        base_dir = os.path.expanduser("~/.cache/apt-offline-remote")
    work_dir = os.path.join(base_dir, host)

    if args.status:
        _show_status(host, work_dir, log)
        return

    if (args.reboot
            and not args.op_update and not args.op_upgrade
            and not args.op_dist_upgrade and not args.op_install_packages
            and args.remote_phase is None):
        sudo_prefix = _detect_sudo(host)
        log.msg("==> Rebooting %s...\n" % host)
        try:
            _ssh_run(host, sudo_prefix + ["reboot"])
        except subprocess.CalledProcessError as e:
            if e.returncode != 255:
                raise
        log.msg("==> Reboot command sent to %s\n" % host)
        return

    phase = args.remote_phase  # "fetch", "download", "finish-install", or None (full)
    keep = args.keep_latest
    clean_remote = args.clean_remote

    # standalone per-host cleanup — no phase, no operation flags
    if (phase is None
            and not args.op_update
            and not args.op_upgrade
            and not args.op_dist_upgrade
            and not args.op_install_packages
            and (keep is not None or clean_remote)):
        if clean_remote:
            log.msg("==> Cleaning remote cache on %s...\n" % host)
            _ssh_run(host, ["rm", "-rf", _REMOTE_CACHE])
            log.msg("==> Remote cache cleaned for %s\n" % host)
        if keep is not None:
            if not os.path.isdir(work_dir):
                log.msg("==> Nothing to clean locally for %s (work dir does not exist)\n" % host)
            else:
                _cleanup_host(work_dir, keep)
                log.msg("==> Cleaned up local work dir for %s (kept %d)\n" % (host, keep))
        return

    # ------------------------------------------------------------------ phase 2
    if phase == "download":
        if not os.path.isdir(work_dir):
            log.warn("No local state for %s — run --fetch first\n" % host)
            return "skipped"
        try:
            state = _latest_state(work_dir)
        except FileNotFoundError:
            log.warn("No local state for %s — run --fetch first\n" % host)
            return "skipped"
        op_dir = os.path.join(work_dir, state["op_dir"])
        local_sig = os.path.join(op_dir, "apt-offline.sig")
        local_bundle = os.path.join(op_dir, "bundle.zip")
        if args.force and os.path.exists(local_bundle):
            os.remove(local_bundle)
        pkg_cache = None if args.no_pkg_cache else os.path.join(base_dir, "pkg-cache")
        meta_cache = os.path.join(base_dir, "metadata-cache") if args.cache_metadata else None
        log.msg("==> Creating bundle from %s...\n" % local_sig)
        _run_fetcher(local_sig, local_bundle, cache_dir=pkg_cache, metadata_cache_dir=meta_cache)
        _mark_downloaded(op_dir)
        log.success("Bundle created: %s\n" % local_bundle)
        return

    # ------------------------------------------------------------------ phase 3
    if phase == "finish-install":
        if not os.path.isdir(work_dir):
            log.warn("No local state for %s — run --fetch first\n" % host)
            return "skipped"
        try:
            state = _latest_state(work_dir)
        except FileNotFoundError:
            log.warn("No local state for %s — run --fetch first\n" % host)
            return "skipped"
        op_dir = os.path.join(work_dir, state["op_dir"])
        if not state.get("downloaded", False):
            raise RuntimeError("bundle for %s was not successfully downloaded — run --download first" % host)
        _check_remote_prereqs(host)
        sudo_prefix = _detect_sudo(host)
        local_bundle = os.path.join(op_dir, "bundle.zip")
        remote_op_dir = "%s/%s" % (_REMOTE_CACHE, state["op_dir"])
        remote_bundle = "%s/bundle.zip" % remote_op_dir
        _ssh_run(host, ["mkdir", "-p", remote_op_dir])
        log.msg("==> Detecting transfer method...\n")
        transfer = _detect_transfer_method(host)
        log.msg("==> Using %s for file transfers\n" % transfer)
        log.msg("==> [1/3] Sending bundle to %s...\n" % host)
        _transfer_put(transfer, host, local_bundle, remote_bundle)
        log.msg("==> [2/3] Installing bundle on %s...\n" % host)
        _ssh_run(host, sudo_prefix + ["apt-offline", "install", remote_bundle])
        log.msg("==> [3/3] Running apt-get on %s...\n" % host)
        apt_env = ["env", "DEBIAN_FRONTEND=noninteractive"]
        apt_opts = ["-y", "-o", "Dpkg::Options::=--force-confold"]
        if state["dist_upgrade"]:
            _ssh_run(host, sudo_prefix + apt_env + ["apt-get", "dist-upgrade"] + apt_opts)
        elif state["upgrade"]:
            _ssh_run(host, sudo_prefix + apt_env + ["apt-get", "upgrade"] + apt_opts)
        elif state["install_packages"]:
            _ssh_run(host, sudo_prefix + apt_env + ["apt-get", "install"] + apt_opts + state["install_packages"])
        _mark_installed(op_dir)
        log.success("Operation completed successfully for %s\n" % host)
        if args.reboot:
            log.msg("==> Rebooting %s...\n" % host)
            try:
                _ssh_run(host, sudo_prefix + ["reboot"])
            except subprocess.CalledProcessError as e:
                if e.returncode != 255:
                    raise
            log.msg("==> Reboot command sent to %s\n" % host)
        return

    # --------------------------------------------------- phase 1 / full pipeline
    if (not args.op_update
            and not args.op_upgrade
            and not args.op_dist_upgrade
            and not args.op_install_packages):
        log.err("At least one of --update, --upgrade, --dist-upgrade or --install-packages must be specified\n")
        raise SystemExit(1)

    _check_remote_prereqs(host)
    sudo_prefix = _detect_sudo(host)
    timestamp = int(time.time())
    tag = _op_tag(args)
    op_dir = os.path.join(work_dir, "%d-%s" % (timestamp, tag))
    os.makedirs(op_dir, exist_ok=True)
    remote_op_dir = "%s/%d-%s" % (_REMOTE_CACHE, timestamp, tag)
    remote_sig = "%s/apt-offline.sig" % remote_op_dir
    remote_bundle = "%s/bundle.zip" % remote_op_dir
    local_sig = os.path.join(op_dir, "apt-offline.sig")
    local_bundle = os.path.join(op_dir, "bundle.zip")
    local_state = os.path.join(op_dir, "state.json")
    _ssh_run(host, ["mkdir", "-p", remote_op_dir])

    log.msg("==> Detecting transfer method...\n")
    transfer = _detect_transfer_method(host)
    log.msg("==> Using %s for file transfers\n" % transfer)

    _ssh_run(host, sudo_prefix + ["mkdir", "-p", "/var/lib/apt/lists/partial"])

    steps = 2 if phase == "fetch" else 5
    log.msg("==> [1/%d] Generating signature on %s...\n" % (steps, host))
    set_cmd = sudo_prefix + ["apt-offline", "set", remote_sig]
    if args.op_install_packages:
        set_cmd += ["--install-packages"] + args.op_install_packages
    if args.op_update:
        set_cmd += ["--update"]
    if args.op_upgrade:
        set_cmd += ["--upgrade"]
    if args.op_dist_upgrade:
        set_cmd += ["--upgrade", "--upgrade-type", "dist-upgrade"]
    set_error = None
    try:
        _ssh_run(host, set_cmd)
    except subprocess.CalledProcessError as e:
        set_error = e

    log.msg("==> [2/%d] Fetching signature...\n" % steps)
    try:
        _transfer_get(transfer, host, remote_sig, local_sig)
    except subprocess.CalledProcessError:
        if set_error:
            raise set_error
        raise

    if os.path.getsize(local_sig) == 0:
        log.warn("Nothing to do on %s — system is already up to date\n" % host)
        shutil.rmtree(op_dir, ignore_errors=True)
        return "skipped"

    if set_error:
        raise set_error

    with open(local_state, "w") as f:
        json.dump({
            "timestamp": timestamp,
            "op_dir": "%d-%s" % (timestamp, tag),
            "update": args.op_update,
            "upgrade": args.op_upgrade,
            "dist_upgrade": args.op_dist_upgrade,
            "install_packages": args.op_install_packages or [],
            "downloaded": False,
            "installed": False,
        }, f, indent=2)

    if phase == "fetch":
        log.success("Signature fetched: %s\n" % local_sig)
        log.msg("==> Run 'apt-offline remote %s --download' to create the bundle when online\n" % host)
        return

    if args.force and os.path.exists(local_bundle):
        os.remove(local_bundle)
    pkg_cache = None if args.no_pkg_cache else os.path.join(base_dir, "pkg-cache")
    meta_cache = os.path.join(base_dir, "metadata-cache") if args.cache_metadata else None
    log.msg("==> [3/5] Creating bundle locally...\n")
    _run_fetcher(local_sig, local_bundle, cache_dir=pkg_cache, metadata_cache_dir=meta_cache)
    _mark_downloaded(op_dir)

    log.msg("==> [4/5] Sending bundle to remote...\n")
    _transfer_put(transfer, host, local_bundle, remote_bundle)

    log.msg("==> [5/5] Installing bundle on remote...\n")
    _ssh_run(host, sudo_prefix + ["apt-offline", "install", remote_bundle])

    apt_env = ["env", "DEBIAN_FRONTEND=noninteractive"]
    apt_opts = ["-y", "-o", "Dpkg::Options::=--force-confold"]
    if args.op_dist_upgrade:
        _ssh_run(host, sudo_prefix + apt_env + ["apt-get", "dist-upgrade"] + apt_opts)
    elif args.op_upgrade:
        _ssh_run(host, sudo_prefix + apt_env + ["apt-get", "upgrade"] + apt_opts)
    elif args.op_install_packages:
        _ssh_run(host, sudo_prefix + apt_env + ["apt-get", "install"] + apt_opts + args.op_install_packages)

    _mark_installed(op_dir)
    log.success("Operation completed successfully for %s\n" % host)

    if args.reboot:
        log.msg("==> Rebooting %s...\n" % host)
        _ssh_run(host, sudo_prefix + ["reboot"])


def _read_hosts_file(path):
    hosts = []
    with open(path) as f:
        for line in f:
            line = line.split("#")[0].strip()
            if line:
                hosts.append(line)
    if not hosts:
        raise ValueError("No hosts found in %s" % path)
    return hosts


def _validate_host(host):
    """SSH targets become directory names. Keep them a single path segment."""
    if (
        not host
        or host in (".", "..")
        or "/" in host
        or "\\" in host
        or "\n" in host
        or "\0" in host
        or host.startswith("-")
    ):
        raise ValueError(
            "invalid SSH host %r (expected an alias or [user@]hostname)" % host
        )


def remote(args):
    from apt_offline_core import AptOfflineCoreLib
    log = AptOfflineCoreLib.log

    if args.remote_host and args.hosts_list:
        log.err("Cannot specify both SSH_HOST and --hosts-list\n")
        sys.exit(1)
    if not args.remote_host and not args.hosts_list:
        log.err("Must specify either SSH_HOST or --hosts-list\n")
        sys.exit(1)
    if args.remote_phase is not None and (args.keep_latest is not None or args.clean_remote
                                           or args.clean_cache or args.clean_pkg_cache or args.clean_metadata_cache):
        log.err("--keep-latest, --clean-remote and cache cleanup flags cannot be combined with --fetch, --download or --finish-install\n")
        sys.exit(1)
    if args.remote_phase in ("download", "finish-install") and (
            args.op_update
            or args.op_upgrade
            or args.op_dist_upgrade
            or args.op_install_packages):
        log.err("--update, --upgrade, --dist-upgrade and --install-packages cannot be combined with --download or --finish-install (operation was already saved by --fetch)\n")
        sys.exit(1)
    if args.force and args.remote_phase in ("fetch", "finish-install"):
        log.err("--force can only be used with --download or the full pipeline\n")
        sys.exit(1)
    if args.reboot and args.remote_phase in ("fetch", "download"):
        log.err("--reboot cannot be combined with --fetch or --download\n")
        sys.exit(1)

    if args.hosts_list:
        try:
            hosts = _read_hosts_file(args.hosts_list)
        except (OSError, ValueError) as e:
            log.err("Error reading hosts list: %s\n" % e)
            sys.exit(1)
    else:
        hosts = args.remote_host

    for host in hosts:
        try:
            _validate_host(host)
        except ValueError as e:
            log.err("%s\n" % e)
            sys.exit(1)

    if args.work_dir:
        base_dir = args.work_dir
    elif args.temp:
        base_dir = "/tmp/apt-offline-remote"
    else:
        base_dir = os.path.expanduser("~/.cache/apt-offline-remote")

    clean_pkg_cache = args.clean_pkg_cache or args.clean_cache
    clean_metadata_cache = args.clean_metadata_cache or args.clean_cache
    for label, subdir in [("pkg-cache", "pkg-cache"), ("metadata-cache", "metadata-cache")]:
        if (label == "pkg-cache" and clean_pkg_cache) or (label == "metadata-cache" and clean_metadata_cache):
            cache_path = os.path.join(base_dir, subdir)
            if os.path.isdir(cache_path):
                shutil.rmtree(cache_path)
                log.msg("==> Cleaned %s (%s)\n" % (label, cache_path))

    if not (args.remote_phase is not None
            or args.op_update or args.op_upgrade
            or args.op_dist_upgrade or args.op_install_packages
            or args.keep_latest is not None or args.clean_remote
            or args.reboot or args.status):
        return

    if args.reboot and len(hosts) > 1:
        log.warn("--reboot with multiple hosts: if any host acts as a jumphost for others in the list, rebooting it may drop mid-operation connections to hosts behind it. Ensure jumphosts appear last in the list.\n")

    succeeded = []
    skipped = []
    failed = []

    for host in hosts:
        if len(hosts) > 1:
            log.msg("\n==> Host: %s\n" % host)
        try:
            result = _remote_single(host, args, log)
            if result == "skipped":
                skipped.append(host)
            else:
                succeeded.append(host)
        except Exception as e:
            log.err("FAILED %s: %s\n" % (host, e))
            failed.append(host)

    if len(hosts) > 1:
        log.msg("\n==> Batch summary: %d succeeded, %d skipped, %d failed\n" % (len(succeeded), len(skipped), len(failed)))
        for host in succeeded:
            log.msg("   OK: %s\n" % host)
        for host in skipped:
            log.warn("%s\n" % host)
        for host in failed:
            log.err("%s\n" % host)
    if failed:
        sys.exit(1)


def register_subparser(subparsers, global_options):
    parser_remote = subparsers.add_parser(
        "remote",
        parents=[global_options],
        add_help=False,
        help="Run the full set/get/install pipeline against a remote host over SSH",
    )
    parser_remote.set_defaults(func=remote)

    parser_remote.add_argument(
        "-h", "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit",
    )

    parser_remote.add_argument(
        "remote_host",
        nargs="*",
        default=None,
        help="One or more SSH hosts to target (aliases from ~/.ssh/config, or [user@]hostname)",
        metavar="SSH_HOST",
    )

    parser_remote.add_argument(
        "--hosts-list",
        dest="hosts_list",
        help="Text file with one SSH host per line (# comments and blank lines ignored)",
        action="store",
        type=str,
        default=None,
        metavar="FILE",
    )

    parser_remote.add_argument(
        "--update",
        dest="op_update",
        help="Generate signature to update APT database on the remote",
        action="store_true",
    )

    parser_remote.add_argument(
        "--upgrade",
        dest="op_upgrade",
        help="Generate signature of packages to be upgraded on the remote",
        action="store_true",
    )

    parser_remote.add_argument(
        "--dist-upgrade",
        dest="op_dist_upgrade",
        help="Perform a full dist-upgrade on the remote",
        action="store_true",
    )

    parser_remote.add_argument(
        "--install-packages",
        dest="op_install_packages",
        help="Packages to install on the remote machine",
        action="store",
        type=str,
        nargs="*",
        metavar="PKG",
    )

    parser_remote.add_argument(
        "--reboot",
        dest="reboot",
        help="Reboot the remote machine after a successful operation",
        action="store_true",
    )

    work_dir_group = parser_remote.add_mutually_exclusive_group()
    work_dir_group.add_argument(
        "--work-dir",
        dest="work_dir",
        help="Local base directory for sig/bundle files (default: ~/.cache/apt-offline-remote)",
        action="store",
        type=str,
        default=None,
        metavar="DIR",
    )
    work_dir_group.add_argument(
        "--temp",
        dest="temp",
        help="Use /tmp/apt-offline-remote as the local working directory",
        action="store_true",
        default=False,
    )

    parser_remote.add_argument(
        "--force",
        dest="force",
        help="Overwrite an existing bundle instead of failing",
        action="store_true",
        default=False,
    )

    parser_remote.add_argument(
        "--cache-metadata",
        dest="cache_metadata",
        help="Cache metadata files (Release, Packages, Translation) under <work-dir>/metadata-cache to avoid re-downloading across hosts (may serve stale data across runs)",
        action="store_true",
        default=False,
    )

    parser_remote.add_argument(
        "--no-pkg-cache",
        dest="no_pkg_cache",
        help="Disable the local package cache (default: <work-dir>/pkg-cache)",
        action="store_true",
        default=False,
    )

    parser_remote.add_argument(
        "--keep-latest",
        dest="keep_latest",
        help="Keep only the N most recent local operations per host (default: 1 if flag is given)",
        nargs="?",
        const=1,
        default=None,
        type=int,
        metavar="N",
    )

    parser_remote.add_argument(
        "--clean-remote",
        dest="clean_remote",
        help="Remove ~/.cache/apt-offline-remote on the remote host(s)",
        action="store_true",
        default=False,
    )

    parser_remote.add_argument(
        "--clean-cache",
        dest="clean_cache",
        help="Remove both pkg-cache and metadata-cache under the local work directory",
        action="store_true",
        default=False,
    )

    parser_remote.add_argument(
        "--clean-pkg-cache",
        dest="clean_pkg_cache",
        help="Remove only the pkg-cache under the local work directory",
        action="store_true",
        default=False,
    )

    parser_remote.add_argument(
        "--clean-metadata-cache",
        dest="clean_metadata_cache",
        help="Remove only the metadata-cache under the local work directory",
        action="store_true",
        default=False,
    )

    parser_remote.add_argument(
        "--status",
        dest="status",
        help="Show the pipeline status of local runs for the given host(s)",
        action="store_true",
        default=False,
    )

    phase_group = parser_remote.add_mutually_exclusive_group()
    phase_group.add_argument(
        "--fetch",
        dest="remote_phase",
        action="store_const",
        const="fetch",
        help="Phase 1: generate and fetch the signature from the remote only",
    )
    phase_group.add_argument(
        "--download",
        dest="remote_phase",
        action="store_const",
        const="download",
        help="Phase 2: download packages locally and create bundle from the latest fetched signature",
    )
    phase_group.add_argument(
        "--finish-install",
        dest="remote_phase",
        action="store_const",
        const="finish-install",
        help="Phase 3: push the latest bundle to remote and complete the installation",
    )
    parser_remote.set_defaults(remote_phase=None)
