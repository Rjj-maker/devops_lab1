# 当前有效运行结果

最新有效运行目录：

```text
evidence/run-20261005T071837Z/
```

结果为 `ACCEPTED`。运行环境为 WSL2 Ubuntu、GNU Make 4.3、cc 13.3.0、Python 3.12.3、x86_64。`strace` 记录到编译器 `openat` 读取 `config.h`。

## MD/RD

| 检查 | 预期 | 实际 |
| --- | --- | --- |
| 首次 `./app` | `1\n` | 匹配 |
| 只改 `config.h` 后普通 make | 仍为 `1\n` | 匹配 |
| `make clean && make` | `2\n` | 匹配 |
| 只改 `unused.h` | 再次 `cc -c main.c` | 匹配 |
| 发现 | MD `config.h`，RD `unused.h` | 与 oracle 一致 |

MD/RD 样例提交：`39430e3cdcf16403eec63bf592129b50ab1ff53d`（`md-rd.bundle`）。

## C0 / C1 / C2

| 版本 | SHA | 干净构建输出 | 发现 |
| --- | --- | --- | --- |
| C0 | `4f985129bb100b082fe2cfb4f95f846d00752a25` | `10` | 无 |
| C1 | `9c3e06606aa42afef25c53dbb5eb0c5a6330e5ea` | `12` | MD `feature.h` |
| C2 | `5efd7ece7569439950881a9b52b184356aa91687` | `19` | 上述 MD 仍在 |

C2 保留 C1 产物后普通 make：`Nothing to be done for 'all'`，`./app` 输出 `12`。随后干净构建输出 `19`。

C0→C1 引入 `main.o` 缺少 `feature.h`。C1→C2 该发现未变化。

## 历史运行

| 目录 | 结果 | 说明 |
| --- | --- | --- |
| `run-20261005T071651Z` | 中断 | 写 C0 SHA 前未创建 `commits/` 目录 |
| `run-20261005T071754Z` | `REJECTED` | 复制 C2 源码刷新了 `main.c` 时间戳，增量误重建 |

上述失败目录保留，不覆盖。

本结果不是 DRAFT API、不是 E5 检测服务，也不表示 B1 Tiny Greeting 镜像已绑定到本项目。
