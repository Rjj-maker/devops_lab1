# C0 / C1 / C2 版本计划

三次提交由 `scripts/run_a_buildchecker.py` 在工作副本中创建，并打上轻量标签 `C0` `C1` `C2`。作者日期固定为 `2026-09-10T00:00:00Z`，便于重复生成。真实 SHA 以 `evidence/run-*/commits/*.sha` 和 `commits.bundle` 为准。

| 标签 | 提交说明 | 相对上一版 |
| --- | --- | --- |
| C0 | 声明正确的初始版本 | — |
| C1 | 新增 `#include "feature.h"`，不改 Makefile | 源码变化；引入 MD |
| C2 | 只把 `CFLAGS` 改为带 `-DMODE=7` | 源码不变；MD 未消除；命令变化 |

EChecker 后续应以 C0 图为 baseline，C1 的 `repository.commit` 为新提交。C2 用于核对命令变化是否被普通时间戳检查漏掉。
