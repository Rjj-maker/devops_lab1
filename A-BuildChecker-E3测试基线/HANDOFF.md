# E3 BuildChecker 交接说明

**交出方：** A 组 BuildChecker 负责人  
**仓库：** https://github.com/Rowan-hhh/devops_lab1  
**目录：** `A-BuildChecker-E3测试基线/`  
**本地提交：** `b7116cd`（`feat(E3/A): add BuildChecker MD/RD baseline and full-check reports`）。若尚未出现在 `origin/main`，先 `git pull` 再确认该 SHA。  
**分工依据：** `docs/E3A组分工.png`

本文只交接 **① 检测项目与 README**、**③ 全量检测与 MD/RD 报告**。请按自己的角色读对应小节，读完后用文末表格回一条确认。

## 1. 请先看哪份文件

| 你是谁 | 先读 | 要做什么 |
| --- | --- | --- |
| B3 接口与 README | 第 3 节 + [`docs/a1-interface.md`](docs/a1-interface.md) | 确认 DRAFT 能按同一 README 取得并运行项目 |
| B2 MDFixer | 第 4 节 + [`handoff/b2/`](handoff/b2/) | 收下完整报告，只选 `MISSING` 做修复 |
| A 组环境负责人 / B1 | 第 5 节 | 为本检测项目准备环境，不要用 Tiny Greeting 镜像冒充 |
| A 组检测/复核 / B4 | 第 6 节 | 等候选 Patch 后核对 MD 是否消失、RD 是否仍在 |
| A 组交付负责人 | 第 7 节 | 最终整理时用本文和有效运行目录 |

公共入口：[`README.md`](README.md)。有效运行：[`evidence/run-20261005T071837Z/`](evidence/run-20261005T071837Z/)，结果 `ACCEPTED`。

## 2. BuildChecker 已经交出什么

| 项 | 位置 | 说明 |
| --- | --- | --- |
| MD/RD 故障项目 | `fixtures/md-rd/` | 漏声明 `config.h`，多声明 `unused.h` |
| C0 / C1 / C2 快照 | `fixtures/commits/` | 声明正确 → 新增 include 未补 Makefile → 只改 `-DMODE=7` |
| 构建 / 验证 | `make` / `./app` | Linux、GNU Make、C 编译器；不需要网络 |
| 人工预期 | `oracle/`、`docs/md-rd-oracle.md` | `detector` 为 `INSTRUCTOR_ORACLE` |
| 实际图 / 声明图 / ERROR_REPORT | `evidence/run-20261005T071837Z/` 与 `handoff/b2/` | 范围：`main.o` 的项目头文件 |
| 可复现提交 | `evidence/run-20261005T071837Z/commits/*.sha` 与 `commits.bundle` | 不是 GitHub `main` 上的三个独立 commit |
| 重跑脚本 | `scripts/run_a_buildchecker.py` | 在仓库根目录执行 |

样例提交 SHA（由运行器生成，与课件行为绑定）：

| 标签 | SHA | 干净构建 `./app` | 发现 |
| --- | --- | --- | --- |
| MD/RD | `39430e3cdcf16403eec63bf592129b50ab1ff53d` | `1` | MD `config.h`，RD `unused.h` |
| C0 | `4f985129bb100b082fe2cfb4f95f846d00752a25` | `10` | 无 |
| C1 | `9c3e06606aa42afef25c53dbb5eb0c5a6330e5ea` | `12` | MD `feature.h` |
| C2 | `5efd7ece7569439950881a9b52b184356aa91687` | `19` | 上述 MD 仍在 |

C2 保留 C1 的 `main.o`/`app` 后普通 `make` 输出仍是 `12`。这是命令变化，不是新的 MD/RD。

**不是本次交付：** E5 BuildChecker 服务、FULL_CHECK API、B1 Tiny Greeting 镜像、MDFixer Patch、B4 拒绝/恢复记录。

## 3. 给 B3：项目、命令、预期输出

请按 [`docs/a1-interface.md`](docs/a1-interface.md) 和各项目 `README.md` 核对。不要改 `fixtures/` 原件，只在工作副本里跑。

在项目根目录：

```bash
make
./app
```

| 项目 | `project_root` | 退出码 | 标准输出 |
| --- | --- | --- | --- |
| MD/RD | `A-BuildChecker-E3测试基线/fixtures/md-rd` | 构建、验证均为 `0` | `1\n` |
| C0 | `.../fixtures/commits/C0` | 同上 | `10\n` |
| C1 | `.../fixtures/commits/C1` | 同上 | `12\n` |
| C2 干净构建 | `.../fixtures/commits/C2` | 同上 | `19\n` |

DRAFT 请求字段对应：`build_command=make`，`test_command=./app`。`make clean` 只用于本地复跑，不新增接口字段。

**请回：** 能否按上述 README 取得源码并跑通；若命令或输出要改，写出差异，不要直接改 A 组 fixtures。

构建成功不等于依赖声明正确。MD/RD 项目首次 `make` 通过，是课件里的预期现象。

## 4. 给 B2：完整报告，只修 MISSING

请从 [`handoff/b2/`](handoff/b2/) 取当前有效副本（与 `run-20261005T071837Z` 一致）。

| 文件 | 内容 | 请选择 |
| --- | --- | --- |
| `handoff/b2/md-rd.error-report.json` | MD：`config.h`；RD：`unused.h` | 只选 `finding-e3-md-rd-missing-001` |
| `handoff/b2/c1.error-report.json` | MD：`feature.h` | 只选 `finding-e3-c1-missing-001` |
| `md-rd.actual.json` / `md-rd.declared.json` | 两张图 | 修复流程不消费图，可用来核对 |

对应 Makefile：`fixtures/md-rd/Makefile`（`main.o: main.c unused.h`）、`fixtures/commits/C1/Makefile`（`main.o: main.c config.h`）。

规则：

1. 必须收下**完整** ERROR_REPORT，不要让 A 组先删掉 RD。
2. `finding_ids` 只能包含 `type=MISSING`。选了 `REDUNDANT` 应按契约拒绝。
3. 你们目录里已有的 [`B-MDFixer-MD交接/E3/`](../B-MDFixer-MD交接/E3/) 是 B2 自己的固定样例，**不是**这次 A 组检测基线的输出。两套可以并行，不要混用 commit 和 Makefile。

**请回：** 已收到哪些 `finding_id`；准备按哪一份 Makefile 出参考 Patch。

## 5. 给 A 组环境负责人 / B1

B1 现有 Tiny Greeting（`make` / `./hello` / `hello E3`）和本检测项目**不是同一份源码**，不能把那个 `image_ref` 填进本项目的 FULL_CHECK。

本项目需要的环境能力：

- 能执行 `make` 和 `./app`
- GNU Make + C 编译器
- 构建和验证不需要网络

本基线已补入 [`B1-MD-RD环境/`](B1-MD-RD环境/)：Dockerfile 直接复制 `fixtures/md-rd` 的六个输入文件，验收脚本检查基本运行、MD stale/clean rebuild 和 RD 触发重编译。它还可以导出 Docker image tar，并生成含 image ID、tar SHA-256 和接收端命令的 `transfer-manifest.json`。

当前有效运行为 [`B1-MD-RD环境/evidence/run-20261010T080813Z/`](B1-MD-RD环境/evidence/run-20261010T080813Z/)，结果为 `ACCEPTED`。镜像身份、tar SHA-256 和本机验收结果见 [`evidence/FINAL_RESULT.md`](B1-MD-RD环境/evidence/FINAL_RESULT.md)。A 组接收机回载与断网运行回执仍需在对方机器上完成。Registry 共享时应用 push 后的 `repo@sha256:...` 作为 `image_ref`。

**请回：** 是否已在 Docker 机器上得到 `ACCEPTED`；向 A 组提供 `transfer-manifest.json` 和镜像 tar，或提供 Registry `repo@sha256:...`。

## 6. 给 A 组检测/复核负责人 / B4

在 B2 交出候选 Patch 之前，本节没有新输入。复核时请对照：

| 版本 | 修复前 | 修复后应看到 |
| --- | --- | --- |
| MD/RD | 改 `config.h` 后普通 make 仍输出 `1`；改 `unused.h` 会多余重编译 | 只改头文件应输出新值；RD 若未修，多余编译可以仍在 |
| C1 / C2 | `feature.h` 为 MISSING；C2 增量 `12`、干净 `19` | 选中的 MISSING 应消失；未选的 RD 与命令变化项按约定保留或另记 |

C2 的 `12` vs `19` 用来核对命令变化，不要当成一条新的 MISSING。原始副本恢复是否成功由 B4 记录，A 组核对结论即可。

**请回：** 收到 Patch 后的复核目录，以及 MD 是否消除、RD 是否仍在。

## 7. 给 A 组交付负责人

最终整理时请带上：

- 本文和 [`README.md`](README.md)
- 有效运行 `evidence/run-20261005T071837Z/`（`summary.json` 为 `ACCEPTED`）
- C0/C1/C2 SHA 与 `commits.bundle`
- 人工预期 `oracle/` 与实际日志的对照（[`validation.md`](validation.md)、[`evidence/FINAL_RESULT.md`](evidence/FINAL_RESULT.md)）
- B3 / B2 / B1 / B4 的确认或差异说明

别人重跑：

```text
python3 A-BuildChecker-E3测试基线/scripts/run_a_buildchecker.py --check-only
python3 A-BuildChecker-E3测试基线/scripts/run_a_buildchecker.py
```

Windows 请用 WSL。脚本每次写新的 `evidence/run-*`，不覆盖旧记录。

## 8. 请各方回执

| 角色 | 请回复的一句话 |
| --- | --- |
| B3 | 已按 README 跑通 / 不能跑通（附命令和退出码） |
| B2 | 已接收 `finding-e3-md-rd-missing-001` 和/或 `finding-e3-c1-missing-001`，不处理 RD |
| 环境 / B1 | 将为本项目提供镜像 / 暂不提供（原因） |
| 复核 / B4 | 尚未开始 / 已复核（MD 消除与否） |
| 交付 | 已纳入 E3 最终包 |

有问题先对本文和 `README.md`，不要改对方目录里的样例。接口字段仍以仓库根目录《接口定义文档 v0.2》为准。
