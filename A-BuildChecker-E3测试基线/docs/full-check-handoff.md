# BuildChecker 全量检测交接（给 B2）

A 组在 E3 产出完整 ERROR_REPORT，以及 `actual.json` / `declared.json`。B2 只接收完整报告，并从中选择 `type=MISSING` 进入修复流程，不要选择 `REDUNDANT`。

## 当前交付

| 项目 | 报告 | B2 应选择的 finding |
| --- | --- | --- |
| MD/RD | `evidence/run-*/md-rd/artifacts/error-report.json` | `config.h` 的 MISSING |
| C1 / C2 | `evidence/run-*/commits/C1/artifacts/error-report.json` | `feature.h` 的 MISSING |

固定给 MDFixer 先行验证的另一份样例仍以 B2 目录 [`B-MDFixer-MD交接/E3/`](../../B-MDFixer-MD交接/E3/) 为准。那份报告是 B2 的固定输入，不是本次 A 组检测器服务的输出。

## 图的范围

- 目标：`main.o`
- 实际图：`main.c` 的引号 include 闭包（项目头文件）
- 声明图：Makefile 中 `main.o` 的前置依赖
- 系统头文件不进入比较

这是 E3 基线分析，不是 E5 的 BuildChecker 服务，也不使用 B1 Tiny Greeting 镜像。

## 环境消费与报告版本

A 组环境负责人已按方法2选择可远端 clone 的 main commit `29c02d6604d7071d4b249ec958dd8a553caa670a`，并基于该提交的 `A-BuildChecker-E3测试基线/fixtures/md-rd` 生成 canonical-main MD/RD 报告。MD/RD DRAFT-compatible 本地镜像与行为复核见 [`evidence/run-20261010T043534Z-md-rd-main-29c02/`](../evidence/run-20261010T043534Z-md-rd-main-29c02/)；full baseline 运行见 [`evidence/run-20261010T051714Z/`](../evidence/run-20261010T051714Z/)。

B1 已提交 MD/RD 专用环境包。A 组已从 GHCR 按固定 digest 拉取 B1 原始镜像，核对 Image ID、RepoDigest、源码 revision 和平台，并通过断网及 MD/RD 行为复测；接收记录为 `ACCEPTED`，见 [`evidence/run-20261010T160627Z-ghcr/`](../evidence/run-20261010T160627Z-ghcr/) 和 [`A_CROSS_MACHINE_RECEIPT.md`](../evidence/run-20261010T160627Z-ghcr/A_CROSS_MACHINE_RECEIPT.md)。E3 不要求部署 DRAFT API。

`handoff/b2/` 现有报告和 B2/B4 candidate 仍绑定 standalone snapshot commit `39430e3cdcf16403eec63bf592129b50ab1ff53d`。canonical-main 报告绑定 `29c02d6604d7071d4b249ec958dd8a553caa670a`。两者代码内容一致；B2 若切换新报告，需要同步迁移 candidate base 和 B4 验证，不要混用两个 commit。
