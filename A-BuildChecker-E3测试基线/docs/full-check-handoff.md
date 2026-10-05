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

## 环境缺口

步骤②（DRAFT 环境消费）由 A 组环境负责人对接 B1。在 MD/RD 项目还没有对应 `image_ref` 之前，本基线在 Linux GNU Make / cc 上运行，并记录该限制。
