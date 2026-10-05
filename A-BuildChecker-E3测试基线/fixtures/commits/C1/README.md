# C1：新增 include，未补 Makefile

项目标识：`e3-buildchecker-c1@2026-09-10`。

`main.c` 增加 `#include "feature.h"`。Makefile 仍是 `main.o: main.c config.h`。

干净构建后 `./app` 输出 `12`。输出正确不表示没有缺失依赖。预期发现：`main.o` 缺少 `feature.h`。
