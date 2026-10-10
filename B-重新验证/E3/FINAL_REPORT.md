# E3 B4 重新验证最终报告

**当前交接批次：** `run-20261010T060745Z`

**历史批次：** `run-20261009T123411Z` 保留为首次通过运行；其中 `request.json` 曾记录本机绝对 recheck 路径，不能作为可移植交接记录。E3 最终交接以当前批次为准。

**执行环境：** WSL2 Ubuntu；GNU Make 4.3；Ubuntu `cc` 13.3.0；Git 2.43.0；Python 3.12.3。
**结论：** 两个 B2 candidate 均通过 B4 的 bundle 身份核验、clean build、测试、增量重建和独立依赖复查，状态均为 `ACCEPTED`。当前批次另包含一份隔离的无效候选拒绝与原始 `Makefile` 恢复记录。

| 候选 | base commit | candidate commit | 选中的 finding | B4 结论 |
| --- | --- | --- | --- | --- |
| MD/RD | `39430e3cdcf16403eec63bf592129b50ab1ff53d` | `37382e088e26b2827c3d9f7d4c5238d3d39d893f` | `finding-e3-md-rd-missing-001` | `ACCEPTED` |
| C1 | `9c3e06606aa42afef25c53dbb5eb0c5a6330e5ea` | `d5d1d4a5a232094b1c2a5a74aadf3932b5ddedcf` | `finding-e3-c1-missing-001` | `ACCEPTED` |

## 1. 共同核验

两份 bundle 的 SHA-256 均与 B2 交接一致；candidate 的父提交分别等于对应 base commit；每个 candidate 的提交差异仅包含 `Makefile`。这些身份核验记录在各自的 `candidate-identity.json`。

通用 B4 验证器依次运行 `make clean`、`make`、`./app` 和独立 recheck。两个候选的四个阶段退出码均为 0，且 `remaining_selected_findings` 均为空。`request.json` 的 recheck 命令只使用候选工作区内相对路径；归档中报告的 `b-evidence/*.log` 对应同一 case 的 `candidate-logs/*.log`，详见 [`README.md`](README.md) 的映射表。

## 2. MD/RD candidate

- bundle SHA-256：`d600eb14082b4ba2113f3c39fff4fd74881426935fec9a14cd608e9753958c28`。
- 初始构建后的程序输出为 `1`；将 `config.h` 的 `VALUE` 改为 `2` 后，普通 `make` 重新编译 `main.o`，程序输出为 `2`。
- 复查确认 `config.h` 已成为 `main.o` 的声明依赖，选中的 MISSING finding 消失。
- `unused.h` 的 `REDUNDANT` finding 仍在报告中；这与 B2 的 MISSING-only 范围一致，未被误判为本次修复失败。
- B4 报告 SHA-256：`b2c2eab382597f633e211449e4c38eb72cfb2e3db95006a7470a702d50a1dc73`。

证据：[`candidate-identity.json`](evidence/run-20261010T060745Z/md-rd/candidate-identity.json)、[`recheck-report.json`](evidence/run-20261010T060745Z/md-rd/recheck-report.json)、[`b4-revalidation.json`](evidence/run-20261010T060745Z/md-rd/b4-revalidation.json)。

## 3. C1 candidate

- bundle SHA-256：`716b515ea0e1ef4f2e8e82defab91f45492335b8de1515bbdc366bae915436f3`。
- 初始构建后的程序输出为 `12`；将 `feature.h` 的 `FEATURE` 改为 `3` 后，普通 `make` 重新编译 `main.o`，程序输出为 `13`。
- 复查确认 `feature.h` 已成为 `main.o` 的声明依赖，未发现 remaining selected finding。
- B4 报告 SHA-256：`1c82cfd4701651f152a857048622ec432a349984de45197c768646e723ad8526`。

证据：[`candidate-identity.json`](evidence/run-20261010T060745Z/c1/candidate-identity.json)、[`recheck-report.json`](evidence/run-20261010T060745Z/c1/recheck-report.json)、[`b4-revalidation.json`](evidence/run-20261010T060745Z/c1/b4-revalidation.json)。

## 4. 无效候选拒绝与恢复

- 该记录来自已通过身份核验的 MD/RD candidate 的**临时 clone**。B4 在 clone 的 `Makefile` 中加入仅用于负例探针的失败目标；它不是 B2 提供或提交的第三份 candidate Patch。
- 负例构建按预期被拒绝：`verification_status=REJECTED`、`error.code=REPAIR_3001`、`error.stage=build`。拒绝报告 SHA-256：`d1f82b9f640c5f8328b8ae756f7650a6b4ec74cdca828e2d8e5ec00f885e8096`。
- B4 将临时 `Makefile` 按原始字节恢复；恢复前后的 SHA-256 均为 `d4c1f668950edf7cab85ed06529a4c9c12e48639cc75ade0ecb1e362390beb4d`。随后再次运行完整 B4 流程，结果为 `ACCEPTED`；恢复报告 SHA-256：`27da280f60ef56f8823e5fb323701fab1d9614d850d4c881bb1ed8e6f8cf9e27`。

证据：[`recovery-summary.json`](evidence/run-20261010T060745Z/negative-recovery-md-rd/recovery-summary.json)、[`拒绝报告`](evidence/run-20261010T060745Z/negative-recovery-md-rd/rejected/b4-revalidation.json)、[`恢复报告`](evidence/run-20261010T060745Z/negative-recovery-md-rd/recovered/b4-revalidation.json)。

## 5. 最终交接

B4 的 `ACCEPTED` 证明选中的 MISSING finding 已被候选 Patch 消除，并不替代 B2 与 A 组的最终接受决定。下一步应由 B4、B2 和 A 组对应人员对本报告和证据目录共同确认，再决定是否接受 Patch。
