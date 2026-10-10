# E3 BuildChecker 基线验证

## 固定信息

| 项目 | 值 |
| --- | --- |
| 仓库 URL | `https://github.com/Rowan-hhh/devops_lab1.git` |
| 原始可追溯运行 | `evidence/run-20261005T071837Z/`（standalone snapshot） |
| canonical-main 最终重跑 | `evidence/run-20261010T051714Z/`，`producer_job_id=job-e3-a-md-rd-29c02d66` |
| canonical MD/RD repository commit | `29c02d6604d7071d4b249ec958dd8a553caa670a` |
| standalone MD/RD reproduction snapshot | `39430e3cdcf16403eec63bf592129b50ab1ff53d` |
| C0 / C1 / C2 | `4f985129bb100b082fe2cfb4f95f846d00752a25` / `9c3e06606aa42afef25c53dbb5eb0c5a6330e5ea` / `5efd7ece7569439950881a9b52b184356aa91687` |
| 构建命令 | `make clean && make` |
| 运行命令 | `./app` |

## 预期行为

- MD/RD：干净构建输出 `1`；把 `VALUE` 改为 `2` 后普通 make 仍为 `1`；再干净构建为 `2`；改 `unused.h` 触发重编译。
- C0 输出 `10`，无 MD/RD。C1 输出 `12`，缺少 `feature.h`。C2 干净构建 `19`，增量保留 C1 产物时为 `12`。

## 验证环境

原始 WSL2 Ubuntu 运行环境为 `Linux 6.6.87.2-microsoft-standard-WSL2` / `x86_64`、GNU Make 4.3、Ubuntu cc 13.3.0、Python 3.12.3、Git 2.43.0。canonical-main analyzer 重跑在 macOS 27 / arm64 / Python 3.9.6 上执行；strace 未安装，因此该轮 `strace_saw_config_h` 为 `null`。MD/RD 的 DRAFT-compatible 镜像复核在 Colima Linux/amd64 中进行，基于 B1 工具链镜像并包含 GNU Make、GCC 和 libc 开发文件。

修改头文件后将其时间戳设为晚于 `main.o`，再执行普通 `make`。C2 增量实验保留 C1 的 `main.o`/`app`，并把目标文件时间调到源码之后，以避免“复制源码刷新时间戳”被误当成命令变化检测。

## 实际结果

原始 WSL2 运行与 canonical-main 最终重跑均为 `ACCEPTED`，分析器发现与 `oracle/*/expected-findings.json` 一致。WSL2 运行的 `strace` 见到 `config.h` 的 `openat`。canonical-main 报告 commit 与可远端 clone 的 main SHA 相同，报告 SHA-256 为 `7b021f47912e16bf43e084f23eaa7ecae59f42fa34a33f02b0c97b7ccdb00f22`。

MD/RD 项目先在 `evidence/run-20261010T043534Z-md-rd-main-29c02/` 的本地派生镜像中运行通过。B1 在提交 `fa07b7199e985b1dda63cc2efa467e5eb5a0f0ee` 增加专用环境包后，A 组按其 Dockerfile 独立重建并通过验收，见 `evidence/run-20261010T114727Z/`。A 组随后从 GHCR 按 digest 拉取 B1 原始镜像，核对 Registry digest、Image ID、源码 revision 和 `linux/amd64` 平台，并通过断网功能、MD stale/clean rebuild 和 RD rebuild 复测；最终接收记录为 `ACCEPTED`，见 `evidence/run-20261010T160627Z-ghcr/`。

上述结果不代表 BuildChecker 服务或 FULL_CHECK API 已实现。B2/B4 已有 candidate 继续绑定 standalone snapshot SHA，未由 canonical-main 报告自动替换。
