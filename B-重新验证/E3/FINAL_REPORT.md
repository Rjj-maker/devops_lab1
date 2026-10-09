# E3 B4 重新验证最终报告

**运行批次：** `run-20261009T123411Z`

**执行环境：** WSL2 Ubuntu；GNU Make 4.3；Ubuntu `cc` 13.3.0；Git 2.43.0；Python 3.12.3。
**结论：** 两个 B2 candidate 均通过 B4 的 bundle 身份核验、clean build、测试、增量重建和独立依赖复查，状态均为 `ACCEPTED`。

| 候选 | base commit | candidate commit | 选中的 finding | B4 结论 |
| --- | --- | --- | --- | --- |
| MD/RD | `39430e3cdcf16403eec63bf592129b50ab1ff53d` | `37382e088e26b2827c3d9f7d4c5238d3d39d893f` | `finding-e3-md-rd-missing-001` | `ACCEPTED` |
| C1 | `9c3e06606aa42afef25c53dbb5eb0c5a6330e5ea` | `d5d1d4a5a232094b1c2a5a74aadf3932b5ddedcf` | `finding-e3-c1-missing-001` | `ACCEPTED` |

## 1. 共同核验

两份 bundle 的 SHA-256 均与 B2 交接一致；candidate 的父提交分别等于对应 base commit；每个 candidate 的提交差异仅包含 `Makefile`。这些身份核验记录在各自的 `candidate-identity.json`。

通用 B4 验证器依次运行 `make clean`、`make`、`./app` 和独立 recheck。两个阶段的退出码均为 0，且 `remaining_selected_findings` 均为空。

## 2. MD/RD candidate

- bundle SHA-256：`d600eb14082b4ba2113f3c39fff4fd74881426935fec9a14cd608e9753958c28`。
- 初始构建后的程序输出为 `1`；将 `config.h` 的 `VALUE` 改为 `2` 后，普通 `make` 重新编译 `main.o`，程序输出为 `2`。
- 复查确认 `config.h` 已成为 `main.o` 的声明依赖，选中的 MISSING finding 消失。
- `unused.h` 的 `REDUNDANT` finding 仍在报告中；这与 B2 的 MISSING-only 范围一致，未被误判为本次修复失败。
- B4 报告 SHA-256：`691ed32d277284db29666d19e3682ca1c10fe8b132569072ab88297643c4f4c7`。

证据：[`candidate-identity.json`](evidence/run-20261009T123411Z/md-rd/candidate-identity.json)、[`recheck-report.json`](evidence/run-20261009T123411Z/md-rd/recheck-report.json)、[`b4-revalidation.json`](evidence/run-20261009T123411Z/md-rd/b4-revalidation.json)。

## 3. C1 candidate

- bundle SHA-256：`716b515ea0e1ef4f2e8e82defab91f45492335b8de1515bbdc366bae915436f3`。
- 初始构建后的程序输出为 `12`；将 `feature.h` 的 `FEATURE` 改为 `3` 后，普通 `make` 重新编译 `main.o`，程序输出为 `13`。
- 复查确认 `feature.h` 已成为 `main.o` 的声明依赖，未发现 remaining selected finding。
- B4 报告 SHA-256：`faa76255f0bbe5b2b29625f60397b6fa9233766e9029d20f129994006807a771`。

证据：[`candidate-identity.json`](evidence/run-20261009T123411Z/c1/candidate-identity.json)、[`recheck-report.json`](evidence/run-20261009T123411Z/c1/recheck-report.json)、[`b4-revalidation.json`](evidence/run-20261009T123411Z/c1/b4-revalidation.json)。

## 4. 最终交接

B4 的 `ACCEPTED` 证明选中的 MISSING finding 已被候选 Patch 消除，并不替代 B2 与 A 组的最终接受决定。下一步应由 B4、B2 和 A 组对应人员对本报告和证据目录共同确认，再决定是否接受 Patch。
