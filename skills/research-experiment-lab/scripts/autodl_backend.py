#!/usr/bin/env python3
"""Safe SSH/SCP backend for immutable AutoDL experiment runs."""

from __future__ import annotations

import argparse
import json
import posixpath
import shlex
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Any

from experiment_common import atomic_json, now, read_json, require_id, sha256_file


AUTH_MODES = {"batch", "interactive-password"}
SESSION_BACKENDS = {"tmux", "screen"}
FORBIDDEN_CREDENTIAL_FIELDS = {"password", "password_file", "private_key"}


def profile_from(path: Path, name: str) -> dict[str, Any]:
    root = read_json(path)
    profiles = root.get("profiles")
    if not isinstance(profiles, dict) or not isinstance(profiles.get(name), dict):
        raise ValueError(f"profile not found: {name}")
    profile = profiles[name]
    remote_root = profile.get("remote_root")
    if not isinstance(remote_root, str):
        raise ValueError("profile remote_root must be a string")
    normalized = str(PurePosixPath(remote_root))
    if (
        not normalized.startswith(("/root/autodl-tmp/", "/root/autodl-nas/"))
        or ".." in PurePosixPath(normalized).parts
    ):
        raise ValueError("remote_root must be a child of /root/autodl-tmp or /root/autodl-nas")
    profile = dict(profile)
    profile["remote_root"] = normalized.rstrip("/")
    forbidden = sorted(FORBIDDEN_CREDENTIAL_FIELDS.intersection(profile))
    if forbidden:
        raise ValueError(
            "profile must not store credential fields: " + ", ".join(forbidden)
        )
    auth = profile.get("auth", "batch")
    if auth not in AUTH_MODES:
        raise ValueError(f"profile auth must be one of: {', '.join(sorted(AUTH_MODES))}")
    profile["auth"] = auth
    session_backend = profile.get("session_backend", "tmux")
    if session_backend not in SESSION_BACKENDS:
        raise ValueError(
            "profile session_backend must be one of: "
            + ", ".join(sorted(SESSION_BACKENDS))
        )
    profile["session_backend"] = session_backend
    if "ssh_alias" not in profile:
        for field in ("host", "user", "port"):
            if field not in profile:
                raise ValueError(f"direct profile requires {field}")
        if not isinstance(profile["port"], int) or not 1 <= profile["port"] <= 65535:
            raise ValueError("profile port must be 1..65535")
    return profile


def auth_parts(profile: dict[str, Any]) -> list[str]:
    if profile.get("auth", "batch") == "interactive-password":
        return [
            "-o",
            "BatchMode=no",
            "-o",
            "PreferredAuthentications=password",
            "-o",
            "PubkeyAuthentication=no",
            "-o",
            "NumberOfPasswordPrompts=1",
        ]
    return ["-o", "BatchMode=yes"]


def ssh_parts(profile: dict[str, Any]) -> list[str]:
    command = ["ssh", *auth_parts(profile)]
    if profile.get("identity_file"):
        command.extend(["-i", str(profile["identity_file"])])
    if "ssh_alias" in profile:
        command.append(str(profile["ssh_alias"]))
    else:
        command.extend(["-p", str(profile["port"]), f"{profile['user']}@{profile['host']}"])
    return command


def scp_parts(profile: dict[str, Any]) -> list[str]:
    command = ["scp", *auth_parts(profile)]
    if profile.get("identity_file"):
        command.extend(["-i", str(profile["identity_file"])])
    if "ssh_alias" not in profile:
        command.extend(["-P", str(profile["port"])])
    return command


def remote_target(profile: dict[str, Any], path: str) -> str:
    host = str(profile.get("ssh_alias") or f"{profile['user']}@{profile['host']}")
    return f"{host}:{path}"


def execute(command: list[str], dry_run: bool) -> int:
    print("COMMAND:", json.dumps(command, ensure_ascii=False))
    if dry_run:
        return 0
    result = subprocess.run(command, text=True, check=False)
    return result.returncode


def checked(command: list[str], dry_run: bool) -> None:
    code = execute(command, dry_run)
    if code != 0:
        raise RuntimeError(f"command failed with exit code {code}")


def capture_checked(command: list[str], dry_run: bool) -> str:
    print("COMMAND:", json.dumps(command, ensure_ascii=False))
    if dry_run:
        return ""
    result = subprocess.run(command, text=True, capture_output=True, check=False)
    if result.returncode != 0:
        if result.stdout:
            print(result.stdout, end="")
        if result.stderr:
            print(result.stderr, end="", file=sys.stderr)
        raise RuntimeError(f"command failed with exit code {result.returncode}")
    return result.stdout


def remote_join(profile: dict[str, Any], *parts: str) -> str:
    path = posixpath.normpath(posixpath.join(profile["remote_root"], *parts))
    root = profile["remote_root"]
    if path != root and not path.startswith(root + "/"):
        raise ValueError(f"remote path escapes configured root: {path}")
    return path


def session_launch_command(profile: dict[str, Any], session: str, runner_command: str) -> str:
    backend = profile["session_backend"]
    if backend == "tmux":
        return (
            f"tmux new-session -d -s {shlex.quote(session)} "
            f"{shlex.quote(runner_command)}"
        )
    return (
        f"screen -DmS {shlex.quote(session)} sh -lc "
        f"{shlex.quote('exec ' + runner_command)}"
    )


def preflight(profile: dict[str, Any], dry_run: bool) -> None:
    root = profile["remote_root"]
    session_backend = profile["session_backend"]
    disk_probe = (
        "/root/autodl-tmp"
        if root.startswith("/root/autodl-tmp/")
        else "/root/autodl-nas"
    )
    command = (
        "set -eu; "
        "printf 'host='; hostname; "
        "printf 'python='; python3 --version; "
        f"printf 'session_backend={session_backend}\\n'; "
        f"printf 'session_binary='; command -v {shlex.quote(session_backend)}; "
        "printf 'gpu\\n'; nvidia-smi --query-gpu=index,name,memory.total "
        "--format=csv,noheader 2>/dev/null || printf 'unavailable\\n'; "
        f"printf 'disk\\n'; df -h {shlex.quote(root)} 2>/dev/null || "
        f"df -h {shlex.quote(disk_probe)}"
    )
    checked(ssh_parts(profile) + [command], dry_run)


def push_snapshot(args: argparse.Namespace, profile: dict[str, Any]) -> None:
    archive = args.archive.resolve()
    manifest = args.manifest.resolve()
    if not archive.is_file() or not manifest.is_file():
        raise ValueError("snapshot archive and manifest must exist")
    metadata = read_json(manifest)
    snapshot_id = require_id(str(metadata.get("snapshot_id")), "snapshot_id")
    incoming = remote_join(profile, "incoming")
    snapshots = remote_join(profile, "snapshots")
    destination = remote_join(profile, "snapshots", snapshot_id)
    remote_archive = posixpath.join(incoming, archive.name)
    remote_manifest = posixpath.join(incoming, manifest.name)
    create = (
        f"set -eu; mkdir -p {shlex.quote(incoming)} {shlex.quote(snapshots)}; "
        f"test ! -e {shlex.quote(destination)}"
    )
    checked(ssh_parts(profile) + [create], args.dry_run)
    checked(
        scp_parts(profile)
        + [str(archive), str(manifest), remote_target(profile, incoming + "/")],
        args.dry_run,
    )
    extract = (
        f"set -eu; test ! -e {shlex.quote(destination)}; "
        f"mkdir {shlex.quote(destination)}; "
        f"python3 -m zipfile -e {shlex.quote(remote_archive)} {shlex.quote(destination)}; "
        f"cp {shlex.quote(remote_manifest)} {shlex.quote(destination + '/snapshot_manifest.json')}"
    )
    checked(ssh_parts(profile) + [extract], args.dry_run)
    sync = {
        "schema_version": "research-experiment/sync-manifest-v1",
        "timestamp": now(),
        "direction": "local-to-remote",
        "operation": "push-snapshot",
        "snapshot_id": snapshot_id,
        "source_files": [
            {"path": str(archive), "size_bytes": archive.stat().st_size, "sha256": sha256_file(archive)},
            {"path": str(manifest), "size_bytes": manifest.stat().st_size, "sha256": sha256_file(manifest)},
        ],
        "destination": destination,
        "profile": args.profile,
        "dry_run": args.dry_run,
        "status": "planned" if args.dry_run else "completed",
    }
    if not args.dry_run:
        atomic_json(args.sync_manifest.resolve(), sync)


def launch(args: argparse.Namespace, profile: dict[str, Any]) -> None:
    experiment_id = require_id(args.experiment_id, "experiment_id")
    run_id = require_id(args.run_id, "run_id")
    snapshot_id = require_id(args.snapshot_id, "snapshot_id")
    local_records = args.local_run_dir.resolve()
    if (local_records / "records").is_dir():
        local_records = local_records / "records"
    command_json = local_records / "command.json"
    run_manifest = local_records / "run_manifest.json"
    if not command_json.is_file() or not run_manifest.is_file():
        raise ValueError("local run records require command.json and run_manifest.json")
    remote_run_dir = remote_join(profile, "experiments", experiment_id, "runs", run_id)
    remote_records = posixpath.join(remote_run_dir, "records")
    workspace = remote_join(profile, "snapshots", snapshot_id)
    create = (
        f"set -eu; test -d {shlex.quote(workspace)}; "
        f"test ! -e {shlex.quote(remote_run_dir)}; "
        f"mkdir -p {shlex.quote(remote_records)}"
    )
    checked(ssh_parts(profile) + [create], args.dry_run)
    script_dir = Path(__file__).resolve().parent
    files = [
        command_json,
        run_manifest,
        script_dir / "remote_run.py",
        script_dir / "experiment_common.py",
    ]
    checked(
        scp_parts(profile) + [*(str(path) for path in files), remote_target(profile, remote_run_dir + "/")],
        args.dry_run,
    )
    # Put immutable input records in records/ while keeping runners at run root.
    arrange = (
        f"set -eu; mv {shlex.quote(remote_run_dir + '/command.json')} "
        f"{shlex.quote(remote_records + '/command.json')}; "
        f"mv {shlex.quote(remote_run_dir + '/run_manifest.json')} "
        f"{shlex.quote(remote_records + '/run_manifest.json')}"
    )
    checked(ssh_parts(profile) + [arrange], args.dry_run)
    session = ("exp-" + run_id)[:80]
    runner_argv = [
        "python3",
        remote_run_dir + "/remote_run.py",
        "--run-dir",
        remote_run_dir,
        "--workspace",
        workspace,
        "--command-json",
        remote_records + "/command.json",
    ]
    runner_command = shlex.join(runner_argv)
    session_command = session_launch_command(profile, session, runner_command)
    checked(ssh_parts(profile) + [session_command], args.dry_run)
    sync = {
        "schema_version": "research-experiment/sync-manifest-v1",
        "timestamp": now(),
        "direction": "local-to-remote",
        "operation": "launch-inputs",
        "experiment_id": experiment_id,
        "run_id": run_id,
        "snapshot_id": snapshot_id,
        "profile": args.profile,
        "source_files": [
            {"path": str(path), "size_bytes": path.stat().st_size, "sha256": sha256_file(path)}
            for path in files
        ],
        "destination": remote_run_dir,
        "dry_run": args.dry_run,
        "status": "planned" if args.dry_run else "completed",
    }
    if not args.dry_run:
        atomic_json(local_records / "sync_manifest.json", sync)


def status(args: argparse.Namespace, profile: dict[str, Any]) -> None:
    experiment_id = require_id(args.experiment_id, "experiment_id")
    run_id = require_id(args.run_id, "run_id")
    status_path = remote_join(
        profile, "experiments", experiment_id, "runs", run_id, "records", "status.json"
    )
    command = (
        f"if test -f {shlex.quote(status_path)}; then cat {shlex.quote(status_path)}; "
        "else printf '{\"state\":\"not-reported\"}\\n'; fi"
    )
    checked(ssh_parts(profile) + [command], args.dry_run)


def pull_records(args: argparse.Namespace, profile: dict[str, Any]) -> None:
    experiment_id = require_id(args.experiment_id, "experiment_id")
    run_id = require_id(args.run_id, "run_id")
    destination = args.destination.resolve()
    if destination.exists():
        raise ValueError(f"pull destination already exists: {destination}")
    if not args.dry_run:
        destination.mkdir(parents=True)
    remote_records = remote_join(
        profile, "experiments", experiment_id, "runs", run_id, "records"
    )
    checked(
        scp_parts(profile) + ["-r", remote_target(profile, remote_records), str(destination)],
        args.dry_run,
    )
    files = []
    if not args.dry_run:
        for path in sorted(destination.rglob("*")):
            if path.is_file():
                files.append(
                    {
                        "path": path.relative_to(destination).as_posix(),
                        "size_bytes": path.stat().st_size,
                        "sha256": sha256_file(path),
                    }
                )
    if not args.dry_run:
        atomic_json(
            destination / "sync_manifest.json",
            {
                "schema_version": "research-experiment/sync-manifest-v1",
                "timestamp": now(),
                "direction": "remote-to-local",
                "operation": "pull-records",
                "experiment_id": experiment_id,
                "run_id": run_id,
                "profile": args.profile,
                "source": remote_records,
                "destination": str(destination),
                "files": files,
                "dry_run": False,
                "status": "completed",
            },
        )


def pull_output(args: argparse.Namespace, profile: dict[str, Any]) -> None:
    experiment_id = require_id(args.experiment_id, "experiment_id")
    run_id = require_id(args.run_id, "run_id")
    relative = PurePosixPath(args.relative_path)
    if relative.is_absolute() or ".." in relative.parts or str(relative) in {"", "."}:
        raise ValueError("relative output path must be a non-empty child path")
    remote_output = remote_join(
        profile,
        "experiments",
        experiment_id,
        "runs",
        run_id,
        "outputs",
        str(relative),
    )
    destination = args.destination.resolve()
    if destination.exists():
        raise ValueError(f"output destination already exists: {destination}")
    size_command = f"set -eu; test -e {shlex.quote(remote_output)}; du -sb {shlex.quote(remote_output)} | cut -f1"
    raw_size = capture_checked(ssh_parts(profile) + [size_command], args.dry_run).strip()
    size_bytes = None if args.dry_run else int(raw_size)
    if size_bytes is not None and size_bytes > args.max_bytes:
        raise ValueError(
            f"remote output is {size_bytes} bytes, above --max-bytes {args.max_bytes}"
        )
    if not args.dry_run:
        destination.mkdir(parents=True)
    checked(
        scp_parts(profile) + ["-r", remote_target(profile, remote_output), str(destination)],
        args.dry_run,
    )
    if not args.dry_run:
        files = [
            {
                "path": path.relative_to(destination).as_posix(),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
            for path in sorted(destination.rglob("*"))
            if path.is_file()
        ]
        atomic_json(
            destination / "sync_manifest.json",
            {
                "schema_version": "research-experiment/sync-manifest-v1",
                "timestamp": now(),
                "direction": "remote-to-local",
                "operation": "pull-output",
                "experiment_id": experiment_id,
                "run_id": run_id,
                "relative_output_path": str(relative),
                "source": remote_output,
                "destination": str(destination),
                "reported_remote_size_bytes": size_bytes,
                "max_bytes": args.max_bytes,
                "files": files,
                "profile": args.profile,
                "status": "completed",
            },
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profiles", type=Path, required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--dry-run", action="store_true")
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("preflight")
    push = sub.add_parser("push-snapshot")
    push.add_argument("--archive", type=Path, required=True)
    push.add_argument("--manifest", type=Path, required=True)
    push.add_argument("--sync-manifest", type=Path, required=True)
    launch_parser = sub.add_parser("launch")
    launch_parser.add_argument("--experiment-id", required=True)
    launch_parser.add_argument("--run-id", required=True)
    launch_parser.add_argument("--snapshot-id", required=True)
    launch_parser.add_argument("--local-run-dir", type=Path, required=True)
    status_parser = sub.add_parser("status")
    status_parser.add_argument("--experiment-id", required=True)
    status_parser.add_argument("--run-id", required=True)
    pull = sub.add_parser("pull-records")
    pull.add_argument("--experiment-id", required=True)
    pull.add_argument("--run-id", required=True)
    pull.add_argument("--destination", type=Path, required=True)
    output = sub.add_parser("pull-output")
    output.add_argument("--experiment-id", required=True)
    output.add_argument("--run-id", required=True)
    output.add_argument("--relative-path", required=True)
    output.add_argument("--destination", type=Path, required=True)
    output.add_argument("--max-bytes", type=int, required=True)
    args = parser.parse_args()
    try:
        profile = profile_from(args.profiles.resolve(), args.profile)
        if args.action == "preflight":
            preflight(profile, args.dry_run)
        elif args.action == "push-snapshot":
            push_snapshot(args, profile)
        elif args.action == "launch":
            launch(args, profile)
        elif args.action == "status":
            status(args, profile)
        elif args.action == "pull-records":
            pull_records(args, profile)
        elif args.action == "pull-output":
            pull_output(args, profile)
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"autodl_backend failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
