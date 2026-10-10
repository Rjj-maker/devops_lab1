# 当前有效运行结果

## Canonical-main 基线重跑

最新完整基线分析运行：[`run-20261010T051714Z/`](run-20261010T051714Z/)，结果为 `ACCEPTED`。producer Job ID 为 `job-e3-a-md-rd-29c02d66`。它基于可远端 clone 的 main commit `29c02d6604d7071d4b249ec958dd8a553caa670a` 生成 MD/RD `actual.json`、`declared.json` 和 `ERROR_REPORT`。报告 SHA-256 为 `7b021f47912e16bf43e084f23eaa7ecae59f42fa34a33f02b0c97b7ccdb00f22`。

MD/RD 报告中的 MISSING 为 `main.o → config.h`，REDUNDANT 为 `main.o → unused.h`，两条记录均使用 canonical main SHA。MD/RD 首次输出 `1`，头文件变化后的 stale build 保持 `1`，clean rebuild 输出 `2`，unused header 变化触发 `main.o` 重编译。C0/C1/C2 全部通过 oracle 和预期构建结果。

本次 analyzer 在 macOS 主机运行，`strace` 未安装，因此该 run 的 `strace_saw_config_h` 为 `null`。此前 Linux/WSL2 运行 `run-20261005T071837Z` 已记录 `strace` 打开 `config.h`；本次没有覆盖或删除该历史证据。

MD/RD runner 仍将 standalone snapshot bundle SHA `39430e3cdcf16403eec63bf592129b50ab1ff53d` 单独记录为 `snapshot_commit`，用于本地重现。它与新 ERROR_REPORT 的仓库 commit 不同，不能混为一个 Git identity。

## MD/RD DRAFT-compatible 镜像复核

A 环境负责人基于 B1 已验收的本地工具链镜像和同一 canonical main SHA 派生了 MD/RD 专用镜像，并在 Colima `linux/amd64` 容器中复核 `make` / `./app`、MD stale/clean rebuild 和 RD rebuild 行为。验收结果为 `ACCEPTED_LOCAL_ENVIRONMENT_VALIDATION`，完整记录见 [`run-20261010T043534Z-md-rd-main-29c02/`](run-20261010T043534Z-md-rd-main-29c02/) 和 [`DRAFT_ENVIRONMENT_VALIDATION.md`](run-20261010T043534Z-md-rd-main-29c02/DRAFT_ENVIRONMENT_VALIDATION.md)。

B1 已在提交 `fa07b7199e985b1dda63cc2efa467e5eb5a0f0ee` 提交 MD/RD 专用环境包。A 组此前从 Dockerfile 独立构建验收，结果见 [`run-20261010T114727Z/`](run-20261010T114727Z/)。

A 组随后从 GHCR 按固定 digest 拉取 B1 原始镜像，并通过接收端身份及功能复测，结果为 `ACCEPTED`。镜像引用为 `ghcr.io/zaneow0/e3-buildchecker-md-rd@sha256:5be5d74a921c8600aeb4ac7a62bdea27f74521008264130039849b8309c285d6`；接收端 Image ID、RepoDigest、源码 revision 和 `linux/amd64` 平台均匹配。`./app` 断网输出 `1\n`，MD stale/clean rebuild 与 RD rebuild 均通过。完整证据见 [`run-20261010T160627Z-ghcr/`](run-20261010T160627Z-ghcr/)，接收回执见 [`A_CROSS_MACHINE_RECEIPT.md`](run-20261010T160627Z-ghcr/A_CROSS_MACHINE_RECEIPT.md)。E3 不要求部署 DRAFT API。

## 历史运行

`run-20261010T050126Z` 是中间 canonical-main 尝试；由于复用了已使用过的报告 `producer_job_id`，已由 `run-20261010T051714Z` 取代，保留原始文件但不用于交接。

| 目录 | 结果 | 说明 |
| --- | --- | --- |
| `run-20261010T051714Z` | `ACCEPTED` | Canonical-main report，`repository.commit=29c02d6…`，producer Job ID 唯一。 |
| `run-20261005T071837Z` | `ACCEPTED` | WSL2 Ubuntu；含 strace 读取 `config.h` 的记录；报告绑定 standalone MD/RD snapshot SHA `39430e3...`。 |
| `run-20261010T050126Z` | `SUPERSEDED` | 中间 canonical-main 尝试复用了 producer Job ID；保留原始记录，不用于交接。 |
| `run-20261005T071754Z` | `REJECTED` | 复制 C2 源码刷新了 `main.c` 时间戳，增量误重建。 |
| `run-20261005T071651Z` | 中断 | 写 C0 SHA 前未创建 `commits/` 目录。 |

所有历史记录均保留。`handoff/b2/` 继续指向 B2/B4 已采用的 standalone SHA `39430e3...`；canonical-main 新报告暂不替换该交接件。
