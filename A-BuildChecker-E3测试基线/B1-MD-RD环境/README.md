# B1 MD/RD 专用环境交付包

本目录为 `A-BuildChecker-E3测试基线/fixtures/md-rd/` 提供独立的 Linux 构建与运行环境。它不使用 Tiny Greeting 源码，也不复制或修改 A 组 fixture。

## 固定输入和预期

| 项目 | 值 |
| --- | --- |
| 源码目录 | `A-BuildChecker-E3测试基线/fixtures/md-rd/` |
| 源码基线 | `main` 提交 `29c02d6604d7071d4b249ec958dd8a553caa670a` |
| 项目标识 | `e3-buildchecker-md-rd@2026-09-10` |
| 默认镜像标签 | `e3-buildchecker-md-rd:b1-20260910` |
| 构建 / 验证 | `make` / `./app` |
| 预期输出 | `1\n` |
| 工具 | GNU Make、GCC、Linux libc 开发文件 |

Docker 构建需要取得 `debian:bookworm-slim` 并安装工具。镜像构建完成后，项目构建、验证和跨机器复验均使用 `--network none`，不需要网络。
默认构建优先使用本地 Docker 缓存；需要刷新基础镜像时显式加 `--pull`。

## 静态检查

在仓库根目录执行：

```text
python "A-BuildChecker-E3测试基线/B1-MD-RD环境/run_b1_md_rd.py" --check-only
```

该命令不调用 Docker，会检查六个项目文件、`interface.json`、Dockerfile 和指定的源码基线提交。

## 本机构建与验收

```text
python "A-BuildChecker-E3测试基线/B1-MD-RD环境/run_b1_md_rd.py"
```

每次会新建 `evidence/run-<UTC 时间>/`，不覆盖历史记录。`summary.json` 只在以下条件全部满足时记为 `ACCEPTED`：

- 镜像为 Linux，且源码基线和项目标识 label 正确；
- 镜像中存在 MD/RD 源码、`Makefile` 和可执行的 `/work/app`；
- 断网运行的标准输出严格为 `1\n`；
- 只改 `config.h` 后普通 `make` 不重编译，输出仍为 `1`（MD stale）；
- 改 `config.h` 后 clean rebuild 会重编译，输出变为 `2`；
- 只改 `unused.h` 会触发 `main.c` 的多余重编译（RD）。

验收在临时容器层中改文件，不会改动 `fixtures/md-rd/` 原件。

## 导出给 A 组跨机器共享

当前已有效运行和镜像身份见 [`evidence/FINAL_RESULT.md`](evidence/FINAL_RESULT.md)。

构建、验收成功后再导出：

```text
python "A-BuildChecker-E3测试基线/B1-MD-RD环境/run_b1_md_rd.py" --export-image "A-BuildChecker-E3测试基线/B1-MD-RD环境/evidence/e3-buildchecker-md-rd.tar"
```

脚本同时生成 `transfer-manifest.json`，其中包含：

- 镜像 tag 和 image ID；
- Registry digest（仅在 Docker 真实返回时记录，不伪造）；
- tar 的字节数和 SHA-256；
- 导入命令、断网验证命令和预期输出。

接收机先核对 tar 的 SHA-256，再执行：

```text
docker load --input e3-buildchecker-md-rd.tar
docker image inspect e3-buildchecker-md-rd:b1-20260910
docker run --rm --network none e3-buildchecker-md-rd:b1-20260910
```

预期最后一条命令退出码为 `0`，标准输出为 `1` 加换行。本地 `docker save` 交付使用 image ID 和 tar SHA-256 识别；如后续改用 Registry，应以 push 后返回的 `repo@sha256:...` 作为跨机器 `image_ref`。
