"""Run the generic B4 flow against one independently supplied E3 candidate bundle."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


B4_ROOT = Path(__file__).resolve().parents[2]
GENERIC_TOOL_DIR = B4_ROOT / "tools"
E3_TOOL_DIR = Path(__file__).resolve().parent
RECHECK_RUNNER_RELATIVE = Path("b-evidence") / "recheck_e3_candidate.py"
INTENTIONAL_FAILURE_TARGET = "e3-b4-intentional-build-failure"
sys.path.insert(0, str(GENERIC_TOOL_DIR))
sys.path.insert(0, str(E3_TOOL_DIR))

from revalidate import RequestValidationError, run_verification  # noqa: E402


@dataclass(frozen=True)
class CandidateSpec:
    name: str
    base_commit: str
    candidate_commit: str
    configuration_id: str
    selected_finding_id: str
    bundle_sha256: str


CASES = {
    "md-rd": CandidateSpec(
        name="md-rd",
        base_commit="39430e3cdcf16403eec63bf592129b50ab1ff53d",
        candidate_commit="37382e088e26b2827c3d9f7d4c5238d3d39d893f",
        configuration_id="cc-default",
        selected_finding_id="finding-e3-md-rd-missing-001",
        bundle_sha256="d600eb14082b4ba2113f3c39fff4fd74881426935fec9a14cd608e9753958c28",
    ),
    "c1": CandidateSpec(
        name="c1",
        base_commit="9c3e06606aa42afef25c53dbb5eb0c5a6330e5ea",
        candidate_commit="d5d1d4a5a232094b1c2a5a74aadf3932b5ddedcf",
        configuration_id="cc-MODE0",
        selected_finding_id="finding-e3-c1-missing-001",
        bundle_sha256="716b515ea0e1ef4f2e8e82defab91f45492335b8de1515bbdc366bae915436f3",
    ),
}


class CandidateVerificationError(RuntimeError):
    """Raised when a bundle does not match its B2 handoff metadata."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run_git(workspace: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=workspace,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if completed.returncode != 0:
        raise CandidateVerificationError(
            f"git {' '.join(args)} exited with {completed.returncode}: {completed.stderr}"
        )
    return completed.stdout.strip()


def _candidate_identity(spec: CandidateSpec, bundle: Path, workspace: Path) -> dict[str, object]:
    observed_bundle_sha = _sha256(bundle)
    if observed_bundle_sha != spec.bundle_sha256:
        raise CandidateVerificationError(
            f"bundle SHA-256 mismatch: expected {spec.bundle_sha256}, got {observed_bundle_sha}"
        )
    _run_git(workspace, "checkout", "--detach", spec.candidate_commit)
    head = _run_git(workspace, "rev-parse", "HEAD")
    parent = _run_git(workspace, "rev-parse", "HEAD^")
    changed_files = [
        line
        for line in _run_git(
            workspace, "diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"
        ).splitlines()
        if line
    ]
    if head != spec.candidate_commit:
        raise CandidateVerificationError(
            f"candidate commit mismatch: expected {spec.candidate_commit}, got {head}"
        )
    if parent != spec.base_commit:
        raise CandidateVerificationError(
            f"candidate parent mismatch: expected {spec.base_commit}, got {parent}"
        )
    if changed_files != ["Makefile"]:
        raise CandidateVerificationError(
            f"candidate must change only Makefile, got {changed_files}"
        )
    if _run_git(workspace, "status", "--porcelain"):
        raise CandidateVerificationError("candidate workspace is not clean before B4 verification")
    return {
        "case": spec.name,
        "bundle_sha256": observed_bundle_sha,
        "base_commit": spec.base_commit,
        "candidate_commit": spec.candidate_commit,
        "candidate_parent": parent,
        "configuration_id": spec.configuration_id,
        "selected_finding_id": spec.selected_finding_id,
        "changed_files": changed_files,
    }


def _request(spec: CandidateSpec) -> dict[str, object]:
    recheck_command = " ".join(
        (
            "python3",
            RECHECK_RUNNER_RELATIVE.as_posix(),
            "--case",
            spec.name,
            "--workspace",
            ".",
            "--output",
            "b-evidence/recheck-report.json",
        )
    )
    return {
        "schema_version": "2.0",
        "base_commit": spec.base_commit,
        "candidate_commit": spec.candidate_commit,
        "configuration_id": spec.configuration_id,
        "finding_ids": [spec.selected_finding_id],
        "commands": {
            "clean": "make clean",
            "build": "make",
            "test": "./app",
            "recheck": recheck_command,
        },
        "recheck_report": "b-evidence/recheck-report.json",
        "timeout_seconds": 60,
    }


def _prepare_recheck_runner(candidate: Path) -> Path:
    """Place the E3 recheck entry point inside the candidate workspace."""

    runner = candidate / RECHECK_RUNNER_RELATIVE
    runner.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(E3_TOOL_DIR / "recheck_e3_candidate.py", runner)
    return runner


def _clone_candidate(bundle_path: Path, candidate: Path) -> None:
    cloned = subprocess.run(
        ["git", "clone", "--no-checkout", str(bundle_path), str(candidate)],
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if cloned.returncode != 0:
        raise CandidateVerificationError(
            f"candidate bundle clone exited with {cloned.returncode}: {cloned.stderr}"
        )


def _persist_execution_evidence(
    candidate: Path,
    evidence_dir: Path,
    identity: dict[str, object],
    request: dict[str, object],
    output_path: Path,
) -> None:
    evidence_dir.mkdir(parents=True)
    _write_json(evidence_dir / "candidate-identity.json", identity)
    _write_json(evidence_dir / "request.json", request)
    shutil.copytree(candidate / "b-evidence", evidence_dir / "candidate-logs")
    shutil.copy2(output_path, evidence_dir / "b4-revalidation.json")
    recheck_report = candidate / "b-evidence" / "recheck-report.json"
    if recheck_report.is_file():
        shutil.copy2(recheck_report, evidence_dir / "recheck-report.json")


def _run_candidate_verification(
    spec: CandidateSpec,
    candidate: Path,
    identity: dict[str, object],
    evidence_dir: Path,
) -> dict[str, object]:
    _prepare_recheck_runner(candidate)
    request = _request(spec)
    request_path = candidate / "b-evidence" / "request.json"
    _write_json(request_path, request)
    output_path = candidate / "b-evidence" / "b4-revalidation.json"
    report = run_verification(request, candidate, output_path)
    _persist_execution_evidence(candidate, evidence_dir, identity, request, output_path)
    return report


def _with_intentional_build_failure(original_makefile: bytes) -> bytes:
    """Return a temporary negative-probe Makefile without touching a B2 input."""

    probe = (
        "\n# E3 B4 negative recovery probe: this target intentionally fails.\n"
        f".PHONY: {INTENTIONAL_FAILURE_TARGET}\n"
        f"all: {INTENTIONAL_FAILURE_TARGET}\n\n"
        f"{INTENTIONAL_FAILURE_TARGET}:\n"
        "\t@printf '%s\\n' 'E3 intentional invalid-candidate probe'\n"
        "\t@false\n"
    ).encode("utf-8")
    return original_makefile.rstrip(b"\n") + b"\n" + probe


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def verify_candidate(
    spec: CandidateSpec, bundle_path: Path, evidence_dir: Path
) -> dict[str, object]:
    """Verify one B2 candidate, retaining reproducible B4 evidence in ``evidence_dir``."""

    bundle_path = Path(bundle_path).resolve()
    evidence_dir = Path(evidence_dir).resolve()
    if not bundle_path.is_file():
        raise CandidateVerificationError(f"candidate bundle does not exist: {bundle_path}")
    if evidence_dir.exists():
        raise CandidateVerificationError(f"evidence directory already exists: {evidence_dir}")

    with tempfile.TemporaryDirectory(prefix=f"e3-b4-{spec.name}-") as temp_dir:
        candidate = Path(temp_dir) / "candidate"
        _clone_candidate(bundle_path, candidate)
        identity = _candidate_identity(spec, bundle_path, candidate)
        return _run_candidate_verification(spec, candidate, identity, evidence_dir)


def verify_rejected_recovery(
    spec: CandidateSpec, bundle_path: Path, evidence_dir: Path
) -> dict[str, object]:
    """Record a deliberate rejected probe and byte-for-byte Makefile recovery."""

    bundle_path = Path(bundle_path).resolve()
    evidence_dir = Path(evidence_dir).resolve()
    if not bundle_path.is_file():
        raise CandidateVerificationError(f"candidate bundle does not exist: {bundle_path}")
    if evidence_dir.exists():
        raise CandidateVerificationError(f"evidence directory already exists: {evidence_dir}")

    with tempfile.TemporaryDirectory(prefix=f"e3-b4-negative-{spec.name}-") as temp_dir:
        candidate = Path(temp_dir) / "candidate"
        _clone_candidate(bundle_path, candidate)
        identity = _candidate_identity(spec, bundle_path, candidate)
        makefile = candidate / "Makefile"
        original_makefile = makefile.read_bytes()
        original_sha256 = hashlib.sha256(original_makefile).hexdigest()

        makefile.write_bytes(_with_intentional_build_failure(original_makefile))
        rejected = _run_candidate_verification(
            spec, candidate, identity, evidence_dir / "rejected"
        )

        makefile.write_bytes(original_makefile)
        restored_sha256 = _sha256(makefile)
        makefile_restored = restored_sha256 == original_sha256
        if not makefile_restored:
            raise CandidateVerificationError("Makefile bytes did not restore after negative probe")
        _run_git(candidate, "diff", "--quiet", "--", "Makefile")
        recovered = _run_candidate_verification(
            spec, candidate, identity, evidence_dir / "recovered"
        )

        summary = {
            "scenario": "intentional-build-failure-then-makefile-restore",
            "case": spec.name,
            "source_candidate_commit": spec.candidate_commit,
            "candidate_identity": identity,
            "injected_change": {
                "file": "Makefile",
                "target": INTENTIONAL_FAILURE_TARGET,
                "purpose": "negative probe only; not a B2 candidate Patch",
            },
            "rejected": rejected,
            "restore": {
                "original_makefile_sha256": original_sha256,
                "restored_makefile_sha256": restored_sha256,
                "makefile_sha256_matches_original": makefile_restored,
            },
            "recovered": recovered,
        }
        _write_json(evidence_dir / "recovery-summary.json", summary)
        return summary


def _recovery_succeeded(summary: dict[str, object]) -> bool:
    rejected = summary["rejected"]
    recovered = summary["recovered"]
    if not isinstance(rejected, dict) or not isinstance(recovered, dict):
        return False
    error = rejected.get("error")
    return (
        rejected.get("verification_status") == "REJECTED"
        and isinstance(error, dict)
        and error.get("code") == "REPAIR_3001"
        and error.get("stage") == "build"
        and recovered.get("verification_status") == "ACCEPTED"
    )


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", choices=sorted(CASES), required=True)
    parser.add_argument("--bundle", type=Path, required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument(
        "--negative-recovery",
        action="store_true",
        help="record an isolated rejected-build probe and original-Makefile recovery",
    )
    args = parser.parse_args(argv)
    try:
        if args.negative_recovery:
            summary = verify_rejected_recovery(
                CASES[args.case], args.bundle, args.evidence_dir
            )
            passed = _recovery_succeeded(summary)
            print("REJECTED_AND_RECOVERED" if passed else "RECOVERY_FAILED")
            return 0 if passed else 1
        report = verify_candidate(CASES[args.case], args.bundle, args.evidence_dir)
    except (CandidateVerificationError, OSError, RequestValidationError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(report["verification_status"])
    return 0 if report["verification_status"] == "ACCEPTED" else 1


if __name__ == "__main__":
    sys.exit(main())
