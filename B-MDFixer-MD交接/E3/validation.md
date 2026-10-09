# E3 固定输入与参考答案验证

## 固定信息

| 项目 | 值 |
| --- | --- |
| 仓库 URL | `https://github.com/Rowan-hhh/devops_lab1.git` |
| base commit | `a98e84ca63d5869d7c29baba0817d249683a4ea1` |
| configuration_id | `cc-c11-default` |
| 构建命令 | `make clean && make` |
| 运行命令 | `./app` |

## 预期行为

- 修复前首次 clean build 成功，程序输出 `1`。将 `config.h` 的 `VALUE` 改为 `2` 后，普通 `make` 不重编 `main.o`，程序仍输出 `1`；再 clean build 后输出 `2`。
- 应用参考 Patch 后首次 clean build 成功，程序输出 `1`。将 `VALUE` 改为 `3` 后，普通 `make` 重编 `main.o`，程序输出 `3`。

## 验证环境

本次在 macOS 临时 Git worktree（从上述 base commit detached 创建）中验证，使用 GNU Make 3.81、Apple clang 21.0.0、Python 3.14.6 和 Git 2.50.1 (Apple Git-155)。为避免 GNU Make 3.81 的秒级时间戳精度使快速编辑与编译落在同一秒，修改临时 `config.h` 后将其时间戳设为晚于 `main.o`，并将临时 `app` 时间设为早于 `main.o`，再执行普通 `make`；这样可确定性地检查对象重编译及可执行文件重链接。报告 JSON 使用 Python 标准库解析和检查；没有安装额外依赖。

## 实际结果

- 修复前：`make clean && make` 成功，`./app` 输出 `1`，退出码为 `0`。将 `VALUE` 改为 `2` 并确保头文件时间戳晚于 `main.o`、可执行文件时间早于 `main.o` 后，普通 `make` 不重编 `main.o`，程序仍输出 `1`，退出码为 `0`。再次 clean build 后程序输出 `2`，退出码为 `0`。
- 修复后：`git apply --check` 通过，Patch 仅增加 `config.h` 依赖，应用后的 Makefile 与 `answer/Makefile.fixed` 字节一致。首次 clean build 成功，程序输出 `1`。将 `VALUE` 改为 `3` 并确保头文件时间戳晚于 `main.o`、可执行文件时间早于 `main.o` 后，普通 `make` 重编 `main.o` 并重链接 `app`，程序输出 `3`，退出码为 `0`。

上述结果只验证固定样例和参考 Patch，不代表 BuildChecker、MDFixer 已实现，也不代表 B4 正式验收、无效候选拒绝或恢复流程已完成。