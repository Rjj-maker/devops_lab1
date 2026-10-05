# A1：BuildChecker 检测项目与 README 定义

本文是 E3 中 A 组 BuildChecker 负责人的第一项交付，面向 B3（确认 DRAFT 能按同一份 README 取得并运行项目）以及后续全量检测。

它落实课件《E3 并行测试基线》A 组清单，不修改《接口定义文档 v0.2》的 Job、Artifact、错误码或端点。

## 1. 固定样例

| 项目 | 约定 |
| --- | --- |
| MD/RD 项目标识 | `e3-buildchecker-md-rd` |
| 提交链标识 | `e3-buildchecker-c0` / `c1` / `c2` |
| 样例版本 | `2026-09-10` |
| 项目根目录 | `A-BuildChecker-E3测试基线/fixtures/` |
| 构建环境 | Linux、GNU Make、C 编译器 |
| 网络要求 | 构建和功能验证不需要网络 |

样例版本对应 E3 PPT 日期，不是 Git SHA。运行记录还要保存：

```bash
git rev-parse HEAD
```

C0/C1/C2 的连续提交 SHA 由 `scripts/run_a_buildchecker.py` 写入 `evidence/run-*/commits/`。

## 2. 输入文件

相对各项目根目录：

| 项目 | 文件 |
| --- | --- |
| MD/RD | `main.c` `config.h` `unused.h` `Makefile` `README.md` `interface.json` |
| C0 | `main.c` `config.h` `Makefile` `README.md` `interface.json` |
| C1 / C2 | 以上加上 `feature.h`；C2 只改 Makefile 中的 `CFLAGS` |

`interface.json` 是接口元数据。构建不要改原始 fixtures，只在工作副本中执行。

## 3. 构建与验证

在项目根目录：

```bash
make
./app
```

| 项目 | 构建退出码 | 验证退出码 | 标准输出 |
| --- | --- | --- | --- |
| MD/RD 首次干净构建 | 0 | 0 | `1\n` |
| C0 干净构建 | 0 | 0 | `10\n` |
| C1 干净构建 | 0 | 0 | `12\n` |
| C2 干净构建 | 0 | 0 | `19\n` |
| C2 保留 C1 产物后的普通 make | 0 | 0 | `12\n` |

干净构建：

```bash
make clean
make
```

DRAFT 请求仍只提交 `build_command=make` 和 `test_command=./app`。`make clean` 是本地复跑步骤。

## 4. 人工预期发现

范围：只判断 `main.o` 的**项目头文件**。系统头文件不进入本答案集合。

| 版本 | MISSING | REDUNDANT |
| --- | --- | --- |
| MD/RD | `main.o` → `config.h` | `main.o` → `unused.h` |
| C0 | 无 | 无 |
| C1 | `main.o` → `feature.h` | 无 |
| C2 | 同上，仍然存在 | 无 |

C2 相对 C1 还有编译命令变化（`-DMODE=7`）。这不是 MD/RD 发现，留给增量检测比较命令快照。

## 5. 与 v0.2 FULL_CHECK 的对应

```json
{
  "job_type": "FULL_CHECK",
  "input": {
    "repository": {
      "project_root": "A-BuildChecker-E3测试基线/fixtures/md-rd"
    },
    "build": {
      "configuration_id": "cc-default",
      "clean_command": "make clean",
      "build_command": "make"
    }
  }
}
```

仓库 URL、完整 commit、环境和 Artifact URI 在运行记录中补齐。不能把本段当作一次已经成功的 Job。B1 的 Tiny Greeting 镜像是另一个项目，不能当作本 MD/RD 项目的 `image_ref`。

## 6. B3 需要确认的事项

1. 能按各项目 README 取得源码和 Makefile。
2. 在 Linux GNU Make / C 编译器环境下执行 `make` 与 `./app`。
3. 退出码和标准输出与上表一致。
4. 不要把“构建成功”解释成依赖声明正确。
