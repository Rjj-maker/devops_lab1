# MD/RD 故障项目

项目标识：`e3-buildchecker-md-rd@2026-09-10`。

完整接口见 [`interface.json`](interface.json) 和 [`../../docs/a1-interface.md`](../../docs/a1-interface.md)。

## 构建

```bash
make
```

成功条件：退出码为 `0`，并生成可执行文件 `app`。

## 功能验证

```bash
./app
```

成功条件：退出码为 `0`，标准输出严格为 `1` 加一个换行。

干净构建：

```bash
make clean
make
```

## 人工预期（本项目范围只看 `main.o` 的项目头文件）

- `MISSING`：`main.c` 读取 `config.h`，Makefile 未声明。
- `REDUNDANT`：Makefile 声明了 `unused.h`，源码未读取。
- 系统头文件（如 `stdio.h`）不进入本人工答案集合。

首次构建可以成功，不能据此判断依赖声明正确。
