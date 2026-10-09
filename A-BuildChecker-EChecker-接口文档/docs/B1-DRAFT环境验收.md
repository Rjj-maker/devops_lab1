# B1 DRAFT 样例环境交叉验收记录

## 验收范围

本记录核对 E03 阶段 B1 提交的 Tiny Greeting DRAFT 失败样例、参考环境和运行证据。本记录不验收 DRAFT API，也不表示 BuildChecker 已完成。

验收基准为仓库 `main` 提交 `36f6dd61689f9cdf087d0f83a7d60d6d05db2225`（`feat(B1): add DRAFT build environment and evidence`）。最新有效运行 ID 为 `run-20260929T161653Z`。

## 结论

**B3 项目契约、B1 失败/参考构建和容器功能验证通过。B1 样例环境验收通过。A 组跨机器取得同一镜像的交付方式仍待确认。**

| 检查项 | 结论 | 核对结果 |
| --- | --- | --- |
| B3 项目输入与命令 | 通过 | `main.c`、`Makefile`、`README.md`、`interface.json` 均存在；构建命令为 `make`；验证命令为 `./hello`；预期退出码均为 `0`，stdout 精确为 `hello E3\n`。 |
| B1 失败构建 | 通过 | `Dockerfile.broken` 构建退出码为 `127`；日志明确显示 `/bin/sh: 1: make: not found`。 |
| B1 参考构建 | 通过 | `Dockerfile.reference` 构建和镜像检查退出码为 `0`；镜像内 GCC 为 `12.2.0-14+deb12u1`、GNU Make 为 `4.3`；`/work/hello` 存在且可执行。 |
| B1 功能验证 | 通过 | 容器使用 `--network none` 运行，退出码为 `0`，stdout 精确为 `hello E3\n`。 |
| 当前提交及镜像平台 | 通过 | 运行摘要记录当前 B1 提交 `36f6dd61689f9cdf087d0f83a7d60d6d05db2225`；镜像为 `linux/amd64`。Colima Engine 为 `linux/arm64`，本次通过 `DOCKER_DEFAULT_PLATFORM=linux/amd64` 完成构建和容器验证。 |
| A 组跨机器取得同一镜像 | 未验收 | 当前镜像位于本机 Colima。Registry 发布、镜像文件共享或 A 组拉取记录尚未提供。 |

## 最新成功运行

当前有效运行目录为 [`../../A-B_DRAFT环境交接包/B1-DRAFT环境/evidence/run-20260929T161653Z/`](../../A-B_DRAFT环境交接包/B1-DRAFT环境/evidence/run-20260929T161653Z/)。先前提交的成功运行 `run-20260929T073452Z/` 已恢复并保留为历史记录；两次代理故障重试记录已清理。完整结果摘要见 [`../../A-B_DRAFT环境交接包/B1-DRAFT环境/evidence/FINAL_RESULT.md`](../../A-B_DRAFT环境交接包/B1-DRAFT环境/evidence/FINAL_RESULT.md)。

镜像信息如下：

- 镜像 ID：`sha256:66b6924106f5f9c5e66705c1678a58dfe81326ede0b3bc61d3a408f3a3a2c06a`
- 本地镜像引用：`e3-draft-tiny-greeting@sha256:66b6924106f5f9c5e66705c1678a58dfe81326ede0b3bc61d3a408f3a3a2c06a`
- 操作系统和架构：`linux/amd64`
- Docker Engine：`29.5.2`
- Colima：`0.10.3`
- 宿主环境：macOS `27` / `arm64`

该 digest 是本机 Colima 的镜像检查结果，不表示镜像已发布到 Registry。重新构建使用可变的 `debian:bookworm-slim` 标签和未锁定版本的系统包，不保证产生相同 digest。要让 A 组使用同一镜像，双方仍需确认 Registry 发布或其他传输方式，并由 A 组核验镜像 digest。

## 版本记录

运行摘要中的 Git SHA 与当前 `main` HEAD 相同。运行时工作区存在验收文档和运行证据的未提交变更，因此 `git.dirty` 为 `true`；B1 源码、Dockerfile 和项目输入的字节摘要均保存在 `summary.json`。本记录将 `run-20260929T161653Z/` 指定为当前有效结果，并保留已提交的 `run-20260929T073452Z/` 作为历史成功记录。

## 下一步

1. B1/B3 与 A 组确认镜像传输方式。Registry 方式应记录镜像地址、可见性、Registry digest 和 A 组拉取结果；其他方式应记录镜像归档文件及 SHA-256。
2. A 组在目标环境取得镜像后核对 `linux/amd64`、digest、工具版本和 `hello E3\n` 输出。
3. 正式项目的 DRAFT API Job 和 Artifact 交付仍按 `docs/instance-values.md` 登记，当前样例运行不替代 API 联调。
