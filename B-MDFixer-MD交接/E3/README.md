# B2 MDFixer E3 固定输入与参考答案

本目录用于保存 B2 的 MDFixer E3 固定输入、MD 报告与参考答案。

第一阶段固定的错误输入位于 [`fixture/`](fixture/)。报告和参考答案基于其 base commit。

base commit：`a98e84ca63d5869d7c29baba0817d249683a4ea1`

MDFixer 只处理 `MISSING` finding。B4 负责后续 Patch 验证、拒绝和恢复。

## 文件索引

- [`report/missing-dependency.error-report.json`](report/missing-dependency.error-report.json)：固定的 Missing Dependency 报告。
- [`answer/Makefile.fixed`](answer/Makefile.fixed)：修复后的 Makefile。
- [`answer/reference.patch`](answer/reference.patch)：针对固定 base commit 的参考 Patch。
- [`answer/explanation.md`](answer/explanation.md)：修复原因与预期行为。
- [`validation.md`](validation.md)：可重复验证步骤、环境和结果。
- [`AI_USAGE.md`](AI_USAGE.md)：AI 协助与人工确认记录。