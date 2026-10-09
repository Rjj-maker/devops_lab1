# 人工预期与判断依据

本文件只解释 **INSTRUCTOR_ORACLE**。不要把它算进后续工具准确率。

## MD/RD

`main.c` 包含 `config.h` 并打印 `VALUE`。Makefile 为：

```text
main.o: main.c unused.h
```

| 发现 | 依据 | 行为证据 |
| --- | --- | --- |
| MD：`config.h` | 实际读取，未声明 | 把 `VALUE` 改为 `2` 后普通 `make` 仍输出 `1`；`make clean && make` 输出 `2` |
| RD：`unused.h` | 已声明，未读取 | 只改 `unused.h` 注释会触发 `cc -c main.c` |

## C0 / C1 / C2

| 版本 | 源码 | Makefile | 干净输出 | 预期发现 |
| --- | --- | --- | --- | --- |
| C0 | `BASE + MODE`，默认 MODE=0 | `main.o: main.c config.h` | 10 | 无 MD/RD |
| C1 | 增加 `feature.h`，`BASE + FEATURE + MODE` | 仍为 C0 的声明 | 12 | MD：`feature.h` |
| C2 | 与 C1 相同 | `CFLAGS` 增加 `-DMODE=7` | 19 | 上述 MD 仍在 |

C1 输出 12 不能说明没有 MD。随后只改 `feature.h` 才会表现漏重建。C2 保留 C1 产物时普通 make 仍可能输出 12。
