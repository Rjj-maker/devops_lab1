# A 组 BuildChecker E3 测试基线

本目录是 A 组 **BuildChecker 负责人** 的 E3 交付，对应《E03 分工：A 组 BuildChecker / 检测基线主流程》的：

1. **① 接口、检测项目与 README 定义**（对接 B3）
2. **③ BuildChecker 全量检测与 MD/RD 报告**（对接 B2）

核心交付对应①检测项目与③全量分析。B1 已在 `fa07b7199e985b1dda63cc2efa467e5eb5a0f0ee` 提交 MD/RD 专用环境包；A 组已从 GHCR 按 digest 拉取 B1 原始镜像并通过最终接收复测，记录见 `evidence/run-20261010T160627Z-ghcr/`。E3 不要求实现 DRAFT API。④ Patch 验证与⑤最终双方交换分别由 A/B4 对接。

E3 只准备可判断对错的项目、人工预期、命令和实际观察。这里没有部署 FULL_CHECK API，也不是 E5 的检测服务。

## 1. 项目参数

| 项目 | 值 |
| --- | --- |
| MD/RD 标识 | `e3-buildchecker-md-rd@2026-09-10` |
| 提交链 | C0 / C1 / C2，样例版本 `2026-09-10` |
| `project_root` | `A-BuildChecker-E3测试基线/fixtures/` |
| 构建命令 | `make` |
| 验证命令 | `./app` |
| 平台 | Linux、GNU Make、C 编译器 |

运行记录中的 Git 版本取自 `git rev-parse HEAD`。项目版本号不能代替 commit SHA。C0/C1/C2 的连续 SHA 在 `evidence/run-*/commits/`。

## 2. 文件说明

| 文件 | 用途 |
| --- | --- |
| `HANDOFF.md` | 给 B3 / B2 / 组内环境、复核、交付的交接说明 |
| `docs/a1-interface.md` | 给 B3 的项目、命令、退出码和预期输出 |
| `docs/md-rd-oracle.md` | 人工预期和判断依据 |
| `docs/c0-c1-c2-plan.md` | 三个提交的变化计划 |
| `docs/full-check-handoff.md` | 给 B2 的完整报告交接说明 |
| `fixtures/md-rd/` | 一个 MD 加一个 RD 的故障项目 |
| `fixtures/commits/C0` `C1` `C2` | 三个版本快照 |
| `oracle/` | `INSTRUCTOR_ORACLE` 预期发现和增量差 |
| `scripts/run_a_buildchecker.py` | 静态检查、行为实验、构图和写报告 |
| `B1-MD-RD环境/` | 基于 `fixtures/md-rd` 的专用 Docker 环境、验收脚本与跨机器导出说明 |
| `evidence/` | 实际命令、退出码、图、报告、提交 bundle 和环境复核证据 |
| `evidence/run-20261010T043534Z-md-rd-main-29c02/` | A 组从 B1 工具链基础镜像派生的 MD/RD 本地环境消费复核 |
| `evidence/run-20261010T114727Z/` | A 组按 B1 Dockerfile 和 runner 独立构建的本地验收 |
| `evidence/run-20261010T160627Z-ghcr/` | A 组按 GHCR digest 接收 B1 原始镜像并完成最终验收与行为复测 |

## 3. 输入检查

在仓库根目录执行：

```text
python3 A-BuildChecker-E3测试基线/scripts/run_a_buildchecker.py --check-only
```

Windows 可用 `python`。该命令检查 fixtures、Makefile 配方使用 TAB、interface 字段以及分析器结果是否等于人工预期。不执行编译。

## 4. 完整运行

需要 GNU Make 和 `cc`。本仓库在 Windows 上请使用 WSL：

```text
python3 A-BuildChecker-E3测试基线/scripts/run_a_buildchecker.py
```

脚本会：

1. 做静态检查；
2. 在 `work/run-<时间>/` 复制样例，不改 fixtures；
3. 跑 MD/RD 的增量、干净重建和冗余声明行为；
4. 创建 C0/C1/C2 Git 提交、标签和 `commits.bundle`；
5. 比较声明依赖和引号 include，写出 `actual.json`、`declared.json`、`error-report.json`；
6. 把命令、stdout、stderr、退出码写入新的 evidence 目录。

脚本不删除已有 evidence，也不覆盖已存在的输出目录。

## 5. 判定规则

`summary.json` 的 `result` 为 `ACCEPTED` 必须同时满足：

- 静态检查通过，分析器发现与 oracle 一致；
- MD/RD 首次输出 `1`；只改 `config.h` 后普通 make 仍为 `1`；干净重建为 `2`；
- 改 `unused.h` 触发对 `main.c` 的重新编译；
- C0/C1/C2 干净构建输出为 `10` / `12` / `19`；
- 保留 C1 产物进入 C2 后，普通 make 输出 `12`。

## 6. 已验证结果

最新有效运行见 [`evidence/FINAL_RESULT.md`](evidence/FINAL_RESULT.md)。

发给对方时用 [`HANDOFF.md`](HANDOFF.md)，按角色读对应小节即可。

## 7. B1 MD/RD 专用环境

B1 环境包见 [`B1-MD-RD环境/README.md`](B1-MD-RD环境/README.md)。它使用本基线的 `fixtures/md-rd` 源码，可验证 `make` / `./app` 以及 MD stale/clean rebuild 和 RD 触发重编译行为。脚本可导出带 SHA-256 交付清单的 Docker image tar。B1 的本机验收结果见 `B1-MD-RD环境/evidence/FINAL_RESULT.md`；A 组已从 GHCR 按固定 digest 接收 B1 原始镜像并通过复测，接收回执见 `evidence/run-20261010T160627Z-ghcr/`。

## 8. 给 B 组的边界

- **B3**：按 `docs/a1-interface.md` 和各项目 README 确认 DRAFT 能取得并运行这些项目。
- **B2**：接收完整 ERROR_REPORT，只选 `MISSING`。RD 必须保留在报告里，不要交给修复器当输入。
- **B1 镜像**：Tiny Greeting 与 MD/RD 检测项目不是同一份源码，不能共用 `image_ref`。MD/RD 专用环境包见 `B1-MD-RD环境/`。A 组已从 `ghcr.io/zaneow0/e3-buildchecker-md-rd@sha256:5be5d74a921c8600aeb4ac7a62bdea27f74521008264130039849b8309c285d6` 拉取并核对 Image ID、RepoDigest、源码 revision 和平台；断网功能及 MD/RD 行为复测均通过，见 `evidence/run-20261010T160627Z-ghcr/`。E3 不要求实现 DRAFT API。
