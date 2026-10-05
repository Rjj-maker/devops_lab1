# AI 使用记录

| 日期 | 工具 | 用途与人工确认 |
| --- | --- | --- |
| 2026-10-05 | Cursor（Grok 4.6） | 按 A 组 E3 分工图补齐 BuildChecker 的①检测项目/README 和③全量检测报告。人工确认：MD/RD 与 C0/C1/C2 行为与课件一致；C2 增量必须保留旧产物而不能只靠复制源码；报告 `detector` 保持 `INSTRUCTOR_ORACLE`；不把 B1 Tiny Greeting 镜像当成本项目环境；不实现 E5 服务。 |

关联文件：

- 项目与接口：[`README.md`](README.md)、[`docs/a1-interface.md`](docs/a1-interface.md)、[`fixtures/`](fixtures/)
- 人工预期：[`oracle/`](oracle/)、[`docs/md-rd-oracle.md`](docs/md-rd-oracle.md)
- 运行器与证据：[`scripts/run_a_buildchecker.py`](scripts/run_a_buildchecker.py)、[`evidence/run-20261005T071837Z/`](evidence/run-20261005T071837Z/)
- B2 交接：[`handoff/b2/`](handoff/b2/)

主要验证命令：`python3 A-BuildChecker-E3测试基线/scripts/run_a_buildchecker.py --check-only`，以及在 WSL 中去掉 `--check-only` 的完整运行。
