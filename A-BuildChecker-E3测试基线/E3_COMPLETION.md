# A 组 BuildChecker E3 完成情况

## 范围

BuildChecker 负责人完成分工图中的①和③。B1 已提交 MD/RD 专用环境包；A 组已从 GHCR 按固定 digest 拉取 B1 原始镜像，并通过镜像身份、源码基线、断网功能和 MD/RD 行为复测。E3-07 环境包验收及 Registry 接收回执完成。E3 不要求实现 DRAFT API。④⑤按各自角色跟踪。

## 状态

| 内容 | 状态 | 产物 |
| --- | --- | --- |
| MD/RD 项目、README、构建/验证命令、人工预期 | DONE | `fixtures/md-rd/`、`docs/a1-interface.md` |
| C0/C1/C2 版本计划与可复现提交 | DONE | `fixtures/commits/`，SHA 与 `commits.bundle` |
| 声明图、实际图、ERROR_REPORT | DONE | canonical-main `evidence/run-20261010T051714Z/`；B2 已接收的旧 standalone 报告保留于 `handoff/b2/` |
| 行为证据（MD 旧值、RD 多余编译、C2 增量 12 / 干净 19） | DONE | 同上 |
| B3 确认 DRAFT 能按本 README 运行 | WAITING | 已提供接口，待 B3 确认 |
| MD/RD 本地 DRAFT 环境消费与构建验证 | PASS_LOCAL | `evidence/run-20261010T043534Z-md-rd-main-29c02/`；基于可检出的 main SHA、B1 工具链基础镜像派生本地 MD/RD 镜像，`make` / `./app` 和 MD/RD 行为检查通过 |
| B1 MD/RD Dockerfile 与 runner 本地复验 | PASS_LOCAL | A 组在干净检出中复跑 `run_b1_md_rd.py`，本机构建和行为检查通过，记录见 `evidence/run-20261010T114727Z/` |
| B1 MD/RD 专用环境包验收与 GHCR 接收回执 | DONE | A 组按 digest 拉取 `ghcr.io/zaneow0/e3-buildchecker-md-rd@sha256:5be5d74a921c8600aeb4ac7a62bdea27f74521008264130039849b8309c285d6`；镜像身份与 B1 Image ID、RepoDigest、源码 revision 匹配；断网功能、MD stale/clean rebuild、RD rebuild 均通过，证据见 `evidence/run-20261010T160627Z-ghcr/` |
| E5 BuildChecker 服务 / FULL_CHECK API | 不做 | E3 不实现服务 |

原始 E3 基线运行 `run-20261005T071837Z` 结果为 `ACCEPTED`。方法2的最终 canonical-main 重跑见 `evidence/run-20261010T051714Z/`，结果为 `ACCEPTED`，MD/RD 报告使用唯一 `producer_job_id`，commit 为 `29c02d6604d7071d4b249ec958dd8a553caa670a`。MD/RD 本地镜像消费报告见 `evidence/run-20261010T043534Z-md-rd-main-29c02/DRAFT_ENVIRONMENT_VALIDATION.md`。
