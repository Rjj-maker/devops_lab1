# MD/RD DRAFT 环境本地验收报告

## 结论

本地环境消费验证结果为 **ACCEPTED_LOCAL**。本次从可被远端 clone 的 `main` 提交 `29c02d6604d7071d4b249ec958dd8a553caa670a` 导出 MD/RD 项目，基于 B1 已验收的工具链镜像构建 MD/RD 专用镜像，并在 Colima `linux/amd64` 容器中验证了 DRAFT 构建/测试命令和 MD/RD 行为。本报告中的未完成项仅反映该次本地运行时的交付状态；最新 Registry 接收结论见文末后续状态。

本记录是 A 组环境负责人的本地 E3 交叉验证，不是 B1 对 MD/RD 项目的正式交付。E3 不要求部署或调用 DRAFT API；本地参考输入形状见 `draft-input.json`。镜像尚未发布 Registry，也未验证其他组员跨主机拉取，因此 B1 环境交付和跨组可获取性仍待完成。

## DRAFT 输入

| 字段 | 值 |
| --- | --- |
| `repository.url` | `https://github.com/Rowan-hhh/devops_lab1.git` |
| `repository.commit` | `29c02d6604d7071d4b249ec958dd8a553caa670a` |
| `repository.project_root` | `A-BuildChecker-E3测试基线/fixtures/md-rd` |
| `build_command` | `make` |
| `test_command` | `./app` |
| 测试预期 | 退出码 `0`，stdout 精确为 `1\n` |

这次使用的 SHA 是 GitHub `main` 可检出的普通完整提交，避免依赖只存在于 bundle 内、无法由标准 DRAFT clone 获取的 `39430e3...`。`snapshot-equivalence.json` 对比了 standalone bundle 中的 `main.c`、`config.h`、`unused.h`、`Makefile`、`README.md` 与 main commit 文件，五项 SHA-256 全部一致；bundle 未包含 `interface.json`。

## 环境镜像

- B1 工具链基础镜像：`e3-draft-tiny-greeting@sha256:66b6924106f5f9c5e66705c1678a58dfe81326ede0b3bc61d3a408f3a3a2c06a`
- MD/RD 派生镜像：`e3-buildchecker-md-rd:29c02d6`
- 本地 `image_ref`：`e3-buildchecker-md-rd@sha256:a74c1fd44aaea1ff2427d6b03fcdd8724b32ed764140303e49ea2378b334b6b3`（仅本机 Colima 可用）
- 镜像 ID：`sha256:a74c1fd44aaea1ff2427d6b03fcdd8724b32ed764140303e49ea2378b334b6b3`
- 平台：`linux/amd64`
- Dockerfile：[`Dockerfile.md-rd`](Dockerfile.md-rd)
- Dockerfile SHA-256：`54e9106dc8b731bc81c5fe4cc1160c9d7eeb2d381c3c6a503a6ff16f7f31a119`

该 RepoDigest 是本机 Colima 引擎上的镜像引用，不代表 Registry 已发布，不保证其他机器可以 pull。

## 验收结果

| 检查 | 结果 |
| --- | --- |
| Docker 镜像构建 | 退出码 `0` |
| `make clean` / `make` | 均成功 |
| `./app` | 退出码 `0`，stdout `1\n` |
| MD 行为 | 修改 `config.h` 后普通 `make` 仍输出 `1`；clean rebuild 输出 `2` |
| RD 行为 | 修改未使用的 `unused.h` 后触发 `main.o` 重编译 |
| A 组完整 E3 基线运行 | `ACCEPTED`，run `run-20261010T051714Z` |
| 当前运行报告的 repository commit | `29c02d6604d7071d4b249ec958dd8a553caa670a`；producer job 为 `job-e3-a-md-rd-29c02d66` |
| MISSING / REDUNDANT | `config.h` / `unused.h`，均标记 `INSTRUCTOR_ORACLE` |

逐项命令、stdout/stderr 和退出码见本目录日志；完整机器可读结果见 [`draft-environment-validation.json`](draft-environment-validation.json)。canonical-main full-check 样例报告为 [`../run-20261010T051714Z/md-rd/artifacts/error-report.json`](../run-20261010T051714Z/md-rd/artifacts/error-report.json)。运行器代码摘要见 [`runner-attestation.json`](../run-20261010T051714Z/runner-attestation.json)。

## Commit 和 B2 交接边界

本次重跑报告将 MD/RD `repository.commit` 绑定到 `29c02d6604d7071d4b249ec958dd8a553caa670a`，并在 `repository-commit.sha` 中记录该值。A 基线运行器仍生成 standalone `md-rd.bundle` 作为内部快照，其提交 SHA 为 `39430e3cdcf16403eec63bf592129b50ab1ff53d`；`snapshot-equivalence.json` 证明五个项目源码/构建文件的字节与 canonical main 文件一致，该 SHA 和 canonical repository SHA 的用途不同。canonical-main 报告使用唯一的 `producer_job_id=job-e3-a-md-rd-29c02d66`。

已交给 B2 的旧交接报告及 B2/B4 候选验证仍绑定 standalone commit `39430e3cdcf16403eec63bf592129b50ab1ff53d`。本次没有覆盖旧交接件。B2 若采用新报告，需以新 commit 为 base 重新校验候选 Patch 和 B4 记录。

## 当次运行的未完成项（后续已更新）

1. B1 尚未提交专用于 MD/RD 项目的环境包；本次 Dockerfile 和镜像由 A 组基于 B1 工具链镜像本地派生。
2. Registry 地址或共享传输方式、正式可跨机器使用的 digest 和 A 组远端 pull 尚未确认。
3. 镜像里未安装 `strace`。E3 的 `make` / `./app` 验收通过；strace 证据沿用既有 WSL2 E3 run，不把本次镜像报告成包含 strace 的环境。


## 后续交付状态

B1 后续在 `fa07b7199e985b1dda63cc2efa467e5eb5a0f0ee` 提交 MD/RD 专用环境包，并将镜像发布到 GHCR。A 组已按 `ghcr.io/zaneow0/e3-buildchecker-md-rd@sha256:5be5d74a921c8600aeb4ac7a62bdea27f74521008264130039849b8309c285d6` 拉取并核验 B1 原始镜像，断网功能、MD stale/clean rebuild 和 RD rebuild 均通过。当前接收结果为 `ACCEPTED`，详见 [`../run-20261010T160627Z-ghcr/A_CROSS_MACHINE_RECEIPT.md`](../run-20261010T160627Z-ghcr/A_CROSS_MACHINE_RECEIPT.md)。本报告保留本地派生镜像运行时的历史状态。
