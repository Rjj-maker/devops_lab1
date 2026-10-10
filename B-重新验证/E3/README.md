# E3：B4 重新验证

本目录是 E3 中 B4 对 B2 候选 Patch 的实际复核交付。B4 不应用 Patch、不修改 A 组基线、也不合并候选；它只对 B2 提供的每个候选 bundle 单独执行身份核验、clean build、运行测试和依赖复查。

## 输入与边界

输入来自 [`B2 -> B4 交接`](../../B-MDFixer-MD交接/E3/integration/a-buildchecker/handoff-b4.md)，共两个互不合并的候选：

| 样例 | 选中的 MISSING finding | configuration_id |
| --- | --- | --- |
| MD/RD | `finding-e3-md-rd-missing-001` (`config.h`) | `cc-default` |
| C1 | `finding-e3-c1-missing-001` (`feature.h`) | `cc-MODE0` |

MD/RD 中的 `finding-e3-md-rd-redundant-001`（`unused.h`）不在 B2 的 MISSING-only 修复范围内。它会被复查记录保留，但不会使本次 selected finding 的 B4 结论变为拒绝。

## 工具

- [`tools/run_e3_b4.py`](tools/run_e3_b4.py)：验证 bundle SHA-256、base/candidate commit、父提交和仅修改 `Makefile` 的范围，然后调用通用 B4 验证器；`--negative-recovery` 会在临时 clone 中记录一次故意失败的构建和原始 `Makefile` 恢复，绝不改写 B2 bundle。
- [`tools/recheck_e3_candidate.py`](tools/recheck_e3_candidate.py)：在候选 workspace 中比较 `main.o` 的 Makefile 前置依赖与真实引号 include，并执行一次头文件变更后的增量重建。
- [`tests/`](tests/)：覆盖两个候选的静态与增量复查，以及端到端 bundle 验证与证据保留。

工具必须在 Linux/WSL 的 GNU Make 与 C 编译器环境中运行。示例：

```sh
python3 B-重新验证/E3/tools/run_e3_b4.py \
  --case md-rd \
  --bundle B-MDFixer-MD交接/E3/integration/a-buildchecker/candidate-bundles/md-rd-candidate.bundle \
  --evidence-dir B-重新验证/E3/evidence/run-<UTC 时间>/md-rd
```

对 C1 使用 `--case c1` 和对应的 `c1-candidate.bundle`。每个 evidence 目录必须是新的空目录，避免覆盖既有运行记录。

记录 E3 要求的无效候选拒绝和恢复时，使用同一个已验证 bundle 的临时 clone：

```sh
python3 B-重新验证/E3/tools/run_e3_b4.py \
  --case md-rd \
  --bundle B-MDFixer-MD交接/E3/integration/a-buildchecker/candidate-bundles/md-rd-candidate.bundle \
  --evidence-dir B-重新验证/E3/evidence/run-<UTC 时间>/negative-recovery-md-rd \
  --negative-recovery
```

该命令只在临时 clone 的 `Makefile` 中加入故意失败的依赖目标。它先记录 `REJECTED / REPAIR_3001`，再按字节恢复原 `Makefile`、核对 SHA-256，并重新验证为 `ACCEPTED`。

## 可移植性与归档路径

`request.json` 中的 recheck 命令固定为相对候选工作区的 `python3 b-evidence/recheck_e3_candidate.py ...`。执行器会先把 recheck 脚本复制到该位置，因此交接记录不依赖 B4 执行机的绝对路径。

`b4-revalidation.json` 中的 `validation.*.log_path` 保留候选工作区内的相对地址 `b-evidence/<文件>`；归档时按下表解析：

| 候选工作区中的原件 | `<case>/` 下的归档位置 |
| --- | --- |
| `b-evidence/{clean,build,test,recheck}.log` | `candidate-logs/{clean,build,test,recheck}.log` |
| `b-evidence/request.json` | `candidate-logs/request.json`；另有顶层 `request.json` 便于交接读取 |
| `b-evidence/b4-revalidation.json` | `candidate-logs/b4-revalidation.json`；另有顶层 `b4-revalidation.json` |
| `b-evidence/recheck-report.json` | `candidate-logs/recheck-report.json`；另有顶层 `recheck-report.json` |
| `b-evidence/recheck_e3_candidate.py` | `candidate-logs/recheck_e3_candidate.py` |

因此，报告中的 `b-evidence/build.log` 在持久化证据目录中对应 `candidate-logs/build.log`；顶层 JSON 文件是同一运行的便捷副本，不是另一轮执行。

## 已完成的正式运行

当前交接批次为 [`evidence/run-20261010T060745Z/`](evidence/run-20261010T060745Z/)：MD/RD、C1 均为 `ACCEPTED`，并包含 MD/RD 的 `negative-recovery-md-rd/`（先拒绝、后恢复通过）记录。此前 [`run-20261009T123411Z/`](evidence/run-20261009T123411Z/) 保留为历史运行，但其 `request.json` 记录过本机绝对路径；E3 最终交接以新批次为准。完整结论、版本与 Artifact SHA-256 见 [`FINAL_REPORT.md`](FINAL_REPORT.md)。
