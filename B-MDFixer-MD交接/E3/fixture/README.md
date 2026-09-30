# Missing Dependency 固定输入

在本目录执行：

```sh
make clean && make
./app
```

初始运行预期输出为 `1`，并以换行结束；程序退出码为 `0`。

## 缺失依赖

`main.o` 使用 `config.h` 中定义的 `VALUE`，但错误 Makefile 只声明 `main.o: main.c`，没有声明 `config.h`。正确依赖应为 `main.o: main.c config.h`。

首次构建仍能成功，是因为编译器处理 `main.c` 时会读取其包含的 `config.h`；缺少 Make 依赖声明不会阻止这次编译。

只修改 `config.h` 后，普通 `make` 不会重新编译 `main.o`，因为 Make 只检查已声明的 `main.c` 依赖，而它没有变化。已有的 `main.o` 和 `app` 会继续使用旧值。

执行 `make clean && make` 会删除 `app` 和 `main.o` 并重新编译，此时编译器读取更新后的 `config.h`，所以 clean build 可以看到新值。