# B1 MD/RD 环境最终本机验收记录

- 验收时间：2026-10-10 16:08（Asia/Shanghai）
- 有效运行：[`run-20261010T080813Z/`](run-20261010T080813Z/)
- 运行结果：`ACCEPTED`
- 项目：`e3-buildchecker-md-rd@2026-09-10`
- 源码基线：`29c02d6604d7071d4b249ec958dd8a553caa670a`
- 镜像：`e3-buildchecker-md-rd:b1-20260910`
- Image ID：`sha256:5be5d74a921c8600aeb4ac7a62bdea27f74521008264130039849b8309c285d6`
- 导出文件：`../e3-buildchecker-md-rd.tar`
- 导出文件大小：`98049024` bytes
- 导出文件 SHA-256：`02ee7f60fccf2392d1895e1cee616d31ba05488faab83e1c76ee07121e6e5681`

## 验收结果

| 检查 | 结果 |
| --- | --- |
| Docker 镜像构建 | 通过 |
| 断网运行 `./app` | 通过，标准输出 `1\n` |
| GNU Make / GCC | 通过 |
| MD 普通 `make` | 未重编译，输出仍为 `1` |
| MD clean rebuild | 重编译，输出为 `2` |
| RD 改动 | 触发 `main.c` 重编译 |
| `docker save` | 通过 |
| tar SHA-256 复核 | 通过 |
| tar/OCI 结构读取 | 通过 |
| `docker load` 回载 | 通过，Image ID 与交付清单一致 |
| 回载后断网运行 | 通过，标准输出 `1\n` |

详细阶段结果见 [`summary.json`](run-20261010T080813Z/summary.json)，交付身份和接收端命令见 [`transfer-manifest.json`](run-20261010T080813Z/transfer-manifest.json)，本机导出后回载记录见 [`transfer-replay.json`](run-20261010T080813Z/transfer-replay.json)。

## 跨机器状态

本机环境包已完成，且已从 Windows 挂载盘成功回载 tar 并断网运行。先前的 WSL `SIGBUS`/`swap.vhdx` 故障由 C 盘空间耗尽引起；释放空间后 WSL 和 Docker 已恢复，同一 tar 回载验证通过。

A 组已于 2026-10-11 从 GHCR 按固定 digest 拉取 B1 原始镜像，并核对 RepoDigest、Image ID、源码 revision 和 `linux/amd64` 平台；断网功能、MD stale/clean rebuild 与 RD rebuild 均通过。A 组接收端回执见 [`../../evidence/run-20261010T160627Z-ghcr/A_CROSS_MACHINE_RECEIPT.md`](../../evidence/run-20261010T160627Z-ghcr/A_CROSS_MACHINE_RECEIPT.md)。本文件记录 B1 本机导出和回载结果；跨机器验收结果以 A 组接收回执为准。
