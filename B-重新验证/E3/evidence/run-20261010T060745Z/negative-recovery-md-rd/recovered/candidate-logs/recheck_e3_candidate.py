"""Recheck one E3 B2 candidate workspace after the generic B4 stages pass."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


TARGET = "main.o"
INCLUDE_RE = re.compile(r'^\s*#\s*include\s+"([^"]+)"')


@dataclass(frozen=True)
class CaseSpec:
    name: str
    selected_finding_id: str
    selected_dependency: str
    header_before: str
    header_after: str
    expected_stdout: str
    known_redundant: dict[str, str]


CASES = {
    "md-rd": CaseSpec(
        name="md-rd",
        selected_finding_id="finding-e3-md-rd-missing-001",
        selected_dependency="config.h",
        header_before="#define VALUE 1",
        header_after="#define VALUE 2",
        expected_stdout="2\n",
        known_redundant={"unused.h": "finding-e3-md-rd-redundant-001"},
    ),
    "c1": CaseSpec(
        name="c1",
        selected_finding_id="finding-e3-c1-missing-001",
        selected_dependency="feature.h",
        header_before="#define FEATURE 2",
        header_after="#define FEATURE 3",
        expected_stdout="13\n",
        known_redundant={},
    ),
}


class RecheckExecutionError(RuntimeError):
    """Raised when a candidate cannot be rebuilt and probed safely."""


def _quoted_includes(project: Path) -> set[str]:
    queue = [project / "main.c"]
    seen: set[Path] = set()
    includes: set[str] = set()
    while queue:
        path = queue.pop()
        if path in seen or not path.is_file():
            continue
        seen.add(path)
        for line in path.read_text(encoding="utf-8").splitlines():
            match = INCLUDE_RE.match(line)
            if not match:
                continue
            header = match.group(1)
            includes.add(header)
            queue.append(project / header)
    return includes


def _declared_prereqs(makefile: Path) -> list[str]:
    for line in makefile.read_text(encoding="utf-8").splitlines():
        if line.startswith(f"{TARGET}:"):
            return [item for item in line.split(":", 1)[1].split() if item]
    raise RecheckExecutionError(f"{makefile} has no {TARGET} rule")


def _run(command: list[str], workspace: Path) -> dict[str, object]:
    completed = subprocess.run(
        command,
        cwd=workspace,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    return {
        "command": command,
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _require_success(record: dict[str, object], description: str) -> None:
    if record["exit_code"] != 0:
        raise RecheckExecutionError(
            f"{description} exited with {record['exit_code']}: {record['stderr']}"
        )


def _mark_newer_than(path: Path, reference: Path) -> None:
    """Make ``path`` newer than ``reference`` without setting it in the future."""

    reference_mtime = reference.stat().st_mtime
    deadline = time.monotonic() + 2
    while True:
        now = time.time()
        if now > reference_mtime:
            os.utime(path, (now, now))
            if path.stat().st_mtime > reference_mtime:
                return
        if time.monotonic() >= deadline:
            raise RecheckExecutionError(
                f"could not make {path.name} newer than {reference.name} without clock skew"
            )
        time.sleep(0.01)


def _run_incremental_probe(spec: CaseSpec, workspace: Path) -> dict[str, object]:
    clean = _run(["make", "clean"], workspace)
    _require_success(clean, "clean")
    build = _run(["make"], workspace)
    _require_success(build, "build")
    baseline = _run(["./app"], workspace)
    _require_success(baseline, "baseline application")

    header_path = workspace / spec.selected_dependency
    header_text = header_path.read_text(encoding="utf-8")
    if spec.header_before not in header_text:
        raise RecheckExecutionError(
            f"{spec.selected_dependency} does not contain expected baseline value"
        )
    header_path.write_text(
        header_text.replace(spec.header_before, spec.header_after, 1), encoding="utf-8"
    )
    object_path = workspace / TARGET
    if not object_path.is_file():
        raise RecheckExecutionError(f"build did not create {TARGET}")
    _mark_newer_than(header_path, object_path)

    incremental_make = _run(["make"], workspace)
    _require_success(incremental_make, "incremental build")
    incremental_app = _run(["./app"], workspace)
    _require_success(incremental_app, "incremental application")
    observed_stdout = str(incremental_app["stdout"])
    return {
        "passed": observed_stdout == spec.expected_stdout,
        "expected_stdout": spec.expected_stdout,
        "observed_stdout": observed_stdout,
        "clean": clean,
        "build": build,
        "baseline": baseline,
        "incremental_make": incremental_make,
        "incremental_app": incremental_app,
    }


def _finding_id(spec: CaseSpec, finding_type: str, dependency: str) -> str:
    if finding_type == "MISSING" and dependency == spec.selected_dependency:
        return spec.selected_finding_id
    if finding_type == "REDUNDANT" and dependency in spec.known_redundant:
        return spec.known_redundant[dependency]
    return f"finding-e3-{spec.name}-{finding_type.lower()}-{dependency.replace('.', '-')}"


def recheck_candidate(
    case_name: str, workspace: Path, output_path: Path | None = None
) -> dict[str, object]:
    """Analyze and behaviorally probe one already-built E3 candidate workspace."""

    try:
        spec = CASES[case_name]
    except KeyError as exc:
        raise RecheckExecutionError(f"unknown E3 candidate case: {case_name}") from exc
    workspace = Path(workspace).resolve()
    if not workspace.is_dir():
        raise RecheckExecutionError(f"candidate workspace does not exist: {workspace}")

    declared = sorted(_declared_prereqs(workspace / "Makefile"))
    actual = sorted({"main.c", *_quoted_includes(workspace)})
    missing = sorted(set(actual) - set(declared))
    redundant = sorted(set(declared) - set(actual))
    findings = [
        {
            "finding_id": _finding_id(spec, "MISSING", dependency),
            "type": "MISSING",
            "target": TARGET,
            "dependency": dependency,
        }
        for dependency in missing
    ] + [
        {
            "finding_id": _finding_id(spec, "REDUNDANT", dependency),
            "type": "REDUNDANT",
            "target": TARGET,
            "dependency": dependency,
        }
        for dependency in redundant
    ]
    findings.sort(key=lambda item: str(item["finding_id"]))
    incremental_probe = _run_incremental_probe(spec, workspace)
    if not incremental_probe["passed"]:
        raise RecheckExecutionError(
            "incremental application output was "
            f"{incremental_probe['observed_stdout']!r}; expected "
            f"{incremental_probe['expected_stdout']!r}"
        )

    report: dict[str, object] = {
        "schema_version": "2.0",
        "case": spec.name,
        "target": TARGET,
        "selected_finding_id": spec.selected_finding_id,
        "declared_prerequisites": declared,
        "actual_dependencies": actual,
        "findings": findings,
        "remaining_selected_findings": [
            finding["finding_id"]
            for finding in findings
            if finding["finding_id"] == spec.selected_finding_id
        ],
        "incremental_probe": incremental_probe,
    }
    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    return report


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=sorted(CASES), required=True)
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        recheck_candidate(args.case, args.workspace, args.output)
    except (OSError, RecheckExecutionError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
