# E3 B2 Candidate 交接给 B4

以下是两个独立候选。请分别取得、构建、测试和重检，不要合并为同一个 candidate。

| 样例 | bundle | SHA-256 | base commit | candidate commit | configuration_id | selected Finding |
|---|---|---|---|---|---|---|
| MD/RD | `candidate-bundles/md-rd-candidate.bundle` | `d600eb14082b4ba2113f3c39fff4fd74881426935fec9a14cd608e9753958c28` | `39430e3cdcf16403eec63bf592129b50ab1ff53d` | `37382e088e26b2827c3d9f7d4c5238d3d39d893f` | `cc-default` | `finding-e3-md-rd-missing-001` |
| C1 | `candidate-bundles/c1-candidate.bundle` | `716b515ea0e1ef4f2e8e82defab91f45492335b8de1515bbdc366bae915436f3` | `9c3e06606aa42afef25c53dbb5eb0c5a6330e5ea` | `d5d1d4a5a232094b1c2a5a74aadf3932b5ddedcf` | `cc-MODE0` | `finding-e3-c1-missing-001` |

## 取得并核对

在各自的临时目录运行对应命令。不要直接使用 bundle 的默认 HEAD；明确 checkout candidate SHA。

```sh
git clone --no-checkout candidate-bundles/md-rd-candidate.bundle md-rd-candidate
git -C md-rd-candidate checkout --detach 37382e088e26b2827c3d9f7d4c5238d3d39d893f
git -C md-rd-candidate rev-parse HEAD^
git -C md-rd-candidate diff-tree --no-commit-id --name-only -r HEAD
```

MD/RD 的 parent 应为 `39430e3cdcf16403eec63bf592129b50ab1ff53d`，变更文件应只有 `Makefile`。C1 使用自己的 candidate bundle 并显式 checkout candidate SHA：

```sh
git clone --no-checkout candidate-bundles/c1-candidate.bundle c1-candidate
git -C c1-candidate checkout --detach d5d1d4a5a232094b1c2a5a74aadf3932b5ddedcf
git -C c1-candidate rev-parse HEAD^
git -C c1-candidate diff-tree --no-commit-id --name-only -r HEAD
```

C1 的 parent 应为 `9c3e06606aa42afef25c53dbb5eb0c5a6330e5ea`，变更文件应只有 `Makefile`。C1 必须使用 C1 candidate，不得使用原始 commits bundle 默认指向的 C2。

## Build 与 test

在匹配各自 `configuration_id` 的约定环境中分别执行：

```sh
make clean && make
./app
```

B2 从候选 bundle 新 clone 的自测结果：MD/RD 初始输出 `1`；改 `config.h` 后重编译、输出 `2`；`unused.h` 仍在规则中且改动后仍触发重编译。MD/RD 的 `REDUNDANT unused.h` 未由 B2 修复。C1 初始输出 `12`；改 `feature.h` 后重编译、输出 `13`。这些是 B2 自测，不替代 B4 的正式验证。

## Recheck 状态与边界

正式 B4 recheck 尚未执行。A 组现有 `run_a_buildchecker.py` 没有面向外部 candidate workspace 的参数；不得将 A 组固定 fixtures 的基线重跑记为 candidate recheck。recheck 命令和结果由 B4 阶段补充。本交接只提供可取得的 candidate workspace 输入、base/candidate 映射、bundle 校验信息和 B2 自测结果；不表示 B4 已接受候选。
