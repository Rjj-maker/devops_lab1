# A 组 BuildChecker E3 完成情况

## 范围

BuildChecker 负责人完成分工图中的①和③。②④⑤不属于本次交付。

## 状态

| 内容 | 状态 | 产物 |
| --- | --- | --- |
| MD/RD 项目、README、构建/验证命令、人工预期 | DONE | `fixtures/md-rd/`、`docs/a1-interface.md` |
| C0/C1/C2 版本计划与可复现提交 | DONE | `fixtures/commits/`，SHA 与 `commits.bundle` |
| 声明图、实际图、ERROR_REPORT | DONE | `evidence/run-20261005T071837Z/` 与 `handoff/b2/` |
| 行为证据（MD 旧值、RD 多余编译、C2 增量 12 / 干净 19） | DONE | 同上 |
| B3 确认 DRAFT 能按本 README 运行 | WAITING | 已提供接口，待 B3 确认 |
| 在 B1 镜像中运行本项目 | BLOCKED | Tiny Greeting 不是本检测项目；步骤②由环境负责人对接 |
| E5 BuildChecker 服务 / FULL_CHECK API | 不做 | E3 不实现服务 |

有效运行 `run-20261005T071837Z` 结果为 `ACCEPTED`。
