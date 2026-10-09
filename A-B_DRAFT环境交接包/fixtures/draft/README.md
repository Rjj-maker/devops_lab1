# Tiny Greeting DRAFT

项目标识：`e3-draft-tiny-greeting@2026-09-06`。

完整接口定义见上级目录的 [`../../docs/b3-interface.md`](../../docs/b3-interface.md) 和本目录的 [`interface.json`](interface.json)。

## 构建

```bash
make
```

成功条件：退出码为 `0`，并生成可执行文件 `hello`。

## 功能验证

```bash
./hello
```

成功条件：退出码为 `0`，标准输出严格为：

```text
hello E3
```

需要干净构建时执行：

```bash
make clean
make
```

如果项目位于 Git 仓库，运行记录还应保存 `git rev-parse HEAD` 的结果。构建和验证失败时，保留原始命令、stdout、stderr、退出码和对应版本。
