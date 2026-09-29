# DRAFT 环境与构建验证

本目录提供 Tiny Greeting 项目的失败构建样例、参考构建环境和可重复执行的验证脚本。项目参数以 [`../fixtures/draft/interface.json`](../fixtures/draft/interface.json) 为准。

## 1. 项目参数

| 项目 | 值 |
| --- | --- |
| 项目标识 | `e3-draft-tiny-greeting` |
| 项目版本 | `2026-09-06` |
| `project_root` | `A-B_DRAFT环境交接包/fixtures/draft` |
| Docker build context | `A-B_DRAFT环境交接包/` |
| 构建命令 | `make` |
| 验证命令 | `./hello` |
| 预期标准输出 | `hello E3\n` |
| 预期退出码 | 构建和验证均为 `0` |

运行记录中的 Git 版本取自 `git rev-parse HEAD`。项目版本号不能代替 commit SHA。

## 2. 文件说明

| 文件 | 用途 |
| --- | --- |
| `Dockerfile.broken` | 缺少 GNU Make 和 C 编译器，用于复现可定位的构建失败 |
| `Dockerfile.reference` | 安装 `gcc`、`make` 和 `libc6-dev`，完成项目构建 |
| `run_b1.py` | 检查输入并记录 Docker 构建、镜像信息和运行结果 |
| `evidence/README.md` | 运行记录的文件结构和核对项 |
| `evidence/FINAL_RESULT.md` | 已完成运行的结果摘要和日志索引 |

## 3. 输入检查

在 `A-B_DRAFT环境交接包/` 目录执行：

```text
python B1-DRAFT环境/run_b1.py --check-only
```

该命令检查：

- `main.c`、`Makefile`、`README.md` 和 `interface.json` 是否存在；
- 项目标识、`project_root`、构建命令和验证命令是否一致；
- 预期退出码和标准输出是否一致；
- 两个 Dockerfile 是否存在；
- 输入文件当前的 SHA-256。

输入检查只验证文件和参数，不执行镜像构建。

## 4. 完整运行

在 Linux 或已配置 Docker 的环境中，进入 `A-B_DRAFT环境交接包/` 后执行：

```text
python B1-DRAFT环境/run_b1.py
```

脚本依次执行：

1. 记录 Docker 版本；
2. 使用 `Dockerfile.broken` 构建，确认缺少 `make` 时返回非零退出码；
3. 使用 `Dockerfile.reference` 构建，确认退出码为 `0`；
4. 记录参考镜像的 ID、标签、digest、操作系统和架构；
5. 记录容器内 `gcc` 和 GNU Make 的版本；
6. 检查 `/work/hello` 存在且具有可执行权限；
7. 使用 `--network none` 运行参考镜像；
8. 核对容器退出码为 `0`，stdout 严格等于 `hello E3\n`；
9. 将命令、stdout、stderr、退出码、Git 状态和汇总写入新的时间戳目录。

默认镜像标签：

```text
e3-draft-tiny-greeting:broken
e3-draft-tiny-greeting:reference
```

可指定镜像标签或输出目录：

```text
python B1-DRAFT环境/run_b1.py --broken-tag e3-draft-tiny-greeting:broken-20260906 --reference-tag e3-draft-tiny-greeting:reference-20260906 --output-dir evidence/run-20260929
```

脚本不会删除镜像、容器、源码或已有运行记录，也不会覆盖已存在的输出目录。

## 5. 判定规则

结果为 `ACCEPTED` 必须同时满足：

- 失败镜像构建返回非零退出码；
- 失败日志包含 `make: not found`；
- 参考镜像构建退出码为 `0`；
- `docker image inspect` 执行成功并返回镜像 ID；
- `gcc --version` 和 `make --version` 均执行成功；
- `/work/hello` 存在且具有可执行权限；
- 容器在 `--network none` 条件下退出码为 `0`；
- 容器 stdout 严格等于 `hello E3\n`。

## 6. 网络与缓存

源码编译完成后的容器运行不需要网络，并固定使用 `--network none`。首次获取基础镜像及安装系统包需要网络；本地已保存基础镜像和软件包缓存时可以离线复用。运行记录包含所用镜像的标识和摘要。

## 7. 已验证结果

最终有效运行目录：

```text
evidence/run-20260929T073452Z/
```

该次运行结果为 `ACCEPTED`：失败样例退出码为 `127`，日志包含 `make: not found`；参考镜像构建、镜像检查、工具版本检查、可执行文件检查和断网运行的退出码均为 `0`；stdout 严格匹配 `hello E3\n`。详细结果见 [`evidence/FINAL_RESULT.md`](evidence/FINAL_RESULT.md)。
