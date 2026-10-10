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

## 报告 commit 边界

本目录报告仍绑定 standalone MD/RD snapshot commit `39430e3cdcf16403eec63bf592129b50ab1ff53d`，并与现有 B2/B4 candidate base 对应。A 组另有 canonical-main 环境验证报告 `A-BuildChecker-E3测试基线/evidence/run-20261010T051714Z/md-rd/artifacts/error-report.json`，绑定 commit `29c02d6604d7071d4b249ec958dd8a553caa670a`。两份报告项目文件内容一致但 Git commit identity 不同。本目录文件未被覆盖；B2/B4 继续基于本目录时，不应混用 canonical-main 报告。若切换 canonical-main 报告，必须同步重新建立 Patch candidate base 并重新执行 B4 验证。
