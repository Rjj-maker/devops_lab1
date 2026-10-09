# 运行记录说明

`run_b1.py` 默认在本目录创建 `run-YYYYMMDDTHHMMSSZ/`。每次运行使用新目录，不覆盖已有记录。

一次完整运行至少包含：

```text
summary.json
docker-version.command.txt
docker-version.stdout.log
docker-version.stderr.log
docker-version.exit-code.txt
broken-build.command.txt
broken-build.stdout.log
broken-build.stderr.log
broken-build.exit-code.txt
reference-build.command.txt
reference-build.stdout.log
reference-build.stderr.log
reference-build.exit-code.txt
reference-image-inspect.command.txt
reference-image-inspect.stdout.log
reference-image-inspect.stderr.log
reference-image-inspect.exit-code.txt
reference-compiler-version.command.txt
reference-compiler-version.stdout.log
reference-compiler-version.stderr.log
reference-compiler-version.exit-code.txt
reference-make-version.command.txt
reference-make-version.stdout.log
reference-make-version.stderr.log
reference-make-version.exit-code.txt
reference-artifact-check.command.txt
reference-artifact-check.stdout.log
reference-artifact-check.stderr.log
reference-artifact-check.exit-code.txt
reference-verify.command.txt
reference-verify.stdout.log
reference-verify.stderr.log
reference-verify.exit-code.txt
```

## 结果核对

- `broken-build.exit-code.txt` 为非零值；
- 失败日志包含可定位的错误信息；
- `reference-build.exit-code.txt` 为 `0`；
- `reference-image-inspect.exit-code.txt` 为 `0`；
- `reference-compiler-version.exit-code.txt` 为 `0`；
- `reference-make-version.exit-code.txt` 为 `0`；
- `reference-artifact-check.exit-code.txt` 为 `0`，输出包含 `/work/hello` 的权限信息；
- `reference-verify.exit-code.txt` 为 `0`；
- `reference-verify.stdout.log` 的内容严格为 `hello E3` 加一个换行；
- `summary.json` 中的 `result` 为 `ACCEPTED`；
- `git.sha` 记录运行时的完整 commit SHA；
- `git.status` 记录运行时尚未提交的文件；
- 操作系统、CPU 架构、Docker 版本、镜像 ID 和运行时间已经记录。

当前有效结果见 [`FINAL_RESULT.md`](FINAL_RESULT.md)，对应目录为 `run-20260929T161653Z/`。先前已提交的 `run-20260929T073452Z/` 保留为历史成功记录；两次代理故障重试目录已清理。
