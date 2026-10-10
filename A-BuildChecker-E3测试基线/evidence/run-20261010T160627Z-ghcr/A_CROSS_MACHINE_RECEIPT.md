# A 组 MD/RD 环境包验收与跨机器接收记录

## 最终结论

A 组已从 GitHub Container Registry 按固定 digest 拉取 B1 发布的 MD/RD 镜像，并在接收环境完成镜像身份、源码基线、断网功能和 MD/RD 行为复测。最终结果为 **ACCEPTED**，E3-07 的 Registry 获取与 A 组接收验收通过。

验收使用的镜像引用为 `ghcr.io/zaneow0/e3-buildchecker-md-rd@sha256:5be5d74a921c8600aeb4ac7a62bdea27f74521008264130039849b8309c285d6`。Docker pull、inspect 和功能验证记录见 [`summary.json`](summary.json)、[`registry-replay.json`](registry-replay.json) 及同目录逐项日志。

## 输入与执行环境

| 项目 | 值 |
| --- | --- |
| B1 环境包提交 | `fa07b7199e985b1dda63cc2efa467e5eb5a0f0ee` |
| MD/RD 源码基线 | `29c02d6604d7071d4b249ec958dd8a553caa670a` |
| A 组验收运行 | `run-20261010T160627Z-ghcr`（2026-10-11，Asia/Shanghai） |
| Docker pull | `docker pull --platform linux/amd64 ghcr.io/zaneow0/e3-buildchecker-md-rd@sha256:5be5d74a921c8600aeb4ac7a62bdea27f74521008264130039849b8309c285d6`，退出码 `0` |
| 执行主机 | macOS 27 / arm64；Colima Docker Engine 29.5.2 / Linux arm64 |
| 镜像平台 | Linux / amd64 |
| B1 标签 | `dev.devops-lab.project=e3-buildchecker-md-rd@2026-09-10` |
| B1 源码标签 | `org.opencontainers.image.revision=29c02d6604d7071d4b249ec958dd8a553caa670a` |

## 镜像身份核对

| 检查项 | 接收端结果 |
| --- | --- |
| Registry manifest digest | `sha256:5be5d74a921c8600aeb4ac7a62bdea27f74521008264130039849b8309c285d6` |
| `RepoDigests` | 包含完整 GHCR 引用及同一 digest |
| Docker Image ID | `sha256:5be5d74a921c8600aeb4ac7a62bdea27f74521008264130039849b8309c285d6` |
| OS / 架构 | `linux/amd64` |
| 源码 revision label | 与 MD/RD 基线 commit 一致 |
| 项目标识 label | 与 `e3-buildchecker-md-rd@2026-09-10` 一致 |

接收端的 Registry digest、Image ID、平台及 label 均与 B1 提交的运行记录一致。此前 A 组从 Dockerfile 独立重建的镜像仍保留为本地验收历史，不再作为跨机器接收依据。

## 功能复测

| 检查 | 接收端结果 |
| --- | --- |
| 镜像中的源码、Makefile 和可执行文件 | 存在，检查退出码 `0` |
| GCC / GNU Make | 版本命令均退出码 `0` |
| 断网运行 `./app` | 退出码 `0`，stdout 精确为 `1\n` |
| MD stale build | 不重编译，输出 `1` |
| MD clean rebuild | 重编译，输出 `2` |
| RD 改动 `unused.h` | 触发 `main.c` 重编译，退出码 `0` |

所有构建行为复测均在新建容器可写层中进行，使用 `--network none`，不修改 Registry 镜像层或仓库 fixture。

## 证据索引

- [`registry-pull.command.txt`](registry-pull.command.txt) 和 [`registry-pull.stdout.log`](registry-pull.stdout.log) 记录按 digest 从 GHCR 拉取。
- [`image-inspect.stdout.log`](image-inspect.stdout.log) 记录 `RepoDigests`、Image ID、平台和镜像 labels。
- [`verify.stdout.log`](verify.stdout.log)、[`md-stale.stdout.log`](md-stale.stdout.log)、[`md-clean-rebuild.stdout.log`](md-clean-rebuild.stdout.log) 和 [`rd-rebuild.stdout.log`](rd-rebuild.stdout.log) 记录断网功能及行为检查。
- 所有命令、stdout、stderr 和退出码均保存在本目录。
