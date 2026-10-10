# B1 MD/RD 环境验收记录

`run_b1_md_rd.py` 默认在本目录下创建 `run-YYYYMMDDTHHMMSSZ/`。每次使用新目录，不覆盖旧证据。

只有在实际 Docker 构建、断网运行、MD stale/clean rebuild 和 RD 重编译验证全部通过后，`summary.json` 才会写入 `result: ACCEPTED`。`--check-only` 不会在本目录生成运行证据。

使用 `--export-image` 时，同一运行目录中的 `transfer-manifest.json` 会记录导出 tar 的 SHA-256 与导入后验证命令。镜像 tar 是大文件，默认不应提交到 Git。

当前有效运行和镜像交付身份见 [`FINAL_RESULT.md`](FINAL_RESULT.md)。
