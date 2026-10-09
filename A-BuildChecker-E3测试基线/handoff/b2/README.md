# B2 交接：完整检测报告

B2 只从完整 ERROR_REPORT 中选择 `MISSING`。不要选择 `REDUNDANT`。

当前有效运行：`evidence/run-20261005T071837Z/`（`ACCEPTED`）。

| 文件 | 内容 | B2 应选 |
| --- | --- | --- |
| `md-rd.error-report.json` | MD：`config.h`；RD：`unused.h` | `finding-e3-md-rd-missing-001` |
| `c1.error-report.json` | MD：`feature.h` | `finding-e3-c1-missing-001` |
| `md-rd.actual.json` / `md-rd.declared.json` | 实际图 / 声明图 | 修复不消费图，仅核对应 |

对应 Makefile 在 `fixtures/md-rd/Makefile` 与 `fixtures/commits/C1/Makefile`。参考修复由 B2 产出，不在本目录。

这些报告的 `detector` 为 `INSTRUCTOR_ORACLE`（E3 基线分析与人工预期一致），不代表 E5 BuildChecker 服务已实现。
