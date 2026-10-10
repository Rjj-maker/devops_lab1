# E3 A组 ④ 检测/复核记录

## 元信息

| 项目 | 内容 |
| --- | --- |
| 复核角色 | A组检测/复核负责人（④） |
| 对应流程 | ④ Patch验证、增量检测与失败恢复 |
| 对接方 | B组 B4 重跑与验证负责人 |
| 复核日期 | 2026-10-10 |
| 复核对象 | 上游 `Rowan-hhh/devops_lab1` main 的 B4 正式运行 `B-重新验证/E3/evidence/run-20261009T123411Z/`（提交 `68bc22a6` feat(E3): complete B4 candidate revalidation，经 `29c02d66` 并入 main） |
| 二次复核对象 | 上游 main 提交 `b513d934`「fix(E3): add B4 recovery evidence and portable paths」（经 `78eb4cd4` 并入 main），回归批次 `B-重新验证/E3/evidence/run-20261010T060745Z/` |
| 复核方式 | 只读。通过 GitHub API 读取上游 main 的证据文件，未改动任何被测文件、未执行构建、未做远程写操作 |
| ④ 状态 | **完成** —— 复核通过（§3–§7）+ 三方确认**接受**（§8），2026-10-10 |

## 1. 复核范围与依据

- 判定规范：`B-重新验证/docs/revalidation.md`（阶段顺序与 ACCEPTED/REJECTED 判定标准）。
- 输入基准：`B-MDFixer-MD交接/E3/integration/a-buildchecker/handoff-b4.md`（B2→B4 交接的 bundle SHA、base/candidate 映射、selected finding）。
- A组基线：`A-BuildChecker-E3测试基线/evidence/run-20261005T071837Z/md-rd/artifacts/error-report.json` 与 `A-BuildChecker-E3测试基线/evidence/run-20261005T071837Z/commits/C1/artifacts/error-report.json`。
- 复核维度：Patch 身份核验、修复有效性、增量检测、失败恢复、（附加）证据可移植性。

## 2. 证据清单

| 证据 | 路径（相对 `B-重新验证/E3/evidence/run-20261009T123411Z/`） |
| --- | --- |
| 验证请求 | `<case>/request.json` |
| 候选身份 | `<case>/candidate-identity.json` |
| 依赖复查报告 | `<case>/recheck-report.json` |
| 四阶段验收记录 | `<case>/b4-revalidation.json` |
| 原始阶段日志 | `<case>/candidate-logs/{clean,build,test,recheck}.log` |

`<case>` 分别为 `md-rd`、`c1`。

## 3. 逐项核对结果

### 3.1 Patch 身份核验

| 核对项 | 期望（来自 B2 交接） | 实际 | 判定 |
| --- | --- | --- | --- |
| MD/RD bundle SHA-256 | `d600eb14082b4ba2113f3c39fff4fd74881426935fec9a14cd608e9753958c28` | 一致 | 通过 |
| C1 bundle SHA-256 | `716b515ea0e1ef4f2e8e82defab91f45492335b8de1515bbdc366bae915436f3` | 一致 | 通过 |
| MD/RD 父提交 = base | `39430e3cdcf16403eec63bf592129b50ab1ff53d` | 一致 | 通过 |
| C1 父提交 = base | `9c3e06606aa42afef25c53dbb5eb0c5a6330e5ea` | 一致 | 通过 |
| 变更文件范围 | 仅 `Makefile` | 仅 `Makefile` | 通过 |

### 3.2 修复有效性与配置一致性

| 核对项 | MD/RD | C1 | 判定 |
| --- | --- | --- | --- |
| selected finding | `finding-e3-md-rd-missing-001`（`config.h`） | `finding-e3-c1-missing-001`（`feature.h`） | 通过 |
| 与 A组基线 finding ID 一致 | 一致 | 一致 | 通过 |
| configuration_id | `cc-default` | `cc-MODE0` | 通过 |
| 声明依赖（recheck declared） | `config.h`、`main.c`、`unused.h` | `config.h`、`feature.h`、`main.c` | — |
| 实际依赖（recheck actual） | `config.h`、`main.c` | `config.h`、`feature.h`、`main.c` | 通过 |
| 选中 MISSING 是否消失 | `remaining_selected_findings=[]` | `remaining_selected_findings=[]` | 通过 |

### 3.3 四阶段执行（clean / build / test / recheck）

| 阶段 | MD/RD 退出码 | C1 退出码 | 判定 |
| --- | --- | --- | --- |
| clean | 0 | 0 | 通过 |
| build | 0 | 0 | 通过 |
| test | 0 | 0 | 通过 |
| recheck | 0 | 0 | 通过 |
| 验收状态 | `ACCEPTED` | `ACCEPTED` | 通过 |

关键日志（摘自 `candidate-logs/`）：

- MD/RD：`build` 输出 `cc -Wall -Wextra -std=c11 -c -o main.o main.c` → `cc ... -o app main.o`；`test` 输出 `1`。
- C1：`build` 输出 `cc -O0 -Wall -Wextra -std=c11 -c -o main.o main.c` → `cc ... -o app main.o`；`test` 输出 `12`。

### 3.4 增量检测（incremental probe）

| 核对项 | MD/RD | C1 | 判定 |
| --- | --- | --- | --- |
| 预期输出 | `2` | `13` | — |
| 实测输出 | `2` | `13` | 通过 |
| 改头文件后普通 `make` | 重新编译 `main.o` 并重链接 | 重新编译 `main.o` 并重链接 | 通过 |

### 3.5 REDUNDANT 未被误判

- MD/RD 复查报告 `findings` 仍保留 `finding-e3-md-rd-redundant-001`（`unused.h`，REDUNDANT），且 `remaining_selected_findings` 为空，最终仍判 `ACCEPTED`。
- 结论：`unused.h` 的 RD 按 **B2 的 MISSING-only 修复范围**保留，未被误判为本次修复失败，符合规范 §4。

## 4. 复核结论

**B4 对两个 B2 候选 Patch 的验证与增量检测，复核通过，`ACCEPTED` 结论可采信。**

- MD/RD（base `39430e3…` → candidate `37382e0…`）：选中 MISSING `config.h` 已消除，增量重建生效。
- C1（base `9c3e066…` → candidate `d5d1d4a…`）：选中 MISSING `feature.h` 已消除，增量重建生效。
- B4 未越界：不应用 Patch、不修改 A组基线、不合并候选。

## 5. 初次复核发现与 B组回复

初次复核（对象 `run-20261009T123411Z`）提出以下问题，已发 B4（抄送 B2）：

| # | 发现 | 性质 | B组回复 |
| --- | --- | --- | --- |
| 1 | 「失败恢复」维度无实际运行证据 | 范围确认 | 已补真实「拒绝 → 恢复 → 再验证」记录 |
| 2 | 命令含本机绝对路径 `/mnt/c/Users/zyh18/…`，违反规范 §6 | 修改 | 已改为相对命令 `python3 b-evidence/recheck_e3_candidate.py …` |
| 3 | `b-evidence/*` 与归档 `candidate-logs/*` 的映射未说明 | 补充说明 | 已在交接说明（README）注明映射 |

> 说明：「recheck 未由我方独立复算」属本次复核的方法限制（非 B组问题），保留于 §8 待办。

## 6. 二次复核（B组修复后回归）

对上游 main 提交 `b513d934`（`fix(E3): add B4 recovery evidence and portable paths`，经 `78eb4cd4` 并入）做只读回归复核，新批次 `B-重新验证/E3/evidence/run-20261010T060745Z/`。

### 6.1 失败恢复（新增 `negative-recovery-md-rd/`）

| 核对项 | 证据 | 实测 | 判定 |
| --- | --- | --- | --- |
| 场景 | `recovery-summary.json` | `scenario=intentional-build-failure-then-makefile-restore`；`purpose: negative probe only; not a B2 candidate Patch` | 通过 |
| 拒绝结果 | `rejected/b4-revalidation.json` | `verification_status=REJECTED`，`error.code=REPAIR_3001`，`stage=build`，`build.exit_code=2`，test/recheck `skipped` | 通过 |
| 失败日志 | `rejected/candidate-logs/build.log` | `make: *** [Makefile:23: e3-b4-intentional-build-failure] Error 1` | 通过 |
| 恢复校验 | `recovery-summary.json` `.restore` | `original_makefile_sha256 == restored_makefile_sha256`，`makefile_sha256_matches_original=true` | 通过 |
| 再验证 | `recovered/b4-revalidation.json` | `verification_status=ACCEPTED`，clean/build/test/recheck 退出码均 0，`remaining_selected_findings=[]` | 通过 |
| 未污染 B2 bundle | `rejected/`、`recovered/candidate-identity.json` | `bundle_sha256` 仍为 `d600eb14…`，与 B2 候选一致 | 通过 |

### 6.2 可移植性（相对命令）

| 核对项 | 证据 | 实测 | 判定 |
| --- | --- | --- | --- |
| 正例命令 | `run-20261010T060745Z/md-rd/request.json`、`c1/request.json` | `recheck: python3 b-evidence/recheck_e3_candidate.py …`（相对） | 通过 |
| 失败恢复命令 | `negative-recovery-md-rd/{rejected,recovered}/request.json` | 同上，相对 | 通过 |
| 说明 | `README.md`「可移植性与归档路径」 | 明确 recheck 命令固定为相对候选工作区路径 | 通过 |

> 注：受 GitHub API 限流影响，`candidate-logs/` 下的 `request.json`（同源副本）未逐一拉取；其与顶层 `request.json` 为同一次运行产物。

### 6.3 归档映射说明

| 核对项 | 证据 | 实测 | 判定 |
| --- | --- | --- | --- |
| 映射表 | `README.md` | 新增 `b-evidence/{clean,build,test,recheck}.log` → `candidate-logs/*` 等映射表，并说明顶层 JSON 为便捷副本、非另一轮执行 | 通过 |

### 6.4 历史批次处置

- `README.md` 明确：`run-20261009T123411Z` 保留为历史运行，**E3 最终交接以新批次 `run-20261010T060745Z` 为准**。旧批次 `request.json` 的绝对路径问题不影响新批次交接。

## 7. 复核结论（定稿）

**B4 对两个 B2 候选 Patch 的复核与失败恢复验证，经二次回归复核全部通过；`ACCEPTED` 结论可采信，初次复核 3 项反馈均已闭环。**

- MD/RD（base `39430e3…` → candidate `37382e0…`）：选中 MISSING `config.h` 消除，增量重建生效。
- C1（base `9c3e066…` → candidate `d5d1d4a…`）：选中 MISSING `feature.h` 消除，增量重建生效。
- 失败恢复：无效候选 → `REJECTED/REPAIR_3001` → 原始 `Makefile` 恢复（SHA 一致）→ 再验证 `ACCEPTED`，闭环成立。
- 可移植性：新批次命令均为相对路径，无本机绝对路径残留。
- 归档映射：已在 `README.md` 明确。
- B4 未越界：不应用 Patch、不修改 A组基线、不合并候选。

## 8. 三方共同确认结论

| 项目 | 内容 |
| --- | --- |
| 确认事项 | 是否接受 B4 复核通过的 B2 候选 Patch |
| 参与方 | A组（检测/复核）、B4、B2 |
| 确认方式 | 三方讨论 |
| 确认日期 | 2026-10-10 |
| **结论** | **接受** |
| 被接受对象 | ① MD/RD：base `39430e3…` → candidate `37382e0…`（选中 MISSING `config.h`）② C1：base `9c3e066…` → candidate `d5d1d4a…`（选中 MISSING `feature.h`） |
| 依据 | 本记录 §3–§7 复核结论；回归批次 `run-20261010T060745Z` |

**说明**：按 `revalidation.md` §6，Patch 的最终提交/推送由**流程发起方**决定；A组职责为检测/复核与共同确认，**不代发起方推送 Patch**。

## 9. ④ 完成状态与后续

- ✅ **④（A组检测/复核）已完成**：复核通过（§3–§7）+ 三方确认接受（§8）。
- 后续：
  - [ ] 提交/推送本记录（待确认；本地文件当前**未跟踪**，未 `git add`/commit/push）。
  - [ ] （可选强复核）如判定需要，在 Linux/WSL 环境独立重跑 `recheck_e3_candidate.py`——本次为文档/数据一致性核对，未独立复算依赖图。
  - [ ] 进入 ⑤ E03 最终整理与交付（其「环境信息」一节依赖 A组 ② 的 `image_ref` 绑定）。
