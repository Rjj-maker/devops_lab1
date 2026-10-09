# MD/RD 参考修复说明

- 报告：`A-BuildChecker-E3测试基线/handoff/b2/md-rd.error-report.json`
- Finding：`finding-e3-md-rd-missing-001`，`MISSING`，目标 `main.o` 缺少 `config.h`
- base commit：`39430e3cdcf16403eec63bf592129b50ab1ff53d`
- configuration_id：`cc-default`

`main.c` 包含 `config.h` 并读取其中的 `VALUE`，但原 Makefile 的 `main.o` 规则没有声明该依赖。Patch 只在依赖行增加 `config.h`，使配置头文件变化能够触发对象文件重编译。

`unused.h` 仍保留在 `main.o` 的依赖行中。它对应报告中的 `finding-e3-md-rd-redundant-001`（`REDUNDANT`），不属于本次 MDFixer 的 MISSING-only 修复范围。

预期首次构建程序输出 `1`；将 `config.h` 中 `VALUE` 改为 `2` 后，普通 `make` 重编 `main.o`，程序输出 `2`。仅修改 `unused.h` 也仍会触发重编译，以确认本 Patch 没有越权处理 RD。
