# C0：声明正确的初始版本

项目标识：`e3-buildchecker-c0@2026-09-10`。

`main.o` 声明 `main.c` 和 `config.h`。默认 `MODE=0`，干净构建后 `./app` 输出 `10`。

```bash
make clean && make
./app
```
