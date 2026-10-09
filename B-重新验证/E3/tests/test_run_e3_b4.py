import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS_DIR))

from run_e3_b4 import CandidateSpec, verify_candidate  # noqa: E402


class E3B4RunnerTests(unittest.TestCase):
    def run_git(self, repo: Path, *args: str) -> str:
        completed = subprocess.run(
            ["git", *args],
            cwd=repo,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return completed.stdout.strip()

    def write_candidate_files(self, repo: Path, fixed: bool) -> None:
        (repo / "main.c").write_text(
            '#include <stdio.h>\n#include "config.h"\nint main(void) { printf("%d\\n", VALUE); }\n',
            encoding="utf-8",
        )
        (repo / "config.h").write_text("#define VALUE 1\n", encoding="utf-8")
        (repo / "unused.h").write_text("/* unselected redundant dependency */\n", encoding="utf-8")
        dependencies = "main.c unused.h config.h" if fixed else "main.c unused.h"
        (repo / "Makefile").write_text(
            "CC ?= cc\n"
            "CFLAGS = -Wall -Wextra -std=c11\n\n"
            ".PHONY: all clean\n\n"
            "all: app\n\n"
            "app: main.o\n\t$(CC) $(CFLAGS) -o $@ $^\n\n"
            f"main.o: {dependencies}\n\t$(CC) $(CFLAGS) -c -o $@ $<\n\n"
            "clean:\n\trm -f app main.o\n",
            encoding="utf-8",
        )

    def test_runner_accepts_a_verified_candidate_and_preserves_evidence(self):
        """Changing the candidate SHA or losing B4 logs must make this handoff unverifiable."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source"
            source.mkdir()
            self.run_git(source, "init", "-b", "main")
            self.run_git(source, "config", "user.name", "B4 Test")
            self.run_git(source, "config", "user.email", "b4-test@example.invalid")

            self.write_candidate_files(source, fixed=False)
            self.run_git(source, "add", ".")
            self.run_git(source, "commit", "-m", "base")
            base_commit = self.run_git(source, "rev-parse", "HEAD")
            self.write_candidate_files(source, fixed=True)
            self.run_git(source, "add", "Makefile")
            self.run_git(source, "commit", "-m", "declare config header")
            candidate_commit = self.run_git(source, "rev-parse", "HEAD")
            bundle = root / "candidate.bundle"
            self.run_git(source, "bundle", "create", str(bundle), "--all")
            bundle_sha = hashlib.sha256(bundle.read_bytes()).hexdigest()
            spec = CandidateSpec(
                name="md-rd",
                base_commit=base_commit,
                candidate_commit=candidate_commit,
                configuration_id="cc-default",
                selected_finding_id="finding-e3-md-rd-missing-001",
                bundle_sha256=bundle_sha,
            )
            evidence_dir = root / "evidence"

            report = verify_candidate(spec, bundle, evidence_dir)

            self.assertEqual(report["verification_status"], "ACCEPTED")
            self.assertEqual(report["remaining_selected_findings"], [])
            self.assertTrue((evidence_dir / "b4-revalidation.json").is_file())
            self.assertTrue((evidence_dir / "candidate-logs" / "build.log").is_file())
            self.assertTrue((evidence_dir / "candidate-logs" / "recheck.log").is_file())
            self.assertTrue((evidence_dir / "recheck-report.json").is_file())

    def test_runner_preserves_rejection_evidence_when_incremental_rebuild_fails(self):
        """A rejected candidate must retain its B4 report and recheck log for B2."""
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source"
            source.mkdir()
            self.run_git(source, "init", "-b", "main")
            self.run_git(source, "config", "user.name", "B4 Test")
            self.run_git(source, "config", "user.email", "b4-test@example.invalid")

            self.write_candidate_files(source, fixed=False)
            self.run_git(source, "add", ".")
            self.run_git(source, "commit", "-m", "base")
            base_commit = self.run_git(source, "rev-parse", "HEAD")
            (source / "Makefile").write_text(
                (source / "Makefile").read_text(encoding="utf-8").replace(
                    "CFLAGS = -Wall", "CFLAGS = -O0 -Wall"
                ),
                encoding="utf-8",
            )
            self.run_git(source, "add", "Makefile")
            self.run_git(source, "commit", "-m", "unrelated makefile change")
            candidate_commit = self.run_git(source, "rev-parse", "HEAD")
            bundle = root / "candidate.bundle"
            self.run_git(source, "bundle", "create", str(bundle), "--all")
            spec = CandidateSpec(
                name="md-rd",
                base_commit=base_commit,
                candidate_commit=candidate_commit,
                configuration_id="cc-default",
                selected_finding_id="finding-e3-md-rd-missing-001",
                bundle_sha256=hashlib.sha256(bundle.read_bytes()).hexdigest(),
            )
            evidence_dir = root / "evidence"

            report = verify_candidate(spec, bundle, evidence_dir)

            self.assertEqual(report["verification_status"], "REJECTED")
            self.assertEqual(report["error"]["stage"], "recheck")
            self.assertTrue((evidence_dir / "b4-revalidation.json").is_file())
            self.assertTrue((evidence_dir / "candidate-logs" / "recheck.log").is_file())


if __name__ == "__main__":
    unittest.main()
