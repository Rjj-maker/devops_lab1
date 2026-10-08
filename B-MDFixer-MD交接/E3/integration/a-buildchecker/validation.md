# A BuildChecker E3 Patch 自测记录

## 验证环境

- macOS 26.5.1
- GNU Make 3.81
- Apple clang 21.0.0 (`clang-2100.1.1.101`)
- Python 3.14.6
- Git 2.50.1 (Apple Git-155)
- 所有 bundle clone、临时源码修改和构建均在 `${TMPDIR:-/tmp}/b2-a-integration-*` 下完成，未在仓库内构建。

## 输入与基线

| 样例 | bundle | base commit | Patch |
|---|---|---|---|
| MD/RD | `A-BuildChecker-E3测试基线/evidence/run-20261005T071837Z/md-rd/md-rd.bundle` | `39430e3cdcf16403eec63bf592129b50ab1ff53d` | `md-rd/reference.patch` |
| C1 | `A-BuildChecker-E3测试基线/evidence/run-20261005T071837Z/commits/commits.bundle` | `9c3e06606aa42afef25c53dbb5eb0c5a6330e5ea` | `c1/reference.patch` |

两份源报告均通过 `python3 -m json.tool ... >/dev/null`，退出码为 0。C1 clone 后显式 detached checkout 到 C1 base，没有使用 bundle 默认指向的 C2。

## MD/RD

- `git apply --check` 通过；应用后 `git diff --name-only` 仅为 `Makefile`，应用后的文件与 `md-rd/Makefile.fixed` 字节一致。
- `make clean && make` 退出码为 0；`./app` 退出码为 0，输出 `1`。
- 将 `config.h` 的 `VALUE` 从 1 改为 2，并用 `touch -t` 将头文件时间设为晚于 `main.o`；普通 `make` 输出编译 `main.c` 的命令，`./app` 退出码为 0，输出 `2`。
- 修改 `unused.h` 并将其时间设为晚于 `main.o`；普通 `make` 再次编译 `main.c`。修复后的规则仍为 `main.o: main.c unused.h config.h`，确认 REDUNDANT 未被修复。

## C1

- `git apply --check` 通过；应用后 `git diff --name-only` 仅为 `Makefile`，应用后的文件与 `c1/Makefile.fixed` 字节一致。
- `make clean && make` 退出码为 0；`./app` 退出码为 0，输出 `12`。
- 将 `feature.h` 的 `FEATURE` 从 2 改为 3，并用 `touch -t` 将头文件时间设为晚于 `main.o`；普通 `make` 输出编译 `main.c` 的命令并成功重链接，`./app` 退出码为 0，输出 `13`。

## 清理与范围

- 两个 candidate commit 仅在系统临时 clone 中创建；候选 bundle 导出后，临时候选仓库已删除。
- 从每个 candidate bundle 创建全新 clone，核对 candidate SHA、parent、仅 `Makefile` 变更、`Makefile.fixed` 字节一致及初始工作区干净。
- 从候选 bundle 新 clone 完成上述两组 clean build、运行和头文件增量测试；临时 clone 与构建产物均已删除。
- 正式 B4 recheck 尚未执行，状态为 `PENDING`。
- 未修改 A 组目录或本次明确排除的其他路径。

## Candidate 阶段验证

| 样例 | candidate | parent | bundle verify/ref | 新 clone clean build / 初始输出 | 增量结果 |
|---|---|---|---|---|---|
| MD/RD | `37382e088e26b2827c3d9f7d4c5238d3d39d893f` | `39430e3cdcf16403eec63bf592129b50ab1ff53d` | PASS；`refs/heads/candidate/b2-md-rd` 指向 candidate，完整历史 | 退出码 0；输出 `1` | `config.h` 变化后重编译、输出 `2`；`unused.h` 仍声明且变化后重编译 |
| C1 | `d5d1d4a5a232094b1c2a5a74aadf3932b5ddedcf` | `9c3e06606aa42afef25c53dbb5eb0c5a6330e5ea` | PASS；`refs/heads/candidate/b2-c1` 指向 candidate，完整历史 | 退出码 0；输出 `12` | `feature.h` 变化后重编译、输出 `13` |

增量测试使用 Python `os.utime` 将被修改头文件的 mtime 设置为晚于 `main.o`，并断言时间顺序；普通 `make` 输出了 `main.c` 的编译命令。两个候选均只修改 `Makefile`，且从 bundle 新 clone 后与对应 `Makefile.fixed` 字节一致。
