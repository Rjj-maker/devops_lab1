# E3 BuildChecker 基线验证

## 固定信息

| 项目 | 值 |
| --- | --- |
| 仓库 URL | `https://github.com/Rowan-hhh/devops_lab1.git` |
| 有效运行 | `evidence/run-20261005T071837Z/` |
| MD/RD commit | `39430e3cdcf16403eec63bf592129b50ab1ff53d` |
| C0 / C1 / C2 | `4f985129bb100b082fe2cfb4f95f846d00752a25` / `9c3e06606aa42afef25c53dbb5eb0c5a6330e5ea` / `5efd7ece7569439950881a9b52b184356aa91687` |
| 构建命令 | `make clean && make` |
| 运行命令 | `./app` |

## 预期行为

- MD/RD：干净构建输出 `1`；把 `VALUE` 改为 `2` 后普通 make 仍为 `1`；再干净构建为 `2`；改 `unused.h` 触发重编译。
- C0 输出 `10`，无 MD/RD。C1 输出 `12`，缺少 `feature.h`。C2 干净构建 `19`，增量保留 C1 产物时为 `12`。

## 验证环境

WSL2 Ubuntu（`Linux 6.6.87.2-microsoft-standard-WSL2`，`x86_64`），GNU Make 4.3，Ubuntu cc 13.3.0，Python 3.12.3，Git 2.43.0。修改头文件后将其时间戳设为晚于 `main.o`，再执行普通 `make`。C2 增量实验保留 C1 的 `main.o`/`app`，并把目标文件时间调到源码之后，以避免“复制源码刷新时间戳”被误当成命令变化检测。

## 实际结果

与预期一致，`summary.json` 为 `ACCEPTED`。分析器发现与 `oracle/*/expected-findings.json` 一致。`strace` 见到 `config.h` 的 `openat`。

上述结果只验证 E3 测试基线和人工预期，不代表 BuildChecker 服务、DRAFT API 或 B4 验收已完成。
