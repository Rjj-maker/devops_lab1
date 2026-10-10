#!/usr/bin/env python3
"""BuildChecker E3 baseline: check fixtures, run Make behaviors, emit graphs and reports.

Uses only the Python standard library. Never deletes previous evidence directories
or original fixtures. All builds run in a fresh work copy.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shlex
import shutil
import stat
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


SCRIPT_DIR = Path(__file__).resolve().parent
PACKAGE_ROOT = SCRIPT_DIR.parent
REPO_ROOT = PACKAGE_ROOT.parent
FIXTURES = PACKAGE_ROOT / "fixtures"
ORACLE = PACKAGE_ROOT / "oracle"
EVIDENCE = PACKAGE_ROOT / "evidence"
REPO_URL = "https://github.com/Rowan-hhh/devops_lab1.git"
PAIR_ID = "pair03"
GIT_DATE = "2026-09-10T00:00:00Z"
INCLUDE_RE = re.compile(r'^\s*#\s*include\s+"([^"]+)"')
TARGET = "main.o"
TEXT_NAMES = {"Makefile", "README.md", "interface.json"}
TEXT_SUFFIXES = {".c", ".h", ".md", ".json", ".txt"}


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def is_text_file(path: Path) -> bool:
    return path.name in TEXT_NAMES or path.suffix in TEXT_SUFFIXES


def copy_tree_lf(src: Path, dst: Path) -> None:
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            copy_tree_lf(item, target)
            continue
        data = item.read_bytes()
        if is_text_file(item):
            text = data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
            target.write_bytes(text.encode("utf-8"))
        else:
            target.write_bytes(data)


def display_command(command: list[str]) -> str:
    return shlex.join(command)


def run_and_record(
    name: str,
    command: list[str],
    cwd: Path,
    evidence_dir: Path,
    timeout_seconds: int = 60,
    env: dict[str, str] | None = None,
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
            env=env,
        )
        exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr
    except FileNotFoundError as error:
        exit_code = 127
        stdout = ""
        stderr = str(error)
    except subprocess.TimeoutExpired as error:
        timed_out = True
        exit_code = None
        stdout = error.stdout.decode("utf-8", "replace") if isinstance(error.stdout, bytes) else (error.stdout or "")
        stderr = error.stderr.decode("utf-8", "replace") if isinstance(error.stderr, bytes) else (error.stderr or "")
        stderr += f"\ncommand timed out after {timeout_seconds} seconds\n"

    evidence_dir.mkdir(parents=True, exist_ok=True)
    (evidence_dir / f"{name}.command.txt").write_text(
        f"cwd={cwd}\ncommand={display_command(command)}\n", encoding="utf-8"
    )
    (evidence_dir / f"{name}.stdout.log").write_text(stdout, encoding="utf-8")
    (evidence_dir / f"{name}.stderr.log").write_text(stderr, encoding="utf-8")
    (evidence_dir / f"{name}.exit-code.txt").write_text(
        "" if exit_code is None else str(exit_code), encoding="utf-8"
    )
    return {
        "name": name,
        "command": command,
        "cwd": str(cwd),
        "exit_code": exit_code,
        "stdout": stdout,
        "stderr": stderr,
        "timed_out": timed_out,
        "started_at": started_at,
        "finished_at": utc_now(),
    }


def git_env() -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "GIT_AUTHOR_NAME": "e3-buildchecker-baseline",
            "GIT_AUTHOR_EMAIL": "e3-buildchecker@localhost",
            "GIT_AUTHOR_DATE": GIT_DATE,
            "GIT_COMMITTER_NAME": "e3-buildchecker-baseline",
            "GIT_COMMITTER_EMAIL": "e3-buildchecker@localhost",
            "GIT_COMMITTER_DATE": GIT_DATE,
        }
    )
    return env


def quoted_includes(project: Path) -> set[str]:
    queue = [project / "main.c"]
    seen_files: set[Path] = set()
    headers: set[str] = set()
    while queue:
        path = queue.pop()
        if path in seen_files or not path.is_file():
            continue
        seen_files.add(path)
        for line in path.read_text(encoding="utf-8").splitlines():
            match = INCLUDE_RE.match(line)
            if not match:
                continue
            name = match.group(1)
            headers.add(name)
            queue.append(project / name)
    return headers


def declared_prereqs(makefile: Path) -> tuple[list[str], int]:
    lines = makefile.read_text(encoding="utf-8").splitlines()
    for index, line in enumerate(lines, start=1):
        if line.startswith(f"{TARGET}:"):
            rest = line.split(":", 1)[1].strip()
            return [item for item in rest.split() if item], index
    raise ValueError(f"{makefile} has no {TARGET} rule")


def makefile_cflags(makefile: Path) -> str:
    for line in makefile.read_text(encoding="utf-8").splitlines():
        if line.startswith("CFLAGS"):
            return line.split("=", 1)[1].strip()
    return ""


def analyze_project(project: Path) -> dict[str, Any]:
    declared, location_line = declared_prereqs(project / "Makefile")
    actual_headers = quoted_includes(project)
    actual = sorted({"main.c", *actual_headers})
    declared_sorted = sorted(declared)
    missing = sorted(set(actual) - set(declared))
    redundant = sorted(set(declared) - set(actual))
    return {
        "target": TARGET,
        "cflags": makefile_cflags(project / "Makefile"),
        "declared": declared_sorted,
        "actual": actual,
        "missing": missing,
        "redundant": redundant,
        "location_line": location_line,
    }


def finding_tuple(items: list[dict[str, str]]) -> list[tuple[str, str, str]]:
    return sorted((item["type"], item["target"], item["dependency"]) for item in items)


def analysis_to_findings(analysis: dict[str, Any]) -> list[tuple[str, str, str]]:
    findings: list[tuple[str, str, str]] = []
    for dependency in analysis["missing"]:
        findings.append(("MISSING", TARGET, dependency))
    for dependency in analysis["redundant"]:
        findings.append(("REDUNDANT", TARGET, dependency))
    return sorted(findings)


def graph_payload(
    graph_type: str,
    commit: str,
    configuration_id: str,
    analysis: dict[str, Any],
    kind: str,
) -> dict[str, Any]:
    names = [TARGET, *analysis[kind]]
    nodes = []
    for name in names:
        if name == TARGET:
            node_kind = "object"
        elif name.endswith(".c"):
            node_kind = "source"
        else:
            node_kind = "header"
        nodes.append({"id": name, "kind": node_kind})
    edges = [{"from": TARGET, "to": name, "kind": "prerequisite"} for name in analysis[kind]]
    return {
        "schema_version": "2.0",
        "graph_type": graph_type,
        "scope": "project-headers-of-main.o",
        "target": TARGET,
        "configuration_id": configuration_id,
        "commit": commit,
        "nodes": nodes,
        "edges": edges,
        "cflags": analysis["cflags"],
    }


def error_report(
    job_id: str,
    commit: str,
    configuration_id: str,
    analysis: dict[str, Any],
    location_file: str,
    finding_prefix: str,
) -> dict[str, Any]:
    findings = []
    for index, dependency in enumerate(analysis["missing"], start=1):
        findings.append(
            {
                "finding_id": f"{finding_prefix}-missing-{index:03d}",
                "type": "MISSING",
                "target": TARGET,
                "dependency": dependency,
                "commit": commit,
                "location": {"file": location_file, "line": analysis["location_line"], "column": 1},
                "evidence": {
                    "summary": f"{TARGET} reads {dependency}, but Makefile does not declare it.",
                    "process": "quoted-include vs makefile-prereq",
                    "observed_file": dependency,
                    "declaration_file": "Makefile",
                },
                "detector": "INSTRUCTOR_ORACLE",
            }
        )
    for index, dependency in enumerate(analysis["redundant"], start=1):
        findings.append(
            {
                "finding_id": f"{finding_prefix}-redundant-{index:03d}",
                "type": "REDUNDANT",
                "target": TARGET,
                "dependency": dependency,
                "commit": commit,
                "location": {"file": location_file, "line": analysis["location_line"], "column": 1},
                "evidence": {
                    "summary": f"Makefile declares {dependency} for {TARGET}, but the translation unit does not include it.",
                    "process": "quoted-include vs makefile-prereq",
                    "observed_file": "main.c",
                    "declaration_file": "Makefile",
                },
                "detector": "INSTRUCTOR_ORACLE",
            }
        )
    return {
        "schema_version": "2.0",
        "report_type": "ERROR_REPORT",
        "producer_job_id": job_id,
        "repository": {"url": REPO_URL, "commit": commit},
        "configuration_id": configuration_id,
        "findings": findings,
    }


def write_analysis_artifacts(
    output_dir: Path,
    job_id: str,
    commit: str,
    configuration_id: str,
    analysis: dict[str, Any],
    location_file: str,
    finding_prefix: str,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    declared = graph_payload("DECLARED_GRAPH", commit, configuration_id, analysis, "declared")
    actual = graph_payload("ACTUAL_GRAPH", commit, configuration_id, analysis, "actual")
    report = error_report(job_id, commit, configuration_id, analysis, location_file, finding_prefix)
    write_json(output_dir / "declared.json", declared)
    write_json(output_dir / "actual.json", actual)
    write_json(output_dir / "error-report.json", report)
    write_json(output_dir / "analysis.json", analysis)
    return {
        "declared_sha256": sha256_file(output_dir / "declared.json"),
        "actual_sha256": sha256_file(output_dir / "actual.json"),
        "error_report_sha256": sha256_file(output_dir / "error-report.json"),
        "missing_count": len(analysis["missing"]),
        "redundant_count": len(analysis["redundant"]),
        "job_id": job_id,
        "commit": commit,
        "uri_prefix": f"artifact://{PAIR_ID}/{job_id}",
    }


def load_expected(name: str) -> list[tuple[str, str, str]]:
    payload = json.loads((ORACLE / name / "expected-findings.json").read_text(encoding="utf-8"))
    return finding_tuple(payload["findings"])


def git_sha(repo: Path) -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return completed.stdout.strip()


def init_git_repo(repo: Path) -> None:
    if repo.exists():
        shutil.rmtree(repo)
    repo.mkdir(parents=True)
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "--local", "user.name", "e3-buildchecker-baseline"], cwd=repo, check=True)
    subprocess.run(
        ["git", "config", "--local", "user.email", "e3-buildchecker@localhost"],
        cwd=repo,
        check=True,
    )


def commit_snapshot(repo: Path, source: Path, message: str, tag: str) -> str:
    for item in list(repo.iterdir()):
        if item.name == ".git":
            continue
        if item.is_dir():
            shutil.rmtree(item)
        else:
            item.unlink()
    for item in source.iterdir():
        if item.name == "interface.json":
            continue
        target = repo / item.name
        if item.is_file() and is_text_file(item):
            text = item.read_text(encoding="utf-8").replace("\r\n", "\n").replace("\r", "\n")
            target.write_bytes(text.encode("utf-8"))
        elif item.is_file():
            shutil.copy2(item, target)
    subprocess.run(["git", "add", "-A"], cwd=repo, check=True, capture_output=True, env=git_env())
    subprocess.run(["git", "commit", "-m", message], cwd=repo, check=True, capture_output=True, env=git_env())
    subprocess.run(["git", "tag", "-f", tag], cwd=repo, check=True, capture_output=True, env=git_env())
    return git_sha(repo)


def newer_than(path: Path, reference: Path, seconds: int = 2) -> None:
    stamp = reference.stat().st_mtime + seconds
    os.utime(path, (stamp, stamp))


def older_than(path: Path, reference: Path, seconds: int = 2) -> None:
    stamp = reference.stat().st_mtime - seconds
    os.utime(path, (stamp, stamp))


def make_executable(path: Path) -> bool:
    if not path.is_file():
        return False
    mode = path.stat().st_mode
    return bool(mode & (stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH))


def static_check() -> dict[str, Any]:
    required = [
        FIXTURES / "md-rd" / "main.c",
        FIXTURES / "md-rd" / "config.h",
        FIXTURES / "md-rd" / "unused.h",
        FIXTURES / "md-rd" / "Makefile",
        FIXTURES / "md-rd" / "README.md",
        FIXTURES / "md-rd" / "interface.json",
        FIXTURES / "commits" / "C0" / "main.c",
        FIXTURES / "commits" / "C0" / "config.h",
        FIXTURES / "commits" / "C0" / "Makefile",
        FIXTURES / "commits" / "C1" / "feature.h",
        FIXTURES / "commits" / "C2" / "Makefile",
        ORACLE / "md-rd" / "expected-findings.json",
        ORACLE / "C0" / "expected-findings.json",
        ORACLE / "C1" / "expected-findings.json",
        ORACLE / "C2" / "expected-findings.json",
        ORACLE / "C0-to-C1" / "expected-delta.json",
        ORACLE / "C1-to-C2" / "expected-delta.json",
    ]
    missing = [str(path.relative_to(PACKAGE_ROOT)).replace("\\", "/") for path in required if not path.is_file()]
    makefile = (FIXTURES / "md-rd" / "Makefile").read_bytes()
    tab_ok = b"\n\t$(CC)" in makefile or b"\n\t" in makefile
    interfaces = {}
    for name, relative, stdout in [
        ("md-rd", "md-rd", "1\n"),
        ("C0", "commits/C0", "10\n"),
        ("C1", "commits/C1", "12\n"),
        ("C2", "commits/C2", "19\n"),
    ]:
        payload = json.loads((FIXTURES / relative / "interface.json").read_text(encoding="utf-8"))
        interfaces[name] = {
            "build_command": payload.get("build", {}).get("command") == "make",
            "verify_command": payload.get("verify", {}).get("command") == "./app",
            "stdout": payload.get("verify", {}).get("stdout") == stdout,
        }
    failed_interface = {
        name: checks for name, checks in interfaces.items() if not all(checks.values())
    }
    md_rd = analyze_project(FIXTURES / "md-rd")
    c0 = analyze_project(FIXTURES / "commits" / "C0")
    c1 = analyze_project(FIXTURES / "commits" / "C1")
    c2 = analyze_project(FIXTURES / "commits" / "C2")
    oracle_ok = {
        "md-rd": analysis_to_findings(md_rd) == load_expected("md-rd"),
        "C0": analysis_to_findings(c0) == load_expected("C0"),
        "C1": analysis_to_findings(c1) == load_expected("C1"),
        "C2": analysis_to_findings(c2) == load_expected("C2"),
    }
    status = "PASSED"
    problems = []
    if missing:
        problems.append(f"missing files: {missing}")
    if not tab_ok:
        problems.append("md-rd Makefile recipes do not use TAB")
    if failed_interface:
        problems.append(f"interface mismatch: {failed_interface}")
    if not all(oracle_ok.values()):
        problems.append(f"oracle mismatch: {oracle_ok}")
    if problems:
        status = "FAILED"
    return {
        "status": status,
        "checked_at": utc_now(),
        "problems": problems,
        "oracle_ok": oracle_ok,
        "interfaces": interfaces,
        "source_sha256": {
            str(path.relative_to(PACKAGE_ROOT)).replace("\\", "/"): sha256_file(path)
            for path in required
            if path.is_file()
        },
    }


def record_versions(evidence_dir: Path) -> dict[str, Any]:
    versions = {}
    for name, command in [
        ("make-version", ["make", "--version"]),
        ("cc-version", ["cc", "--version"]),
        ("git-version", ["git", "--version"]),
        ("python-version", [sys.executable, "--version"]),
    ]:
        versions[name] = run_and_record(name, command, PACKAGE_ROOT, evidence_dir / "env", 30)
    strace = shutil.which("strace")
    versions["strace"] = strace
    if strace:
        versions["strace-version"] = run_and_record(
            "strace-version", ["strace", "--version"], PACKAGE_ROOT, evidence_dir / "env", 30
        )
    return versions


def run_md_rd(
    work_root: Path, evidence_dir: Path, report_commit: Optional[str] = None
) -> dict[str, Any]:
    work = work_root / "md-rd"
    copy_tree_lf(FIXTURES / "md-rd", work)
    logs = evidence_dir / "md-rd"
    logs.mkdir(parents=True, exist_ok=True)
    md_repo = work_root / "md-rd-repo"
    init_git_repo(md_repo)
    snapshot_commit = commit_snapshot(
        md_repo,
        FIXTURES / "md-rd",
        "md-rd: missing config.h and redundant unused.h",
        "md-rd",
    )
    # The generated bundle commit is useful for isolated B2 reproduction, but it
    # is not fetchable from the shared repository. E3 environment-binding runs
    # may publish analysis artifacts against the ordinary repository commit.
    commit = report_commit or snapshot_commit
    (logs / "md-rd.sha").write_text(snapshot_commit + "\n", encoding="utf-8")
    (logs / "repository-commit.sha").write_text(commit + "\n", encoding="utf-8")
    subprocess.run(
        ["git", "bundle", "create", str((logs / "md-rd.bundle").resolve()), "--all"],
        cwd=md_repo,
        check=True,
        capture_output=True,
    )
    clean = run_and_record("clean-build", ["make", "clean"], work, logs)
    build = run_and_record("build", ["make"], work, logs)
    verify = run_and_record("verify", ["./app"], work, logs)
    config_h = work / "config.h"
    config_h.write_text(
        config_h.read_text(encoding="utf-8").replace("#define VALUE 1", "#define VALUE 2"),
        encoding="utf-8",
    )
    newer_than(config_h, work / "main.o")
    older_than(work / "app", work / "main.o")
    incremental = run_and_record("md-incremental", ["make"], work, logs)
    md_verify = run_and_record("md-incremental-verify", ["./app"], work, logs)
    rebuild = run_and_record("md-clean-rebuild", ["make", "clean"], work, logs)
    rebuild_make = run_and_record("md-clean-build", ["make"], work, logs)
    rebuild_verify = run_and_record("md-clean-verify", ["./app"], work, logs)

    copy_tree_lf(FIXTURES / "md-rd", work)
    run_and_record("rd-prep-clean", ["make", "clean"], work, logs)
    run_and_record("rd-prep-build", ["make"], work, logs)
    unused = work / "unused.h"
    unused.write_text(
        unused.read_text(encoding="utf-8").replace(
            "/* Declared by Makefile but not included by main.c. */",
            "/* Declared by Makefile but not included by main.c. still unused */",
        ),
        encoding="utf-8",
    )
    newer_than(unused, work / "main.o")
    rd_make = run_and_record("rd-incremental", ["make"], work, logs)

    analysis = analyze_project(FIXTURES / "md-rd")
    analysis_job_id = (
        "job-e3-a-md-rd-001"
        if report_commit is None
        else f"job-e3-a-md-rd-{report_commit[:8]}"
    )
    artifacts = write_analysis_artifacts(
        logs / "artifacts",
        analysis_job_id,
        commit,
        "cc-default",
        analysis,
        "A-BuildChecker-E3测试基线/fixtures/md-rd/Makefile",
        "finding-e3-md-rd",
    )
    strace_ok = None
    if shutil.which("strace"):
        copy_tree_lf(FIXTURES / "md-rd", work)
        run_and_record("strace-clean", ["make", "clean"], work, logs)
        strace_run = run_and_record(
            "strace-make",
            ["strace", "-ff", "-o", str(logs / "trace.log"), "-e", "trace=%file,%process", "make"],
            work,
            logs,
            timeout_seconds=60,
        )
        traces = list(logs.glob("trace.log*"))
        combined = ""
        for path in traces:
            combined += path.read_text(encoding="utf-8", errors="replace")
        strace_ok = "config.h" in combined
        (logs / "strace-config.h.grep.txt").write_text(
            "\n".join(line for line in combined.splitlines() if "config.h" in line) + "\n",
            encoding="utf-8",
        )
        artifacts["strace"] = {"exit_code": strace_run["exit_code"], "saw_config_h": strace_ok}

    checks = {
        "clean_build": build["exit_code"] == 0 and verify["exit_code"] == 0 and verify["stdout"] == "1\n",
        "md_stale": md_verify["stdout"] == "1\n",
        "md_clean": rebuild_verify["stdout"] == "2\n",
        "rd_rebuild": "main.c" in rd_make["stdout"] or "-c" in rd_make["stdout"],
        "oracle": analysis_to_findings(analysis) == load_expected("md-rd"),
        "app_executable": make_executable(work / "app") or rebuild_verify["exit_code"] == 0,
    }
    return {
        "commit": commit,
        "snapshot_commit": snapshot_commit,
        "checks": checks,
        "artifacts": artifacts,
        "commands": {
            "clean": clean["exit_code"],
            "build": build["exit_code"],
            "verify": verify["stdout"],
            "md_incremental": md_verify["stdout"],
            "md_clean": rebuild_verify["stdout"],
            "rd_stdout": rd_make["stdout"],
        },
        "strace_saw_config_h": strace_ok,
        "passed": all(checks.values()),
        "rebuild_log_exit": rebuild["exit_code"],
        "rebuild_make_exit": rebuild_make["exit_code"],
    }


def run_commits(work_root: Path, evidence_dir: Path) -> dict[str, Any]:
    repo = work_root / "commits-repo"
    logs = evidence_dir / "commits"
    logs.mkdir(parents=True, exist_ok=True)
    init_git_repo(repo)
    sha_c0 = commit_snapshot(repo, FIXTURES / "commits" / "C0", "C0: correct header declarations", "C0")
    sha_c1 = commit_snapshot(repo, FIXTURES / "commits" / "C1", "C1: include feature.h without Makefile update", "C1")
    sha_c2 = commit_snapshot(repo, FIXTURES / "commits" / "C2", "C2: change compile command to -DMODE=7", "C2")
    (logs / "C0.sha").write_text(sha_c0 + "\n", encoding="utf-8")
    (logs / "C1.sha").write_text(sha_c1 + "\n", encoding="utf-8")
    (logs / "C2.sha").write_text(sha_c2 + "\n", encoding="utf-8")
    log = run_and_record("git-log", ["git", "log", "--oneline", "--decorate"], repo, logs)
    subprocess.run(
        ["git", "bundle", "create", str((logs / "commits.bundle").resolve()), "--all"],
        cwd=repo,
        check=True,
        capture_output=True,
    )

    results = {}
    for label, sha, configuration_id, job_id, finding_prefix, expected_stdout in [
        ("C0", sha_c0, "cc-MODE0", "job-e3-a-c0-001", "finding-e3-c0", "10\n"),
        ("C1", sha_c1, "cc-MODE0", "job-e3-a-c1-001", "finding-e3-c1", "12\n"),
        ("C2", sha_c2, "cc-MODE7", "job-e3-a-c2-001", "finding-e3-c2", "19\n"),
    ]:
        work = work_root / label
        copy_tree_lf(FIXTURES / "commits" / label, work)
        run_and_record(f"{label}-clean", ["make", "clean"], work, logs / label)
        build = run_and_record(f"{label}-build", ["make"], work, logs / label)
        verify = run_and_record(f"{label}-verify", ["./app"], work, logs / label)
        analysis = analyze_project(work)
        artifacts = write_analysis_artifacts(
            logs / label / "artifacts",
            job_id,
            sha,
            configuration_id,
            analysis,
            "Makefile",
            finding_prefix,
        )
        results[label] = {
            "sha": sha,
            "stdout": verify["stdout"],
            "exit_code": verify["exit_code"],
            "build_exit_code": build["exit_code"],
            "expected_stdout": expected_stdout,
            "oracle_ok": analysis_to_findings(analysis) == load_expected(label),
            "analysis": analysis,
            "artifacts": artifacts,
            "passed": verify["stdout"] == expected_stdout and verify["exit_code"] == 0,
        }

    c1_work = work_root / "C1"
    c2_inc = work_root / "C2-incremental"
    copy_tree_lf(FIXTURES / "commits" / "C2", c2_inc)
    shutil.copy2(c1_work / "main.o", c2_inc / "main.o")
    shutil.copy2(c1_work / "app", c2_inc / "app")
    # C2 sources were just copied, so they are newer than C1 objects. Keep the
    # C1 products and make them newer than sources so ordinary make only sees
    # timestamps, not the CFLAGS change.
    newer_than(c2_inc / "main.o", c2_inc / "main.c", seconds=5)
    newer_than(c2_inc / "app", c2_inc / "main.o", seconds=2)
    incremental = run_and_record("C2-incremental-make", ["make"], c2_inc, logs / "C2-incremental")
    inc_verify = run_and_record("C2-incremental-verify", ["./app"], c2_inc, logs / "C2-incremental")
    clean = run_and_record("C2-clean", ["make", "clean"], c2_inc, logs / "C2-incremental")
    clean_build = run_and_record("C2-clean-build", ["make"], c2_inc, logs / "C2-incremental")
    clean_verify = run_and_record("C2-clean-verify", ["./app"], c2_inc, logs / "C2-incremental")

    c1_findings = analysis_to_findings(results["C1"]["analysis"])
    c0_findings = analysis_to_findings(results["C0"]["analysis"])
    c2_findings = analysis_to_findings(results["C2"]["analysis"])
    delta_c0_c1 = {
        "from": "C0",
        "to": "C1",
        "from_commit": sha_c0,
        "to_commit": sha_c1,
        "introduced": [
            {"type": item[0], "target": item[1], "dependency": item[2]}
            for item in c1_findings
            if item not in c0_findings
        ],
        "resolved": [
            {"type": item[0], "target": item[1], "dependency": item[2]}
            for item in c0_findings
            if item not in c1_findings
        ],
        "unchanged": [
            {"type": item[0], "target": item[1], "dependency": item[2]}
            for item in c1_findings
            if item in c0_findings
        ],
    }
    delta_c1_c2 = {
        "from": "C1",
        "to": "C2",
        "from_commit": sha_c1,
        "to_commit": sha_c2,
        "introduced": [
            {"type": item[0], "target": item[1], "dependency": item[2]}
            for item in c2_findings
            if item not in c1_findings
        ],
        "resolved": [
            {"type": item[0], "target": item[1], "dependency": item[2]}
            for item in c1_findings
            if item not in c2_findings
        ],
        "unchanged": [
            {"type": item[0], "target": item[1], "dependency": item[2]}
            for item in c2_findings
            if item in c1_findings
        ],
        "command_change": {
            "from_cflags": results["C1"]["analysis"]["cflags"],
            "to_cflags": results["C2"]["analysis"]["cflags"],
            "incremental_stdout": inc_verify["stdout"],
            "clean_stdout": clean_verify["stdout"],
        },
    }
    write_json(logs / "c0-to-c1-delta.json", delta_c0_c1)
    write_json(logs / "c1-to-c2-delta.json", delta_c1_c2)
    expected_c0_c1 = json.loads((ORACLE / "C0-to-C1" / "expected-delta.json").read_text(encoding="utf-8"))
    expected_c1_c2 = json.loads((ORACLE / "C1-to-C2" / "expected-delta.json").read_text(encoding="utf-8"))
    delta_ok = finding_tuple(delta_c0_c1["introduced"]) == finding_tuple(
        expected_c0_c1["introduced"]
    ) and finding_tuple(delta_c1_c2["unchanged"]) == finding_tuple(expected_c1_c2["unchanged"])
    checks = {
        "C0": results["C0"]["passed"] and results["C0"]["oracle_ok"],
        "C1": results["C1"]["passed"] and results["C1"]["oracle_ok"],
        "C2_clean": results["C2"]["passed"] and results["C2"]["oracle_ok"],
        "C2_incremental": inc_verify["stdout"] == "12\n",
        "C2_clean_after_incremental": clean_verify["stdout"] == "19\n",
        "delta": delta_ok,
    }
    return {
        "shas": {"C0": sha_c0, "C1": sha_c1, "C2": sha_c2},
        "results": {
            label: {
                "sha": item["sha"],
                "stdout": item["stdout"],
                "passed": item["passed"],
                "oracle_ok": item["oracle_ok"],
                "artifacts": item["artifacts"],
            }
            for label, item in results.items()
        },
        "incremental": {
            "make_stdout": incremental["stdout"],
            "stdout": inc_verify["stdout"],
            "clean_stdout": clean_verify["stdout"],
            "clean_exit": clean["exit_code"],
            "clean_build_exit": clean_build["exit_code"],
        },
        "git_log": log["stdout"],
        "checks": checks,
        "passed": all(checks.values()),
    }


def current_repo_sha() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if completed.returncode != 0:
        return "0" * 40
    return completed.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description="Run A-group BuildChecker E3 baseline")
    parser.add_argument("--check-only", action="store_true")
    parser.add_argument(
        "--md-rd-report-commit",
        help="bind MD/RD report metadata to a reachable full repository commit",
    )
    parser.add_argument(
        "--environment-image-ref",
        help="record the image reference used for this E3 environment run",
    )
    args = parser.parse_args()

    check = static_check()
    if args.check_only:
        print(json.dumps(check, ensure_ascii=False, indent=2))
        return 0 if check["status"] == "PASSED" else 1
    if check["status"] != "PASSED":
        write_json(EVIDENCE / "last-static-check.json", check)
        print("static check failed", file=sys.stderr)
        print(json.dumps(check, ensure_ascii=False, indent=2))
        return 2

    if shutil.which("make") is None or shutil.which("cc") is None:
        print("make or cc not found; run this script on Linux/WSL with GNU Make and a C compiler", file=sys.stderr)
        return 2

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    evidence_dir = EVIDENCE / f"run-{stamp}"
    if evidence_dir.exists():
        raise SystemExit(f"evidence directory already exists: {evidence_dir}")
    evidence_dir.mkdir(parents=True)
    work_root = PACKAGE_ROOT / "work" / f"run-{stamp}"
    work_root.mkdir(parents=True, exist_ok=True)

    versions = record_versions(evidence_dir)
    repo_head = current_repo_sha()
    if args.md_rd_report_commit and args.md_rd_report_commit != repo_head:
        raise SystemExit(
            "--md-rd-report-commit must equal the checked-out repository HEAD "
            f"({repo_head}) so the report identifies the tested source tree"
        )
    md_rd = run_md_rd(work_root, evidence_dir, report_commit=args.md_rd_report_commit)
    commits = run_commits(work_root, evidence_dir)

    env_payload = {
        "os": platform.platform(),
        "python": sys.version,
        "cwd": str(PACKAGE_ROOT),
        "repo_head": repo_head,
        "machine": platform.machine(),
        "image_ref": args.environment_image_ref,
        "md_rd_project_root": "A-BuildChecker-E3测试基线/fixtures/md-rd",
    }
    write_json(evidence_dir / "env.json", env_payload)
    write_json(evidence_dir / "static-check.json", check)

    passed = md_rd["passed"] and commits["passed"]
    summary = {
        "result": "ACCEPTED" if passed else "REJECTED",
        "checked_at": utc_now(),
        "git_head": repo_head,
        "environment": env_payload,
        "md_rd": md_rd,
        "commits": commits,
        "tool_versions": {
            "make": versions["make-version"]["stdout"].splitlines()[0] if versions["make-version"]["stdout"] else "",
            "cc": versions["cc-version"]["stdout"].splitlines()[0] if versions["cc-version"]["stdout"] else "",
        },
        "notes": [
            "Graphs compare Makefile prerequisites of main.o with quoted project includes.",
            "System headers are out of scope.",
            "This is the E3 baseline analyzer, not a server-side FULL_CHECK API Job or the E5 BuildChecker service.",
            "MD/RD report commit identifies the shared repository tree; snapshot_commit identifies the standalone bundle used for reproduction.",
            "The environment image reference is recorded separately from any Registry delivery or DRAFT API receipt.",
        ],
    }
    write_json(evidence_dir / "summary.json", summary)
    print(f"EVIDENCE_DIR={evidence_dir}")
    print(f"result={summary['result']}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
