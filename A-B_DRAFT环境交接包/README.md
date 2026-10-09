# DRAFT–BuildChecker 环境交接包

本材料依据《接口定义文档 v0.2》，不替代原接口文档。

本目录用于帮助 A/B 双方按既有接口契约完成 DRAFT 环境到 BuildChecker 的交接。它只提取环境交接所需的规则、待确认的实例值和 JSON 结构样例，不重新设计 Job、Artifact、错误码、端点或字段语义。

如本材料与《接口定义文档 v0.2》存在不一致，以原接口文档为准。接口基线见 [`../接口定义文档_v0.2.md`](../接口定义文档_v0.2.md)。

## 当前状态

本包不表示真实联调已经完成。当前真实状态如下：

| 项目 | 状态 |
| --- | --- |
| E03 Tiny Greeting 项目输入和命令 | 已提交；`make` 与 `./hello` 已按 B3 约定核对 |
| B1 失败/参考构建和当前提交验证 | 已通过；最新运行结果为 `ACCEPTED`，记录见 `B1-DRAFT环境/evidence/FINAL_RESULT.md` |
| 最新 B1 运行的代码基准 | `36f6dd61689f9cdf087d0f83a7d60d6d05db2225`；B1 输入及 Dockerfile 摘要见运行 `summary.json` |
| A 组取得相同参考镜像 | 待确认；当前只有本地镜像信息，没有 Registry 发布或 A 组拉取记录 |
| E03 最终项目仓库、commit 与项目目录 | 待确认；Tiny Greeting 是课程固定样例 |
| E03 最终项目构建与测试命令 | 待确认；当前已核对的是 Tiny Greeting 样例命令 |
| Artifact 共享位置和访问权限 | 待确认 |
| DRAFT API 的真实 Job 与 Artifact 交付 | 待确认；当前记录是 Docker 样例运行，不是 API 联调 |

本包包含 B1 样例 Dockerfile、日志和镜像检查记录，但不包含可直接拉取的镜像本体、Registry 发布证明、真实 DRAFT API Job 或跨组 Artifact 读取证明。

## 文件索引

- [`docs/environment-handoff.md`](docs/environment-handoff.md)：环境交接所需的契约规则及核对点。
- [`docs/instance-values.md`](docs/instance-values.md)：真实联调参数表；未确定内容统一标记为“待确认”。
- [`docs/b3-interface.md`](docs/b3-interface.md)：B3 负责的具体 DRAFT 输入、构建/验证命令和预期结果。
- [`B1-DRAFT环境/README.md`](B1-DRAFT环境/README.md)：B1 的失败构建样例、参考镜像构建和运行证据。
- [A 组 B1 环境验收记录](../A-BuildChecker-EChecker-接口文档/docs/B1-DRAFT环境验收.md)：A 组对样例、版本追溯和镜像交接的核对结果。
- [`fixtures/draft/README.md`](fixtures/draft/README.md)：Tiny Greeting 项目级 README。
- [`fixtures/draft/interface.json`](fixtures/draft/interface.json)：供 BuildChecker 读取的机器可读接口约定。
- [`examples/README.md`](examples/README.md)：JSON 示例的占位值和使用限制。
- `examples/*.example.json`：DRAFT 请求、回执、Job 结果及 FULL_CHECK 请求的结构样例。

建议先阅读本文件，再阅读环境交接说明和实例值表，最后查看 JSON 结构样例。

## 示例值声明

所有 `.example.json` 文件仅用于说明 v0.2 的既有结构。JSON 中的仓库 URL、commit、`sha256` 和镜像 digest 都是结构占位值：

- `example.com` 是示例域名；
- `0123456789abcdef0123456789abcdef01234567` 是示例完整 commit；
- 重复字符组成的 64 位 `sha256` 和镜像 digest 是示例值；
- `pair03`、示例 `job_id`、`trace_id` 和时间均为结构占位值；
- `make`、`make test`、`make clean` 和 `cc-MODE0` 是结构占位值，并不表示双方已经选定这些命令或配置。

结构样例不能作为真实运行证据。实际值及确认状态只在 `docs/instance-values.md` 中记录。

## 使用边界

- 不在本包中修改接口字段、枚举值、状态流转、错误码或端点。
- 不把运行配置新增为接口字段。
- 不使用 `.example.json` 声称服务已经受理、构建、测试、发布镜像或完成检测。
- 真实文件产物必须按 v0.2 的 `artifact://` 规则交接，并由接收方核对其内容和元数据。
