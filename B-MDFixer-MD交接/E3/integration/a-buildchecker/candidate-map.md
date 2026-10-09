# E3 B2 Candidate 映射

两个候选由各自报告对应的 base 独立生成，未合并为同一个 candidate。

## MD/RD

| 字段 | 值 |
|---|---|
| 样例 | A BuildChecker MD/RD |
| 报告路径 | `A-BuildChecker-E3测试基线/handoff/b2/md-rd.error-report.json` |
| 报告 SHA-256 | `170da7625e7bf7cf8b011dd988fd204fb2887e44bf806c52cc9bf31abe0cf6a2` |
| configuration_id | `cc-default` |
| selected Finding | `finding-e3-md-rd-missing-001` |
| unselected Finding | `finding-e3-md-rd-redundant-001` (`REDUNDANT`, `unused.h`) |
| base commit | `39430e3cdcf16403eec63bf592129b50ab1ff53d` |
| Patch | `md-rd/reference.patch` |
| Patch SHA-256 | `dc23000f710fec64eec45a677de651b26871ab103d8ad483abc0941f5d817eb7` |
| candidate commit | `37382e088e26b2827c3d9f7d4c5238d3d39d893f` |
| candidate parent | `39430e3cdcf16403eec63bf592129b50ab1ff53d` |
| candidate ref | `refs/heads/candidate/b2-md-rd` |
| bundle | `candidate-bundles/md-rd-candidate.bundle` |
| bundle SHA-256 | `d600eb14082b4ba2113f3c39fff4fd74881426935fec9a14cd608e9753958c28` |
| bundle verify | PASS；完整历史；list-heads 包含 candidate ref，指向 candidate commit |
| commit 文件变化 | 仅 `Makefile`：为 `main.o` 增加 `config.h`，保留 `unused.h` |

`finding-e3-md-rd-redundant-001` 保留在报告中，未由此 candidate 修复。

## C1

| 字段 | 值 |
|---|---|
| 样例 | A BuildChecker C1 |
| 报告路径 | `A-BuildChecker-E3测试基线/handoff/b2/c1.error-report.json` |
| 报告 SHA-256 | `4eb0bd6ebe1f86faaba666691087e41e913b29a31ef4408fb39501043af1f645` |
| configuration_id | `cc-MODE0` |
| selected Finding | `finding-e3-c1-missing-001` |
| unselected Finding | 无 |
| base commit | `9c3e06606aa42afef25c53dbb5eb0c5a6330e5ea` |
| Patch | `c1/reference.patch` |
| Patch SHA-256 | `2bdf153731595c72582cab0125cc6a758a7fde129270c903bcecdbb1dad7500b` |
| candidate commit | `d5d1d4a5a232094b1c2a5a74aadf3932b5ddedcf` |
| candidate parent | `9c3e06606aa42afef25c53dbb5eb0c5a6330e5ea` |
| candidate ref | `refs/heads/candidate/b2-c1` |
| bundle | `candidate-bundles/c1-candidate.bundle` |
| bundle SHA-256 | `716b515ea0e1ef4f2e8e82defab91f45492335b8de1515bbdc366bae915436f3` |
| bundle verify | PASS；完整历史；list-heads 包含 candidate ref，指向 candidate commit |
| commit 文件变化 | 仅 `Makefile`：为 `main.o` 增加 `feature.h` |
