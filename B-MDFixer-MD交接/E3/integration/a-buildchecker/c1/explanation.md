# C1 参考修复说明

- 报告：`A-BuildChecker-E3测试基线/handoff/b2/c1.error-report.json`
- Finding：`finding-e3-c1-missing-001`，`MISSING`，目标 `main.o` 缺少 `feature.h`
- base commit：`9c3e06606aa42afef25c53dbb5eb0c5a6330e5ea`
- configuration_id：`cc-MODE0`

C1 的 `main.c` 包含 `feature.h` 并使用其中的 `FEATURE`，但原 Makefile 的 `main.o` 规则没有声明该依赖。Patch 只在依赖行增加 `feature.h`，不改其他依赖、配方、编译参数或规则。

预期在 base 上 clean build 后程序输出 `12`（`BASE=10`、`FEATURE=2`、`MODE=0`）。将 `feature.h` 中 `FEATURE` 改为 `3` 后，普通 `make` 应重编 `main.o`，程序输出 `13`。
