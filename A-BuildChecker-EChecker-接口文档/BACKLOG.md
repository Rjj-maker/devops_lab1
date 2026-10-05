# Backlog — DevOps 教学实验

## 使用说明

- 每项任务有负责人、产物和验收条件
- 状态：`TODO` / `IN_PROGRESS` / `DONE` / `BLOCKED`
- 优先级：P0（必须）/ P1（重要）/ P2（可选）

---

## E2 任务（接口契约）

| ID | 任务 | 责任方 | 产物 | 验收条件 | 状态 |
|----|------|--------|------|----------|------|
| E2-01 | 统一任务模型（四类 Job） | A+B 共同 | 仓库根目录 `ab-job-contract.schema.json` | 四类对象可表达；Schema 符合 Draft 2020-12；非法 `job_type` 被拒绝 | DONE |
| E2-02 | BuildChecker 接口定义 | A 组 | FULL_CHECK 请求、回执和响应样例 | 请求包含环境与构建配置；成功输出包含两张图、ERROR_REPORT 和正确计数；失败输出为 `null` | DONE |
| E2-03 | EChecker 接口定义 | A 组 | INCREMENTAL_CHECK 请求、回执和响应样例 | 携带 baseline；样例中 `baseline.commit == base_commit` 且 `repository.commit != base_commit`；成功输出引用更新图和发现变化 | DONE |
| E2-04 | ERROR_REPORT 格式定义 | A 组 | MISSING/RD 发现样例 | 含 `finding_id`、类型、target、dependency、完整 commit、位置和 evidence；固定预期发现标记 `INSTRUCTOR_ORACLE` | DONE |
| E2-05 | 产物访问约定 | A+B 共同 | ADR + 契约样例 | 说明 `artifact://` 到共享相对路径的映射、元数据与摘要核验；双方确认访问方案 | IN_PROGRESS |
| E2-06 | Artifact 共享机制 | A+B 共同 | 共享目录、权限和 SHA-256 约定 | 确认共享位置与读写权限；双方按 URI 找到并读取文件 | BLOCKED |
| E2-07 | 与 B 组三轮配对练习 | A+B 共同 | 三轮讨论记录及双方确认的接口样例 | 覆盖环境/基线、MISSING 报告和失败输入，保留双方确认记录 | BLOCKED |
| E2-08 | ADR 记录 | A+B 各自 | ADR 文档 | 记录异步 Job 决策及替代方案、理由和后果 | DONE |
| E2-09 | 个人贡献记录 | 各自 | Git 提交；如有 Issue/PR 则保留链接 | 提交含作者、SHA 和说明；贡献可由本地历史追溯 | DONE |
| E2-10 | A 组样例 Schema 与静态一致性校验 | A 组 | `E2_COMPLETION.md` 中的校验结果 | A 组有效样例通过对应 `$defs`；非法任务类型和缺少 baseline 的样例被拒绝；跨字段关系通过静态检查 | DONE |
| E2-11 | E2 完成情况登记 | A+B 共同 | 完成情况说明 | 登记已完成内容、验证结果、未完成项、原因和下一步 | IN_PROGRESS |

---

## E3 任务（并行测试基线）

| ID | 任务 | 责任方 | 产物 | 验收条件 | 状态 |
|----|------|--------|------|----------|------|
| E3-01 | MD/RD 项目准备 | A 组 BuildChecker | `A-BuildChecker-E3测试基线/fixtures/md-rd/` | 可 `make && ./app`；含一条 MD 和一条 RD 及人工依据 | DONE |
| E3-02 | C0/C1/C2 提交版本 | A 组 BuildChecker | `fixtures/commits/` 与 `evidence/run-*/commits/*.sha` | 三个连续 commit 可追溯；C1 引入 MD，C2 只改命令 | DONE |
| E3-03 | 基线依赖图 | A 组 BuildChecker | C0 `actual.json` / `declared.json` | C0 无 MD/RD；图只覆盖 `main.o` 项目头文件 | DONE |
| E3-04 | 增量检测基线 | A 组 BuildChecker | `commits/c0-to-c1-delta.json` | C1 相对 C0 新增 `feature.h` 缺失；C2 该发现未消除 | DONE |
| E3-05 | 并行测试执行 | A 组 BuildChecker | `evidence/run-20261005T071837Z/summary.json` | 基线行为与 oracle 一致，结果 `ACCEPTED`。不含 E5 服务和 B4 Patch 复核 | DONE |

---

## 已完成

- E2-01 统一任务模型：根目录 `ab-job-contract.schema.json` 已提交，Schema 本身通过 Draft 2020-12 检查。
- E2-02 BuildChecker：FULL_CHECK 请求、202 回执、成功和失败 Job 样例已提交。
- E2-03 EChecker：INCREMENTAL_CHECK 请求、202 回执和成功 Job 样例已提交。
- E2-04 ERROR_REPORT：样例包含一条 MISSING 和一条 REDUNDANT 发现；固定预期发现标记为 `INSTRUCTOR_ORACLE`。
- E2-08 异步 Job 决策记录见 `ADR-001-async-job.md`。
- E2-10 A 组样例通过对应 Schema `$defs` 校验；缺少 `baseline` 和非法 `job_type` 的输入按预期被拒绝。baseline 与 base commit、Job/报告字段及计数的静态一致性检查见 `E2_COMPLETION.md`。
- E2-11 A 组完成情况见 `E2_COMPLETION.md`。B 组确认项仍未完成。
- E3-01～E3-05 BuildChecker 测试基线见 `A-BuildChecker-E3测试基线/`。有效运行 `evidence/run-20261005T071837Z/` 为 `ACCEPTED`。B3 确认、B1 为本项目提供镜像、B4 Patch 复核仍待对方。

## 未完成或受外部确认阻塞

| 任务 | 当前状态 | 原因 | 下一步 |
|------|----------|------|--------|
| E2-05 产物访问约定 | IN_PROGRESS | A 组已提出 ADR-002；配对 B 组尚未确认 | 与 B 组逐项确认映射和接收方核验规则，再将 ADR 更新为双方接受的状态 |
| E2-06 Artifact 共享机制 | BLOCKED | 真实 `pair_id`、共享位置、读写权限和同步方式尚未确认 | 确认同号配对组和共享方案后更新 `docs/instance-values.md`，再验证双方读取 |
| E2-07 三轮配对练习 | BLOCKED | 当前仓库没有可核对的三轮讨论记录或双方确认记录 | 与配对 B 组完成并保存三轮记录 |
| E2-11 双组完成情况登记 | IN_PROGRESS | 本文件和 A 组完成情况已经记录；B 组状态及双方共同确认尚未登记 | 汇总 B 组交付与双方验收结果 |
| E3 B3 确认检测项目 README | WAITING | BuildChecker 接口已交付，B3 尚未确认 DRAFT 可按同一 README 运行 | B3 按 `A-BuildChecker-E3测试基线/docs/a1-interface.md` 确认 |
| E3 DRAFT 环境绑定 MD/RD 项目 | BLOCKED | 步骤②由 A 组环境负责人对接 B1；Tiny Greeting 不是本检测项目 | 为本项目提供 Dockerfile/`image_ref` 后再在该环境复跑 |
| E3 Patch 验证与失败恢复 | BLOCKED | 步骤④由 A 组检测/复核负责人对接 B4 | B4 提供候选 Patch 与拒绝恢复记录后复核 MD/RD |

`pair03` 等联调实例值仍为占位，直到双方确认。E3 BuildChecker 基线的真实 SHA 与运行记录见 `A-BuildChecker-E3测试基线/evidence/`。
