# B1 DRAFT 构建验证结果

## 结论

最新有效运行目录：`run-20260929T161653Z`

运行结果：`ACCEPTED`

完整数据、命令、stdout/stderr、退出码和镜像信息见 [`run-20260929T161653Z/summary.json`](run-20260929T161653Z/summary.json) 及同目录日志。本文件将该目录指定为当前有效成功运行；先前提交的 `run-20260929T073452Z/` 保留为历史记录。

## 验证结果

| 检查项 | 实际结果 | 判定 |
| --- | --- | --- |
| B3 输入与接口检查 | 全部通过 | 通过 |
| `Dockerfile.broken` 构建 | 退出码 `127` | 预期失败 |
| 失败原因 | `/bin/sh: 1: make: not found` | 原因可定位 |
| `Dockerfile.reference` 构建 | 退出码 `0` | 通过 |
| 镜像检查 | 退出码 `0` | 通过 |
| GCC 版本检查 | GCC `12.2.0-14+deb12u1`，退出码 `0` | 通过 |
| GNU Make 版本检查 | GNU Make `4.3`，退出码 `0` | 通过 |
| 可执行文件检查 | `/work/hello` 存在且具有执行权限 | 通过 |
| 断网容器运行 | 退出码 `0` | 通过 |
| 实际 stdout | `hello E3\n` | 精确匹配 |
| stderr | 已保留原始日志 | 已记录 |

## 镜像信息

```text
标签：e3-draft-tiny-greeting:reference
镜像 ID：sha256:66b6924106f5f9c5e66705c1678a58dfe81326ede0b3bc61d3a408f3a3a2c06a
本地镜像引用：e3-draft-tiny-greeting@sha256:66b6924106f5f9c5e66705c1678a58dfe81326ede0b3bc61d3a408f3a3a2c06a
操作系统：linux
架构：amd64
```

该 digest 是 Colima 本地镜像检查结果，不表示镜像已发布到 Registry。A 组跨机器取得镜像的方式和 Registry digest 仍需单独确认。

## 源码与环境

```text
B1 源码提交：36f6dd61689f9cdf087d0f83a7d60d6d05db2225
执行主机：macOS 27 / arm64
Docker Engine：29.5.2 / Ubuntu 24.04.4 / linux/arm64
镜像目标平台：linux/amd64
Colima：0.10.3
```

运行通过 `DOCKER_DEFAULT_PLATFORM=linux/amd64` 构建和执行 amd64 镜像。运行时工作区包含未提交的验收文档和运行证据，摘要中的 `git.dirty` 为 `true`；B1 输入和 Dockerfile 的 SHA-256 保存在 `summary.json`。

## 原始记录

- [`broken-build.stdout.log`](run-20260929T161653Z/broken-build.stdout.log)
- [`broken-build.stderr.log`](run-20260929T161653Z/broken-build.stderr.log)
- [`reference-build.stdout.log`](run-20260929T161653Z/reference-build.stdout.log)
- [`reference-build.stderr.log`](run-20260929T161653Z/reference-build.stderr.log)
- [`reference-image-inspect.stdout.log`](run-20260929T161653Z/reference-image-inspect.stdout.log)
- [`reference-compiler-version.stdout.log`](run-20260929T161653Z/reference-compiler-version.stdout.log)
- [`reference-make-version.stdout.log`](run-20260929T161653Z/reference-make-version.stdout.log)
- [`reference-artifact-check.stdout.log`](run-20260929T161653Z/reference-artifact-check.stdout.log)
- [`reference-verify.stdout.log`](run-20260929T161653Z/reference-verify.stdout.log)
- [`reference-verify.stderr.log`](run-20260929T161653Z/reference-verify.stderr.log)
- [`summary.json`](run-20260929T161653Z/summary.json)
