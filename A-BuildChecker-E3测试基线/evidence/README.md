# 运行记录说明

`run_a_buildchecker.py` 默认创建 `run-YYYYMMDDTHHMMSSZ/`。每次使用新目录，不覆盖已有记录。

一次完整运行至少包含：

```text
summary.json
env.json
static-check.json
env/make-version.*
env/cc-version.*
md-rd/build.*
md-rd/verify.*
md-rd/md-incremental-verify.*
md-rd/md-clean-verify.*
md-rd/rd-incremental.*
md-rd/artifacts/actual.json
md-rd/artifacts/declared.json
md-rd/artifacts/error-report.json
commits/C0.sha
commits/C1.sha
commits/C2.sha
commits/commits.bundle
commits/c0-to-c1-delta.json
commits/c1-to-c2-delta.json
commits/C2-incremental/C2-incremental-verify.stdout.log
```

## 结果核对

- `summary.json` 的 `result` 为 `ACCEPTED`
- MD/RD：增量输出 `1`，干净重建输出 `2`，改 `unused.h` 触发重编译
- C0 / C1 / C2 干净构建输出分别为 `10` / `12` / `19`
- C2 保留 C1 产物后普通 make 输出 `12`
- 分析器发现与 `oracle/*/expected-findings.json` 一致
- `commits/*.sha` 为 40 位小写十六进制

当前有效结果见 [`FINAL_RESULT.md`](FINAL_RESULT.md)。
