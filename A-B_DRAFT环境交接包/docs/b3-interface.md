# B3：DRAFT 接口与 README 定义

本文是 E3 第一阶段 B3 的具体交付，面向 A 组 BuildChecker 和 B 组后续环境、失败样例及修复验证。
它落实《接口定义文档 v0.2》中的 DRAFT `build_command`、`test_command` 和项目输入约定，不修改 v0.2 的 Job、Artifact、错误码或端点定义。

## 1. 固定样例

| 项目 | 约定 |
| --- | --- |
| 项目标识 | `e3-draft-tiny-greeting` |
| 样例版本 | `2026-09-06` |
| 项目根目录 | `A-B_DRAFT环境交接包/fixtures/draft/` |
| 构建环境 | Linux、GNU Make、C 编译器 |
| 网络要求 | 构建和功能验证不需要网络 |

样例版本对应 E3 PPT 中 Tiny Greeting 参考样例的日期。它不是 Git SHA；若运行目录位于 Git 仓库，运行记录还应保存：

```bash
git rev-parse HEAD
```

## 2. 输入文件

BuildChecker 处理以下相对项目根目录的文件：

```text
main.c
Makefile
README.md
interface.json
```

其中 `interface.json` 是接口元数据，`main.c` 和 `Makefile` 是构建所需输入，`README.md` 是项目级运行说明。
BuildChecker 不应修改原始输入，应在新的工作副本中执行构建和验证。

## 3. DRAFT 构建接口

在项目根目录执行：

```bash
make
```

构建成功必须同时满足：

1. `make` 退出码为 `0`。
2. 生成名为 `hello` 的可执行文件。
3. `hello` 可以被当前 Linux 环境直接执行。

需要验证干净构建时执行：

```bash
make clean
make
```

`make clean` 删除 `hello` 后应退出码为 `0`。按照 v0.2，DRAFT 请求只提交 `build_command` 和 `test_command`；`make clean` 是本地复跑步骤，不新增接口字段。

## 4. 功能验证接口

构建成功后执行：

```bash
./hello
```

预期结果：

| 项目 | 预期值 |
| --- | --- |
| 进程退出码 | `0` |
| 标准输出 | 严格为 `hello E3` 加一个换行，即 `hello E3\\n` |
| 标准错误 | 不作内容断言，但必须保留原始记录 |

除末尾换行外，不接受额外字符、额外空格或额外输出。构建成功不等于功能验证成功，DRAFT 只有构建和测试退出码都为 `0` 才能判定成功。

## 5. 与 v0.2 DRAFT 请求的对应关系

本样例的请求字段取值如下，具体请求仍须遵守 v0.2 的完整结构和幂等要求：

```json
{
  "job_type": "DRAFT",
  "input": {
    "repository": {
      "project_root": "A-B_DRAFT环境交接包/fixtures/draft"
    },
    "build": {
      "build_command": "make",
      "test_command": "./hello"
    }
  }
}
```

仓库 URL、完整 commit、`trace_id`、limits 和创建请求头由实际联调记录补齐。不能把本段片段当作完整请求，也不能把样例版本当作 commit SHA。

## 6. 运行证据

每次运行至少保存：

- 实际命令、工作目录和项目版本
- Git SHA（如果可用）
- 操作系统、CPU 架构、编译器版本和 GNU Make 版本
- 构建 stdout、stderr、退出码
- 功能验证 stdout、stderr、退出码
- `hello` 是否存在及是否可执行

失败时还要保存失败命令、原始日志和对应版本。B1 的 `Dockerfile.broken`、`Dockerfile.reference`、镜像信息和运行记录见 [`B1-DRAFT环境/README.md`](../B1-DRAFT环境/README.md) 及 [A 组交叉验收记录](../../A-BuildChecker-EChecker-接口文档/docs/B1-DRAFT环境验收.md)。本文件只定义项目接口，不替代 B1 的运行证据。


## 7. B1 环境交接状态

B1 已基于本接口准备 `Dockerfile.broken` 和 `Dockerfile.reference`。最新运行已从当前 B1 提交完成失败构建、参考构建、工具版本和功能验证；A 组交叉验收确认样例符合本接口定义。版本追溯和镜像跨组取得状态见 [B1 DRAFT 样例环境验收记录](../../A-BuildChecker-EChecker-接口文档/docs/B1-DRAFT环境验收.md)。

该验收只覆盖 Tiny Greeting 固定样例。镜像 Registry 发布和 A 组按 digest 获取尚未验证。E03 最终项目、BuildChecker 检测实现以及 C0/C1/C2 版本不由本接口样例代替。
