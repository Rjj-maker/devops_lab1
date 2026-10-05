# C2：只改变编译命令

项目标识：`e3-buildchecker-c2@2026-09-10`。

源码与 C1 相同。`CFLAGS` 增加 `-DMODE=7`。`feature.h` 的缺失依赖仍然存在。

保留 C1 的 `main.o` 和 `app` 后执行普通 `make`，预期仍输出 `12`。`make clean && make` 后输出 `19`。
