# A 组 MD/RD 环境包验收与跨机器接收记录

## 本次运行结论

A 组按 B1 提交 `fa07b7199e985b1dda63cc2efa467e5eb5a0f0ee` 中的 Dockerfile 和 runner 完成本机独立构建及功能验收，结果为 `ACCEPTED`。A 组本机导出归档重新加载后，断网运行输出 `1\n`。本次记录仅证明按 B1 Dockerfile 在 A 组环境重建的镜像通过本地验收，不作为 B1 原始镜像的跨机器接收回执。

本次运行当时的 Registry 接收状态为 `BLOCKED`，仅表示本地 Dockerfile 重建尚未取得 B1 原始镜像。后续 A 组已从 GHCR 按 B1 digest 拉取原始镜像并通过身份核对、断网功能与 MD/RD 行为复测；当前接收结论为 `ACCEPTED`，完整回执见 [`../run-20261010T160627Z-ghcr/A_CROSS_MACHINE_RECEIPT.md`](../run-20261010T160627Z-ghcr/A_CROSS_MACHINE_RECEIPT.md)。

## 输入与执行环境

| 项目 | 值 |
| --- | --- |
| B1 环境包提交 | `fa07b7199e985b1dda63cc2efa467e5eb5a0f0ee` |
| MD/RD 源码基线 | `29c02d6604d7071d4b249ec958dd8a553caa670a` |
| 静态检查 | `PASSED`；`source_matches_baseline_commit=true` |
| A 组运行 ID | `run-20261010T114727Z` |
| 执行主机 | macOS 27 / arm64；Colima Docker Engine 29.5.2 / Ubuntu 24.04.4 |
| 镜像平台 | `linux/amd64`，通过 `DOCKER_DEFAULT_PLATFORM=linux/amd64` 构建 |
| 工作树状态 | 干净临时检出；runner 记录 commit 为 B1 环境包提交 |

## 功能检查

| 检查 | 结果 |
| --- | --- |
| 镜像构建、镜像检查、源码和工具版本检查 | 全部退出码为 `0` |
| 断网运行 `./app` | 退出码 `0`，stdout 为 `1\n` |
| MD stale build | 不重编译，输出 `1` |
| MD clean rebuild | 重新编译，输出 `2` |
| RD 头文件改动 | 触发 `main.c` 重编译 |
| A 组导出归档 SHA-256 | `113373dc87ff883683937e6f1d02c1cf2ccc21c8abff61f496415f2531cf8788` |
| A 组导出归档大小 | `98049536` bytes |
| A 组重载归档后的断网运行 | 退出码 `0`，stdout 为 `1\n` |

完整 stdout、stderr、命令和退出码见 [`summary.json`](summary.json) 及本目录日志。A 组本机重建镜像为 `e3-buildchecker-md-rd:b1-20260910`，Image ID 为 `sha256:ce6e924d768cc529c9b53381500106b65192a40acd17de83e7d437aba0c863a8`。

## 与 B1 原始产物的区分

B1 运行记录声明的 Image ID 为 `sha256:5be5d74a921c8600aeb4ac7a62bdea27f74521008264130039849b8309c285d6`，原始归档 SHA-256 为 `02ee7f60fccf2392d1895e1cee616d31ba05488faab83e1c76ee07121e6e5681`。A 组重建的 Image ID 和 tar SHA-256 均不同，不能将 A 组重建产物标记为已收到的 B1 原始镜像。B1 原始 tar 未包含在 Git 提交中；本次没有对其内容进行接收端校验。

## 本次运行时的 Registry 状态

仓库未指定共享 Registry 地址或镜像命名空间。本机 Docker 配置未设置 Registry 凭据，GitHub CLI 也未登录；本次未执行 Registry push 或 pull。B1 当前运行记录的镜像和归档身份不能替代可访问的 Registry `repo@sha256:...`。

本节记录本次本地重建验收时的状态，不代表当前状态。后续 A 组按准确 GHCR digest 接收 B1 原始镜像，并已在 [`run-20261010T160627Z-ghcr/`](../run-20261010T160627Z-ghcr/) 完成镜像身份核对及断网功能、MD/RD 行为复测。
