# 参考修复说明

这是 Missing Dependency：`main.c` 包含并读取 `config.h`，但 Makefile 中 `main.o` 只声明依赖 `main.c`。

首次构建能够成功，因为编译器编译 `main.c` 时会读取 `config.h`；缺少 Make 依赖声明不妨碍这次编译。之后只修改 `config.h`，普通 `make` 看不到已声明依赖变化，因此会保留旧的 `main.o` 和旧运行结果。

`reference.patch` 只把依赖声明从 `main.o: main.c` 改为 `main.o: main.c config.h`。修复后，`config.h` 更新会使 `main.o` 过期并触发重建，程序随之使用新的 `VALUE`。

MDFixer 只处理 `MISSING`。B4 后续负责正式 Patch 验证、无效候选拒绝和恢复；本参考答案不代表 B4 验收已完成。