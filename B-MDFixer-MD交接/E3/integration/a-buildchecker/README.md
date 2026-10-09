# A BuildChecker -> B2 MDFixer E3 联调

本目录保存 A 组 BuildChecker 向 B2 MDFixer 交接的 E3 联调成果，与 `B-MDFixer-MD交接/E3/` 下 B2 原有固定 oracle 样例并行存在，不得混用报告、base commit、Makefile 或 Patch。

本阶段包括 A 组原始报告的接收记录、MD/RD 和 C1 两套参考 Patch、修复后 Makefile、candidate 映射、candidate bundles 和 B2 自测。报告只通过 A 组原始路径和 SHA-256 引用，不复制报告。

交接索引见 [`candidate-map.md`](candidate-map.md)，B4 操作说明见 [`handoff-b4.md`](handoff-b4.md)。两个候选及其 bundle 已生成并从全新 clone 完成 B2 自测；正式 B4 recheck 仍为 `PENDING`。A 组原始目录由 A 组维护，B2 不修改其中内容。
