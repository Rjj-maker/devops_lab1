#!/usr/bin/env python3
"""Run and record the DRAFT broken/reference Docker scenarios.

The script uses only the Python standard library. It never deletes images,
containers, source files, or previous evidence directories.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import shlex
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


RUNNER_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = RUNNER_DIR.parent
REPO_ROOT = PACKAGE_ROOT.parent
FIXTURE_DIR = PACKAGE_ROOT / "fixtures" / "draft"
INTERFACE_PATH = FIXTURE_DIR / "interface.json"
BROKEN_DOCKERFILE = RUNNER_DIR / "Dockerfile.broken"
REFERENCE_DOCKERFILE = RUNNER_DIR / "Dockerfile.reference"
EXPECTED_STDOUT = "hello E3\n"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def static_check() -> dict[str, Any]:
    required_files = [
        FIXTURE_DIR / "main.c",
        FIXTURE_DIR / "Makefile",
        FIXTURE_DIR / "README.md",
        INTERFACE_PATH,
        BROKEN_DOCKERFILE,
        REFERENCE_DOCKERFILE,
    ]
    missing = [str(path.relative_to(PACKAGE_ROOT)) for path in required_files if not path.is_file()]
    if missing:
        raise ValueError(f"missing required files: {missing}")

    interface = json.loads(INTERFACE_PATH.read_text(encoding="utf-8"))
    checks = {
        "project_id": interface.get("project", {}).get("id") == "e3-draft-tiny-greeting",
        "project_root": interface.get("project", {}).get("project_root")
        == "A-B_DRAFT环境交接包/fixtures/draft",
        "build_command": interface.get("build", {}).get("command") == "make",
        "build_exit_code": interface.get("build", {}).get("exit_code") == 0,
        "verify_command": interface.get("verify", {}).get("command") == "./hello",
        "verify_exit_code": interface.get("verify", {}).get("exit_code") == 0,
        "verify_stdout": interface.get("verify", {}).get("stdout") == EXPECTED_STDOUT,
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"interface check failed: {failed}")

    return {
        "status": "PASSED",
        "checked_at": utc_now(),
        "checks": checks,
        "source_sha256": {
            path.relative_to(PACKAGE_ROOT).as_posix(): sha256_file(path)
            for path in required_files
        },
    }


def display_command(command: list[str]) -> str:
    return shlex.join(command)


def run_and_record(
    name: str,
    command: list[str],
    cwd: Path,
    evidence_dir: Path,
    timeout_seconds: int,
) -> dict[str, Any]:
    started_at = utc_now()
    timed_out = False
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout_seconds,
            check=False,
        )
        exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except subprocess.TimeoutExpired as error:
        timed_out = True
        exit_code = None
        stdout = (error.stdout or "") if isinstance(error.stdout, str) else ""
        stderr = (error.stderr or "") if isinstance(error.stderr, str) else ""
        stderr += f"\ncommand timed out after {timeout_seconds} seconds\n"

    (evidence_dir / f"{name}.command.txt").write_text(
        f"cwd={cwd}\ncommand={display_command(command)}\n",
        encoding="utf-8",
    )
    (evidence_dir / f"{name}.stdout.log").write_text(stdout, encoding="utf-8")
    (evidence_dir / f"{name}.stderr.log").write_text(stderr, encoding="utf-8")
    (evidence_dir / f"{name}.exit-code.txt").write_text(
        "TIMEOUT\n" if exit_code is None else f"{exit_code}\n",
        encoding="utf-8",
    )

    return {
        "command": display_command(command),
        "working_directory": str(cwd),
        "started_at": started_at,
        "finished_at": utc_now(),
        "exit_code": exit_code,
        "timed_out": timed_out,
        "stdout_log": f"{name}.stdout.log",
        "stderr_log": f"{name}.stderr.log",
    }


def git_metadata() -> dict[str, Any]:
    safe_directory = f"safe.directory={REPO_ROOT}"
    git_prefix = [
        "git",
        "-c",
        safe_directory,
        "-c",
        "core.fileMode=false",
        "-c",
        "core.autocrlf=true",
    ]
    completed = subprocess.run(
        [*git_prefix, "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if completed.returncode != 0:
        return {"sha": None, "status": None, "error": completed.stderr.strip()}
    status = subprocess.run(
        [*git_prefix, "status", "--short"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return {
        "sha": completed.stdout.strip(),
        "status": status.stdout.splitlines() if status.returncode == 0 else None,
        "dirty": bool(status.stdout.strip()) if status.returncode == 0 else None,
    }


def parse_image_inspect(stdout: str) -> dict[str, Any]:
    try:
        value = json.loads(stdout)
        if not isinstance(value, list) or not value or not isinstance(value[0], dict):
            return {}
        image = value[0]
        return {
            "image_id": image.get("Id"),
            "repo_tags": image.get("RepoTags") or [],
            "repo_digests": image.get("RepoDigests") or [],
            "created": image.get("Created"),
            "architecture": image.get("Architecture"),
            "os": image.get("Os"),
        }
    except json.JSONDecodeError:
        return {}


def run_docker(args: argparse.Namespace, static_result: dict[str, Any]) -> int:
    docker = shutil.which("docker")
    if docker is None:
        print(
            "Docker CLI was not found. Static checks passed, but no runtime evidence was generated.",
            file=sys.stderr,
        )
        return 2

    run_id = datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%SZ")
    evidence_dir = args.output_dir or (RUNNER_DIR / "evidence" / run_id)
    evidence_dir = evidence_dir.resolve()
    if evidence_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing evidence directory: {evidence_dir}")
    evidence_dir.mkdir(parents=True)

    summary: dict[str, Any] = {
        "schema_version": "1.0",
        "run_id": run_id,
        "generated_at": utc_now(),
        "project": "e3-draft-tiny-greeting@2026-09-06",
        "git": git_metadata(),
        "host": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": sys.version,
        },
        "static_check": static_result,
        "expected": {
            "broken_build_nonzero": True,
            "reference_build_exit_code": 0,
            "verify_exit_code": 0,
            "verify_stdout": EXPECTED_STDOUT,
        },
        "stages": {},
    }

    docker_version = run_and_record(
        "docker-version",
        [docker, "version"],
        PACKAGE_ROOT,
        evidence_dir,
        args.timeout_seconds,
    )
    summary["stages"]["docker_version"] = docker_version

    broken_build = run_and_record(
        "broken-build",
        [
            docker,
            "build",
            "-f",
            str(BROKEN_DOCKERFILE.relative_to(PACKAGE_ROOT)),
            "-t",
            args.broken_tag,
            ".",
        ],
        PACKAGE_ROOT,
        evidence_dir,
        args.timeout_seconds,
    )
    broken_build["expected_failure_observed"] = (
        broken_build["exit_code"] is not None and broken_build["exit_code"] != 0
    )
    broken_output = (
        (evidence_dir / "broken-build.stdout.log").read_text(encoding="utf-8")
        + "\n"
        + (evidence_dir / "broken-build.stderr.log").read_text(encoding="utf-8")
    ).lower()
    broken_build["expected_reason_observed"] = (
        "make: not found" in broken_output
        or "make: command not found" in broken_output
    )
    summary["stages"]["broken_build"] = broken_build

    reference_build = run_and_record(
        "reference-build",
        [
            docker,
            "build",
            "-f",
            str(REFERENCE_DOCKERFILE.relative_to(PACKAGE_ROOT)),
            "-t",
            args.reference_tag,
            ".",
        ],
        PACKAGE_ROOT,
        evidence_dir,
        args.timeout_seconds,
    )
    summary["stages"]["reference_build"] = reference_build

    if reference_build["exit_code"] == 0:
        inspect_result = run_and_record(
            "reference-image-inspect",
            [docker, "image", "inspect", args.reference_tag],
            PACKAGE_ROOT,
            evidence_dir,
            args.timeout_seconds,
        )
        summary["stages"]["image_inspect"] = inspect_result
        inspect_stdout = (evidence_dir / "reference-image-inspect.stdout.log").read_text(
            encoding="utf-8"
        )
        summary["image"] = parse_image_inspect(inspect_stdout)

        compiler_version = run_and_record(
            "reference-compiler-version",
            [
                docker,
                "run",
                "--rm",
                "--network",
                "none",
                "--entrypoint",
                "gcc",
                args.reference_tag,
                "--version",
            ],
            PACKAGE_ROOT,
            evidence_dir,
            args.timeout_seconds,
        )
        summary["stages"]["compiler_version"] = compiler_version

        make_version = run_and_record(
            "reference-make-version",
            [
                docker,
                "run",
                "--rm",
                "--network",
                "none",
                "--entrypoint",
                "make",
                args.reference_tag,
                "--version",
            ],
            PACKAGE_ROOT,
            evidence_dir,
            args.timeout_seconds,
        )
        summary["stages"]["make_version"] = make_version

        artifact_check = run_and_record(
            "reference-artifact-check",
            [
                docker,
                "run",
                "--rm",
                "--network",
                "none",
                "--entrypoint",
                "/bin/sh",
                args.reference_tag,
                "-c",
                "test -x /work/hello && ls -l /work/hello",
            ],
            PACKAGE_ROOT,
            evidence_dir,
            args.timeout_seconds,
        )
        artifact_check["executable"] = artifact_check["exit_code"] == 0
        summary["stages"]["artifact_check"] = artifact_check

        verify = run_and_record(
            "reference-verify",
            [docker, "run", "--rm", "--network", "none", args.reference_tag],
            PACKAGE_ROOT,
            evidence_dir,
            args.timeout_seconds,
        )
        actual_stdout = (evidence_dir / "reference-verify.stdout.log").read_text(
            encoding="utf-8"
        )
        verify["stdout_exact_match"] = actual_stdout == EXPECTED_STDOUT
        summary["stages"]["verify"] = verify
    else:
        summary["stages"]["image_inspect"] = {"skipped": "reference build failed"}
        summary["stages"]["compiler_version"] = {"skipped": "reference build failed"}
        summary["stages"]["make_version"] = {"skipped": "reference build failed"}
        summary["stages"]["artifact_check"] = {"skipped": "reference build failed"}
        summary["stages"]["verify"] = {"skipped": "reference build failed"}

    verify_stage = summary["stages"]["verify"]
    inspect_stage = summary["stages"]["image_inspect"]
    compiler_stage = summary["stages"]["compiler_version"]
    make_stage = summary["stages"]["make_version"]
    artifact_stage = summary["stages"]["artifact_check"]
    accepted = (
        bool(broken_build["expected_failure_observed"])
        and bool(broken_build["expected_reason_observed"])
        and reference_build["exit_code"] == 0
        and inspect_stage.get("exit_code") == 0
        and bool(summary.get("image", {}).get("image_id"))
        and compiler_stage.get("exit_code") == 0
        and make_stage.get("exit_code") == 0
        and artifact_stage.get("executable") is True
        and verify_stage.get("exit_code") == 0
        and verify_stage.get("stdout_exact_match") is True
    )
    summary["result"] = "ACCEPTED" if accepted else "REJECTED"
    summary_path = evidence_dir / "summary.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Evidence: {evidence_dir}")
    print(f"Result: {summary['result']}")
    return 0 if accepted else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate reproducible DRAFT failure and success records."
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="validate project inputs and Dockerfile presence without invoking Docker",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="new evidence directory; existing directories are never overwritten",
    )
    parser.add_argument(
        "--broken-tag",
        default="e3-draft-tiny-greeting:broken",
    )
    parser.add_argument(
        "--reference-tag",
        default="e3-draft-tiny-greeting:reference",
    )
    parser.add_argument(
        "--timeout-seconds",
        type=int,
        default=900,
        help="timeout for each Docker command",
    )
    args = parser.parse_args()
    if args.timeout_seconds <= 0:
        parser.error("--timeout-seconds must be positive")
    return args


def main() -> int:
    args = parse_args()
    try:
        result = static_check()
        if args.check_only:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        return run_docker(args, result)
    except (FileExistsError, OSError, ValueError, json.JSONDecodeError) as error:
        print(f"validation error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
