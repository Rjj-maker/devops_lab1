# DRAFT 构建验证结果

## 结论

最终有效运行：`run-20260929T073452Z`

结果：`ACCEPTED`

数据来源为 [`run-20260929T073452Z/summary.json`](run-20260929T073452Z/summary.json) 及同目录日志。

## 验证结果

| 检查项 | 实际结果 | 判定 |
| --- | --- | --- |
| 输入与接口检查 | 全部检查通过 | 通过 |
| `Dockerfile.broken` 构建 | 退出码 `127` | 预期失败 |
| 失败原因 | `/bin/sh: 1: make: not found` | 原因可定位 |
| `Dockerfile.reference` 构建 | 退出码 `0` | 通过 |
| 镜像检查 | 退出码 `0` | 通过 |
| GCC 版本检查 | GCC `12.2.0`，退出码 `0` | 通过 |
| GNU Make 版本检查 | GNU Make `4.3`，退出码 `0` | 通过 |
| 可执行文件检查 | `/work/hello` 存在且具有执行权限 | 通过 |
| 断网容器运行 | 退出码 `0` | 通过 |
| 实际 stdout | `hello E3\n` | 精确匹配 |
| stderr | 已保留原始日志 | 已记录 |

## 镜像信息

```text
标签：e3-draft-tiny-greeting:reference
镜像 ID：sha256:71242bf070701f40c589820e4aadf74315ac1782fdb6bb5f72abdef49030803d
本地 digest：e3-draft-tiny-greeting@sha256:71242bf070701f40c589820e4aadf74315ac1782fdb6bb5f72abdef49030803d
操作系统：linux
架构：amd64
```

上述 digest 对应本次运行使用的本地 Docker 镜像。镜像发布到 Registry 后，应另行记录 Registry 返回的 digest。

## 源码与环境

```text
项目：e3-draft-tiny-greeting@2026-09-06
运行时 Git SHA：8c248c22f903dff80bda078a69296096787a9d9b
运行环境：WSL2 Ubuntu / Linux 6.6.87.2 / amd64
Docker Server：29.1.3
功能验证网络：none
```

最终运行时，本目录尚未加入 Git 跟踪，具体状态已写入 `summary.json`。输入文件和 Dockerfile 的 SHA-256 均已记录。

## 原始记录

- [`broken-build.stdout.log`](run-20260929T073452Z/broken-build.stdout.log)
- [`broken-build.stderr.log`](run-20260929T073452Z/broken-build.stderr.log)
- [`reference-build.stdout.log`](run-20260929T073452Z/reference-build.stdout.log)
- [`reference-build.stderr.log`](run-20260929T073452Z/reference-build.stderr.log)
- [`reference-image-inspect.stdout.log`](run-20260929T073452Z/reference-image-inspect.stdout.log)
- [`reference-compiler-version.stdout.log`](run-20260929T073452Z/reference-compiler-version.stdout.log)
- [`reference-make-version.stdout.log`](run-20260929T073452Z/reference-make-version.stdout.log)
- [`reference-artifact-check.stdout.log`](run-20260929T073452Z/reference-artifact-check.stdout.log)
- [`reference-verify.stdout.log`](run-20260929T073452Z/reference-verify.stdout.log)
- [`reference-verify.stderr.log`](run-20260929T073452Z/reference-verify.stderr.log)
- [`summary.json`](run-20260929T073452Z/summary.json)
