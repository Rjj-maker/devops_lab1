#!/usr/bin/env python3
"""Build, validate, and optionally export the B1 MD/RD Docker environment.

Only Python's standard library is used. Source fixtures are never modified and
existing evidence or image archives are never overwritten.
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
BASELINE_ROOT = RUNNER_DIR.parent
REPO_ROOT = BASELINE_ROOT.parent
FIXTURE_DIR = BASELINE_ROOT / "fixtures" / "md-rd"
INTERFACE_PATH = FIXTURE_DIR / "interface.json"
DOCKERFILE = RUNNER_DIR / "Dockerfile"
SOURCE_BASELINE_COMMIT = "29c02d6604d7071d4b249ec958dd8a553caa670a"
EXPECTED_STDOUT = "1\n"
REQUIRED_SOURCE_NAMES = (
    "main.c",
    "config.h",
    "unused.h",
    "Makefile",
    "README.md",
    "interface.json",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def source_matches_baseline_commit() -> bool | None:
    """Return None when Git or the baseline commit is unavailable."""
    git = shutil.which("git")
    if git is None:
        return None
    completed = subprocess.run(
        [
            git,
            "-c",
            f"safe.directory={REPO_ROOT}",
            "-c",
            "core.autocrlf=true",
            "diff",
            "--ignore-space-at-eol",
            "--quiet",
            SOURCE_BASELINE_COMMIT,
            "--",
            str(FIXTURE_DIR.relative_to(REPO_ROOT)),
        ],
        cwd=REPO_ROOT,
        capture_output=True,
        check=False,
    )
    if completed.returncode == 0:
        return True
    if completed.returncode == 1:
        return False
    return None


def static_check() -> dict[str, Any]:
    required_files = [FIXTURE_DIR / name for name in REQUIRED_SOURCE_NAMES]
    required_files.append(DOCKERFILE)
    missing = [str(path.relative_to(BASELINE_ROOT)) for path in required_files if not path.is_file()]
    if missing:
        raise ValueError(f"missing required files: {missing}")

    interface = json.loads(INTERFACE_PATH.read_text(encoding="utf-8"))
    checks = {
        "project_id": interface.get("project", {}).get("id") == "e3-buildchecker-md-rd",
        "project_root": interface.get("project", {}).get("project_root")
        == "A-BuildChecker-E3测试基线/fixtures/md-rd",
        "platform": interface.get("project", {}).get("platform") == "linux",
        "network_not_required": interface.get("project", {}).get("network_required") is False,
        "build_command": interface.get("build", {}).get("command") == "make",
        "build_exit_code": interface.get("build", {}).get("exit_code") == 0,
        "verify_command": interface.get("verify", {}).get("command") == "./app",
        "verify_exit_code": interface.get("verify", {}).get("exit_code") == 0,
        "verify_stdout": interface.get("verify", {}).get("stdout") == EXPECTED_STDOUT,
        "dockerfile_copies_fixed_source_set": "COPY main.c"
        in DOCKERFILE.read_text(encoding="utf-8"),
    }
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise ValueError(f"static check failed: {failed}")

    baseline_match = source_matches_baseline_commit()
    if baseline_match is False:
        raise ValueError(
            "fixtures/md-rd differs from source baseline commit "
            f"{SOURCE_BASELINE_COMMIT}"
        )

    return {
        "status": "PASSED",
        "checked_at": utc_now(),
        "source_baseline_commit": SOURCE_BASELINE_COMMIT,
        "source_matches_baseline_commit": baseline_match,
        "checks": checks,
        "source_sha256": {
            path.relative_to(BASELINE_ROOT).as_posix(): sha256_file(path)
            for path in required_files
        },
    }


def display_command(command: list[str]) -> str:
    return shlex.join(str(part) for part in command)


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
        stdout = error.stdout if isinstance(error.stdout, str) else ""
        stderr = error.stderr if isinstance(error.stderr, str) else ""
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


def read_stdout(evidence_dir: Path, name: str) -> str:
    return (evidence_dir / f"{name}.stdout.log").read_text(encoding="utf-8")


def last_nonempty_line(value: str) -> str | None:
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    return lines[-1] if lines else None


def parse_image_inspect(stdout: str) -> dict[str, Any]:
    try:
        value = json.loads(stdout)
    except json.JSONDecodeError:
        return {}
    if not isinstance(value, list) or not value or not isinstance(value[0], dict):
        return {}
    image = value[0]
    config = image.get("Config") if isinstance(image.get("Config"), dict) else {}
    return {
        "image_id": image.get("Id"),
        "repo_tags": image.get("RepoTags") or [],
        "repo_digests": image.get("RepoDigests") or [],
        "created": image.get("Created"),
        "architecture": image.get("Architecture"),
        "os": image.get("Os"),
        "labels": config.get("Labels") or {},
    }


def git_metadata() -> dict[str, Any]:
    git = shutil.which("git")
    if git is None:
        return {"sha": None, "dirty": None, "error": "Git CLI not found"}
    prefix = [
        git,
        "-c",
        f"safe.directory={REPO_ROOT}",
        "-c",
        "core.fileMode=false",
        "-c",
        "core.autocrlf=true",
    ]
    head = subprocess.run(
        [*prefix, "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    if head.returncode != 0:
        return {"sha": None, "dirty": None, "error": head.stderr.strip()}
    status = subprocess.run(
        [*prefix, "status", "--short"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
    )
    return {
        "sha": head.stdout.strip(),
        "status": status.stdout.splitlines() if status.returncode == 0 else None,
        "dirty": bool(status.stdout.strip()) if status.returncode == 0 else None,
    }


def docker_run_command(docker: str, tag: str, shell_command: str) -> list[str]:
    return [
        docker,
        "run",
        "--rm",
        "--network",
        "none",
        "--entrypoint",
        "/bin/sh",
        tag,
        "-c",
        shell_command,
    ]


def write_transfer_manifest(
    path: Path,
    tag: str,
    image: dict[str, Any],
    archive_path: Path | None,
) -> dict[str, Any]:
    archive = None
    if archive_path is not None:
        archive = {
            "file": archive_path.name,
            "size_bytes": archive_path.stat().st_size,
            "sha256": sha256_file(archive_path),
        }
    manifest = {
        "schema_version": "1.0",
        "generated_at": utc_now(),
        "project": "e3-buildchecker-md-rd@2026-09-10",
        "source_baseline_commit": SOURCE_BASELINE_COMMIT,
        "image_tag": tag,
        "image_id": image.get("image_id"),
        "repo_digests": image.get("repo_digests", []),
        "archive": archive,
        "import_command": f"docker load --input {archive_path.name}" if archive_path else None,
        "verify_command": f"docker run --rm --network none {tag}",
        "expected_stdout": EXPECTED_STDOUT,
    }
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def run_docker(args: argparse.Namespace, static_result: dict[str, Any]) -> int:
    docker = shutil.which("docker")
    if docker is None:
        print(
            "Docker CLI was not found. Static checks passed, but no runtime evidence was generated.",
            file=sys.stderr,
        )
        return 2

    run_id = datetime.now(timezone.utc).strftime("run-%Y%m%dT%H%M%SZ")
    evidence_dir = (args.output_dir or (RUNNER_DIR / "evidence" / run_id)).resolve()
    if evidence_dir.exists():
        raise FileExistsError(f"refusing to overwrite existing evidence directory: {evidence_dir}")
    evidence_dir.mkdir(parents=True)

    summary: dict[str, Any] = {
        "schema_version": "1.0",
        "run_id": run_id,
        "generated_at": utc_now(),
        "project": "e3-buildchecker-md-rd@2026-09-10",
        "source_baseline_commit": SOURCE_BASELINE_COMMIT,
        "git": git_metadata(),
        "host": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": sys.version,
        },
        "static_check": static_result,
        "expected": {
            "verify_stdout": EXPECTED_STDOUT,
            "md_stale_output": "1",
            "md_clean_rebuild_output": "2",
            "rd_change_recompiles_main": True,
        },
        "stages": {},
    }

    stages = summary["stages"]
    stages["docker_version"] = run_and_record(
        "docker-version", [docker, "version"], BASELINE_ROOT, evidence_dir, args.timeout_seconds
    )
    stages["image_build"] = run_and_record(
        "image-build",
        [
            docker,
            "build",
            *(["--pull"] if args.pull else []),
            "-f",
            str(DOCKERFILE.relative_to(BASELINE_ROOT)),
            "-t",
            args.image_tag,
            str(FIXTURE_DIR.relative_to(BASELINE_ROOT)),
        ],
        BASELINE_ROOT,
        evidence_dir,
        args.timeout_seconds,
    )

    image: dict[str, Any] = {}
    if stages["image_build"]["exit_code"] == 0:
        stages["image_inspect"] = run_and_record(
            "image-inspect",
            [docker, "image", "inspect", args.image_tag],
            BASELINE_ROOT,
            evidence_dir,
            args.timeout_seconds,
        )
        image = parse_image_inspect(read_stdout(evidence_dir, "image-inspect"))
        summary["image"] = image

        runtime_cases = {
            "verify": [docker, "run", "--rm", "--network", "none", args.image_tag],
            "compiler_version": docker_run_command(docker, args.image_tag, "gcc --version"),
            "make_version": docker_run_command(docker, args.image_tag, "make --version"),
            "source_check": docker_run_command(
                docker,
                args.image_tag,
                "test -x /work/app && test -f /work/main.c && test -f /work/config.h "
                "&& test -f /work/unused.h && test -f /work/Makefile",
            ),
            "md_stale": docker_run_command(
                docker,
                args.image_tag,
                "sed -i 's/#define VALUE 1/#define VALUE 2/' config.h && make && ./app",
            ),
            "md_clean_rebuild": docker_run_command(
                docker,
                args.image_tag,
                "sed -i 's/#define VALUE 1/#define VALUE 2/' config.h "
                "&& make clean && make && ./app",
            ),
            "rd_rebuild": docker_run_command(
                docker,
                args.image_tag,
                "sleep 1 && touch unused.h && make && ./app",
            ),
        }
        for name, command in runtime_cases.items():
            stages[name] = run_and_record(
                name, command, BASELINE_ROOT, evidence_dir, args.timeout_seconds
            )

        verify_stdout = read_stdout(evidence_dir, "verify")
        stages["verify"]["stdout_exact_match"] = verify_stdout == EXPECTED_STDOUT

        stale_stdout = read_stdout(evidence_dir, "md_stale")
        stages["md_stale"]["observed_output"] = last_nonempty_line(stale_stdout)
        stages["md_stale"]["main_recompiled"] = "main.c" in stale_stdout

        clean_stdout = read_stdout(evidence_dir, "md_clean_rebuild")
        stages["md_clean_rebuild"]["observed_output"] = last_nonempty_line(clean_stdout)
        stages["md_clean_rebuild"]["main_recompiled"] = "main.c" in clean_stdout

        rd_stdout = read_stdout(evidence_dir, "rd_rebuild")
        stages["rd_rebuild"]["observed_output"] = last_nonempty_line(rd_stdout)
        stages["rd_rebuild"]["main_recompiled"] = "main.c" in rd_stdout
    else:
        for name in (
            "image_inspect",
            "verify",
            "compiler_version",
            "make_version",
            "source_check",
            "md_stale",
            "md_clean_rebuild",
            "rd_rebuild",
        ):
            stages[name] = {"skipped": "image build failed"}

    accepted = (
        stages["docker_version"].get("exit_code") == 0
        and stages["image_build"].get("exit_code") == 0
        and stages["image_inspect"].get("exit_code") == 0
        and bool(image.get("image_id"))
        and image.get("os") == "linux"
        and image.get("labels", {}).get("org.opencontainers.image.revision")
        == SOURCE_BASELINE_COMMIT
        and image.get("labels", {}).get("dev.devops-lab.project")
        == "e3-buildchecker-md-rd@2026-09-10"
        and stages["verify"].get("exit_code") == 0
        and stages["verify"].get("stdout_exact_match") is True
        and stages["compiler_version"].get("exit_code") == 0
        and stages["make_version"].get("exit_code") == 0
        and stages["source_check"].get("exit_code") == 0
        and stages["md_stale"].get("exit_code") == 0
        and stages["md_stale"].get("observed_output") == "1"
        and stages["md_stale"].get("main_recompiled") is False
        and stages["md_clean_rebuild"].get("exit_code") == 0
        and stages["md_clean_rebuild"].get("observed_output") == "2"
        and stages["md_clean_rebuild"].get("main_recompiled") is True
        and stages["rd_rebuild"].get("exit_code") == 0
        and stages["rd_rebuild"].get("observed_output") == "1"
        and stages["rd_rebuild"].get("main_recompiled") is True
    )

    archive_path: Path | None = None
    if accepted and args.export_image is not None:
        archive_path = args.export_image.resolve()
        if archive_path.exists():
            raise FileExistsError(f"refusing to overwrite existing image archive: {archive_path}")
        archive_path.parent.mkdir(parents=True, exist_ok=True)
        stages["image_export"] = run_and_record(
            "image-export",
            [docker, "image", "save", "--output", str(archive_path), args.image_tag],
            BASELINE_ROOT,
            evidence_dir,
            args.timeout_seconds,
        )
        accepted = accepted and stages["image_export"].get("exit_code") == 0
        if not accepted:
            archive_path = None
    elif args.export_image is not None:
        stages["image_export"] = {"skipped": "runtime validation was not accepted"}

    transfer_manifest = write_transfer_manifest(
        evidence_dir / "transfer-manifest.json",
        args.image_tag,
        image,
        archive_path,
    )
    summary["transfer"] = transfer_manifest
    summary["result"] = "ACCEPTED" if accepted else "REJECTED"
    (evidence_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Evidence: {evidence_dir}")
    if archive_path is not None:
        print(f"Image archive: {archive_path}")
        print(f"Archive SHA-256: {transfer_manifest['archive']['sha256']}")
    print(f"Result: {summary['result']}")
    return 0 if accepted else 1


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and export the B1 environment for the E3 MD/RD fixture."
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="validate source inputs and Dockerfile without invoking Docker",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="new evidence directory; existing directories are never overwritten",
    )
    parser.add_argument(
        "--image-tag",
        default="e3-buildchecker-md-rd:b1-20260910",
    )
    parser.add_argument(
        "--pull",
        action="store_true",
        help="refresh the base image instead of preferring the local Docker cache",
    )
    parser.add_argument(
        "--export-image",
        type=Path,
        help="optional new .tar path for docker save; writes its SHA-256 to the manifest",
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
    if args.check_only and (args.output_dir is not None or args.export_image is not None):
        parser.error("--check-only cannot be combined with --output-dir or --export-image")
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
