import json
import sys
import tempfile
import unittest
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parents[1] / "tools"
sys.path.insert(0, str(TOOLS_DIR))

from recheck_e3_candidate import recheck_candidate  # noqa: E402


class E3CandidateRecheckTests(unittest.TestCase):
    def write_md_rd_candidate(self, workspace: Path) -> None:
        (workspace / "main.c").write_text(
            '#include <stdio.h>\n#include "config.h"\nint main(void) { printf("%d\\n", VALUE); }\n',
            encoding="utf-8",
        )
        (workspace / "config.h").write_text("#define VALUE 1\n", encoding="utf-8")
        (workspace / "unused.h").write_text("/* unused */\n", encoding="utf-8")
        (workspace / "Makefile").write_text(
            "CC ?= cc\n"
            "CFLAGS = -Wall -Wextra -std=c11\n\n"
            ".PHONY: all clean\n\n"
            "all: app\n\n"
            "app: main.o\n\t$(CC) $(CFLAGS) -o $@ $^\n\n"
            "main.o: main.c unused.h config.h\n\t$(CC) $(CFLAGS) -c -o $@ $<\n\n"
            "clean:\n\trm -f app main.o\n",
            encoding="utf-8",
        )

    def write_c1_candidate(self, workspace: Path) -> None:
        (workspace / "main.c").write_text(
            '#include <stdio.h>\n#include "config.h"\n#include "feature.h"\nint main(void) { printf("%d\\n", BASE + FEATURE); }\n',
            encoding="utf-8",
        )
        (workspace / "config.h").write_text("#define BASE 10\n", encoding="utf-8")
        (workspace / "feature.h").write_text("#define FEATURE 2\n", encoding="utf-8")
        (workspace / "Makefile").write_text(
            "CC ?= cc\n"
            "CFLAGS = -O0 -Wall -Wextra -std=c11\n\n"
            ".PHONY: all clean\n\n"
            "all: app\n\n"
            "app: main.o\n\t$(CC) $(CFLAGS) -o $@ $^\n\n"
            "main.o: main.c config.h feature.h\n\t$(CC) $(CFLAGS) -c -o $@ $<\n\n"
            "clean:\n\trm -f app main.o\n",
            encoding="utf-8",
        )

    def test_md_rd_recheck_leaves_only_unselected_redundant_finding(self):
        """A reintroduced config.h omission must make the selected finding reappear."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            self.write_md_rd_candidate(workspace)

            report = recheck_candidate("md-rd", workspace)

            self.assertEqual(report["selected_finding_id"], "finding-e3-md-rd-missing-001")
            self.assertEqual(report["remaining_selected_findings"], [])
            self.assertEqual(
                report["findings"],
                [
                    {
                        "finding_id": "finding-e3-md-rd-redundant-001",
                        "type": "REDUNDANT",
                        "target": "main.o",
                        "dependency": "unused.h",
                    }
                ],
            )
            self.assertTrue(report["incremental_probe"]["passed"])
            self.assertEqual(report["incremental_probe"]["observed_stdout"], "2\n")
            self.assertNotIn(
                "Clock skew", report["incremental_probe"]["incremental_make"]["stderr"]
            )

    def test_c1_recheck_reports_no_finding_after_feature_dependency_is_declared(self):
        """A reintroduced feature.h omission must make the selected finding reappear."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            self.write_c1_candidate(workspace)

            report = recheck_candidate("c1", workspace)

            self.assertEqual(report["selected_finding_id"], "finding-e3-c1-missing-001")
            self.assertEqual(report["remaining_selected_findings"], [])
            self.assertEqual(report["findings"], [])
            self.assertTrue(report["incremental_probe"]["passed"])
            self.assertEqual(report["incremental_probe"]["observed_stdout"], "13\n")
            self.assertNotIn(
                "Clock skew", report["incremental_probe"]["incremental_make"]["stderr"]
            )

    def test_recheck_writes_machine_readable_report(self):
        """A malformed or missing report would prevent the generic B4 verifier from deciding."""
        with tempfile.TemporaryDirectory() as temp_dir:
            workspace = Path(temp_dir)
            self.write_c1_candidate(workspace)
            output_path = workspace / "evidence" / "recheck.json"

            report = recheck_candidate("c1", workspace, output_path)

            self.assertEqual(json.loads(output_path.read_text(encoding="utf-8")), report)
            self.assertIn("findings", report)
            self.assertIsInstance(report["findings"], list)


if __name__ == "__main__":
    unittest.main()
