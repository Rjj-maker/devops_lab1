# E4 可重复工程环境：实验包

E4 的目标：把**本组自己的服务仓库**改造成"任何组员在服务器上执行一条命令，就能构建、测试、留下证据，而且结果一样"。E5—E14 都在这个环境里进行。

学生按组使用：[A 组全流程命令手册](../课件/E4_A组全流程命令手册_20260929.md) 或 [B 组全流程命令手册](../课件/E4_B组全流程命令手册_20260929.md)。

依据：实验里程碑表 E4"共同建立 Docker、依赖固定、Secret、测试与一键命令"，最低证据"镜像/Compose、基线日志、无密钥泄露"；课程项目设计 Sprint 2"服务必须在其他同学机器运行"。

## 1. 包里有什么

| 目录 | 给谁 | 内容 |
| --- | --- | --- |
| `A-buildchecker/` | A 组 | BuildChecker 服务仓库模板：服务骨架、Dockerfile、compose、Makefile、锁文件、E3 的 `md-rd` 样例 |
| `B-draft/` | B 组 | DRAFT 服务仓库模板：同上，另含挂载宿主机 Docker 的写法、E3 的 `draft` 样例 |
| `setup/bootstrap_ubuntu.sh` | 老师或各组第一次登录时 | 安装 Docker、Compose、Git、Make，配置镜像加速，把登录账号加入 docker 组 |

模板的目录结构（以 A 为例，与课程项目设计附录 A 一致）：

```
A-buildchecker/
  services/buildchecker/
    Dockerfile            固定 digest、导出版本清单、按哈希安装依赖、非 root
    buildchecker/         服务代码：cli.py（version / smoke）、smoke.py
    tests/                单元测试（pytest）
  fixtures/md-rd/         E3 的 MD/RD 人工样例
  compose.yaml            资源限制、无网络、SYS_PTRACE
  Makefile                doctor / build / test / smoke / scan / shell / lock / clean
  requirements-dev.in     直接依赖
  requirements-dev.lock   带哈希的锁文件
  .env.example .gitignore .dockerignore
  scripts/doctor.py       服务器与 Git 身份自检
  scripts/secret_scan.py  工作区、Git 历史、镜像的密钥检查
```

## 2. 服务器与学号目录

- 苏州校区已为 A01—A17、B01—B17 各分配一台阿里云服务器。每组使用自己的公网 IP；老师按组私发轮换后的登录凭据，不把含全部 IP 和初始密码的分配表发给全班。服务器系统版本以实际自检为准。
- **服务器课前准备（每组只做一次）**：教师或助教负责分配和轮换初始凭据、检查 SSH；有管理员权限且熟悉操作的组长也可检查并初始化 Docker。阿里云安全组仅向可信来源开放 SSH，不开放 Docker API 端口 2375/2376。初始化脚本只适用于 Ubuntu 22.04/24.04；确认系统、Docker 确实未安装时才执行（已装好可跳过）：

  ```sh
  sudo bash setup/bootstrap_ubuntu.sh
  # 需要镜像加速时
  sudo DOCKER_MIRROR=https://<镜像加速地址> bash setup/bootstrap_ubuntu.sh
  ```

- **每人一个工作目录，本地 Git 身份设置为学号**。因为登录账号是共用的，**不要**用 `--global`，只在自己的克隆里设置；E4 不要求个人提交：

  ```sh
  ssh <老师私发的登录账号>@<本组公网IP>  # 在自己电脑的终端执行
  mkdir -p ~/<学号> && cd ~/<学号>
  git clone <本组仓库地址> && cd <仓库>
  git config user.name  "<学号>"
  git config user.email "<学号>@localhost"  # E4 不推送，填本地示例值即可
  ```

  `make doctor` 会检查这一点；镜像名和 Compose 项目名也取自 `user.name`（例如 `e4-buildchecker:231220001`），避免组员在同一台服务器上使用同名镜像或容器。E4 普通组员只克隆、不推送；`学号@localhost` 是本地配置示例，不需要 Git 平台账号。学号目录、`git config` 只影响本地工作区和以后创建的提交，**不会自动产生提交、上传证据或证明操作者身份**。

## 3. 当堂操作

组长确认本组远程仓库已有对应模板；若仓库为空，由组长或教师作一次模板初始化提交并推送。此后每名组员各自在学号目录克隆并执行：

```sh
make doctor     # 服务器与 Git 身份自检             → work/<时间>/env.json
make build      # 构建服务镜像                      → build.log、image.json、toolchain.lock
make test       # 在容器里运行本组单元测试          → test.log
make smoke      # 用 E3 样例做冒烟测试              → smoke.json
make scan       # 工作区、Git 历史、镜像的密钥检查  → secret-scan.txt
make all        # 以上五步，放在同一个证据目录
```

预期结果：

| 命令 | A 组 | B 组 |
| --- | --- | --- |
| `make test` | `3 passed` | `4 passed` |
| `make smoke` | `"passed": true`；`config_h_opened` 里有 `openat(... "config.h" ...)`；`app_output` 为 `1` | `"passed": true`；`build_exit_code` 非 0；`make_error_line` 含 `/bin/sh: 1: make: not found` |
| `make scan` | `密钥检查：未发现问题` | 同左 |

冒烟测试只确认环境和操作链路可用。`smoke.json` 是 E4 的检查结果，不是 E5 的完整原始证据：A 组当前只保留少量 `strace` 摘要行，B 组保留构建日志末尾和单独的关键错误行；`log_tail` 不保证包含 `make: not found`。E5 应在同一镜像中按 E5 操作步骤重新执行，并保存 A 组完整的 `strace -ff` 记录与 `make -p` 输出，或 B 组完整的 Docker 构建日志和退出码。

之后每人再做一次"重跑对照"：另一名组员在自己的目录重新克隆、执行 `make all`，比较两份 `test.log`、`smoke.json` 和 `toolchain.lock`。镜像 ID 不同是正常的（构建时间不同），要能用 `toolchain.lock` 说明工具版本一致。

### 3.1 E4 的个人运行与本组仓库

每名学生从**真正的本组 Git 仓库地址**克隆，先用 `git remote -v` 核对 `origin`。课堂试跑时使用的 `/root/E4实验包/...` 是服务器上的本地模板，不是课程平台的小组远程仓库。学号目录使每人的工作区、`.env` 和 `work/` 分开，镜像与 Compose 项目也按学号区分；同一台服务器的 Docker 引擎和缓存仍由本组共用。

E4 每名组员在自己的学号目录运行一次 `make all`，记下所测仓库的完整 SHA 和成功的 `work/<时间>/`，再与另一名组员比较结论。`work/` 在 `.gitignore` 中，E4 **不要求每人创建分支、提交、推送或由组长合并**；小组仓库不会自动记录每个人这次运行。后续要按个人提交评定贡献时，再安排个人改动的提交和合并流程。

组长负责确认本组远程仓库含有对应模板，并额外克隆一次用于检查；若远程仓库为空，才需由组长或教师把模板作一次初始化提交并推送。这是**小组仓库准备**，不是组员个人的 E4 提交。`git config user.name` 只会标记将来创建的提交，不能凭它认定这次实验由谁运行。

## 4. 固定到什么程度

| 依赖 | 固定方式 | 证据 |
| --- | --- | --- |
| 基础镜像 | `python:3.13-slim@sha256:f82c9645…`（E3 在 Colima 上真实构建时解析到的 digest；已在 Docker Hub 确认是多架构索引，含 amd64） | `build.log` 中的 resolve 行 |
| Docker 命令行（B 组） | `docker:28.5.1-cli@sha256:9190b061…`，多阶段构建只复制客户端和 buildx 插件 | Dockerfile |
| 系统工具 | apt 源会下架旧版本，不写死版本号；构建时把实际版本写进 `/opt/toolchain.lock` | `toolchain.lock` |
| Python 包 | `requirements-dev.lock` 带哈希，`pip install --require-hashes` | 锁文件、`toolchain.lock` 中的 `pip:` 行 |
| 被测项目 | 完整 40 位 commit SHA；E3 样例未纳入 Git，用源码内容摘要代替 | 复现说明 |

## 5. B 组：为什么要挂载宿主机的 Docker

**原因**：DRAFT 的工作就是反复执行 `docker build`。课程要求服务本身也跑在容器里（课程项目设计 P-15），而容器默认没有 Docker 引擎，于是出现"在容器里还要用 Docker"的问题。DRAFT 论文没有这个问题：论文里 DRAFT 直接运行在一台 Ubuntu 22.04 服务器上，没有把它容器化。这一点要写进 E5 的差异记录。

**做法**（已写在 `B-draft/` 里）：

1. Dockerfile 从官方 `docker:cli` 镜像复制 `docker` 命令行，镜像里**只有客户端，没有引擎**。
2. `compose.yaml` 把宿主机的 `/var/run/docker.sock` 挂进容器：容器里执行的 `docker build`，实际由宿主机的 Docker 完成。
3. `docker.sock` 属于宿主机的 docker 组，容器里的 `app` 用户需要加入这个组：Makefile 用 `stat -c %g /var/run/docker.sock` 取得组号，compose 用 `group_add` 加进去。
4. 验证：`make smoke` 以服务默认的 `app` 用户运行，能够访问宿主机 Docker 并取得构建日志。以 `root` 登录这台 ECS 时，`make shell` 可能按宿主机 UID 进入容器，不能单凭它证明默认 `app` 用户有此权限。

**风险**：

- 能访问 `docker.sock` 就等于拥有宿主机 root 权限：可以启动特权容器、挂载宿主机任意目录、删除任意镜像和容器。
- 构建由宿主机执行，**compose 里对 DRAFT 容器的 CPU、内存限制管不到这些构建**；构建出的镜像和缓存也占用宿主机磁盘。
- 被构建的项目如果有恶意的 Dockerfile，影响的是宿主机。
- 在容器里执行 `docker run -v <路径>` 时，路径是**宿主机**上的路径，不是容器里的路径。

**本课程的约束**：每组独占一台服务器，风险只在本组内；只构建课程指定的项目；构建设置超时（Makefile 的 `timeout`），E6 起每次构建使用唯一镜像名并及时清理；不开放 Docker API 端口（2375/2376）。

## 6. 密钥

- 课程不提供 LLM 接口，需要时使用自己的 API Key，写在 `.env`（`make` 会从 `.env.example` 生成并设为 600 权限）。
- `.env` 已写入 `.gitignore` 和 `.dockerignore`；B 组通过 compose 的 `env_file` 在运行时注入，不写进 Dockerfile 的 `ENV`/`ARG`，不 `COPY` 进镜像。
- `make scan` 检查三处：被 Git 跟踪的文件、Git 历史、镜像的构建历史与环境变量。输出只显示前 4 位。
- Key 一旦推送到远端就当作已泄露：先到服务商处作废并重新申请，再清理仓库。

## 7. 常见问题

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `permission denied ... docker.sock`（宿主机上） | 登录账号不在 docker 组 | `sudo usermod -aG docker $USER`，重新登录 |
| `permission denied ... docker.sock`（B 组容器里） | 没有加入 docker.sock 的组 | 用 `make` 运行，不要直接 `docker compose run`；或先 `export DOCKER_GID=$(stat -c %g /var/run/docker.sock)` |
| `strace: ... Operation not permitted` | 容器限制了 ptrace | 确认 compose 中有 `cap_add: [SYS_PTRACE]` |
| `3 passed` 后 `make test` 不返回 | Compose 的非交互命令接入日志管道后仍保持交互输入 | 使用新版 Makefile；`test` 和 `smoke` 的 `docker compose run` 已加 `-T --interactive=false` |
| 拉取镜像超时 | 试用 ECS 直连 Docker Hub 超时 | A、B 组均核验固定 digest 的镜像站地址；步骤见各组命令手册第 4 节 |
| `No space left on device` | 镜像与构建缓存占满磁盘 | `make clean`；`docker builder prune` |
| 提交作者显示成别人 | 用了共享的全局身份 | 删除 `--global` 设置，在自己的克隆里设置学号 |
| `THESE PACKAGES DO NOT MATCH THE HASHES` | 锁文件与 `.in` 不一致或被改动 | `make lock` 重新生成并提交 |

## 8. 已验证与未验证

- 已验证：Windows 本机两个模板的单元测试各 `3 passed`，`secret_scan.py` 均显示"未发现问题"。Ubuntu 22.04 ECS 已安装 Docker、Compose 与 buildx；A 组使用固定 digest 的镜像站，在同一台服务器上以 `2026000001`、`2026000002` 两个模拟学生目录分别完整运行 `make all`。两次环境自检、镜像构建、单测（各 `3 passed`）、冒烟（均 `"passed": true`，`config.h` 被打开、程序输出 `1`）与密钥扫描均通过，工具链版本输出相同。证据目录分别为 `work/20260929-023139/`、`work/20260929-023920/`。还用假 Key 验证扫描器报错，删除假文件后再次扫描通过，第一份克隆的 `git status --short` 为空。两次构建复用了同一台服务器的 Docker 缓存；正式教学仍由各组员按第 3 节保存自己的证据。
- B 组也已在同一台 Ubuntu 22.04 ECS 的 `2026000003`、`2026000004` 两个模拟学生克隆中分别完整运行 `make all`：`make doctor` 通过，镜像构建成功，`toolchain.lock` 输出相同（容器内 Docker CLI 28.5.1），冒烟记录宿主机 Docker Server 29.1.3；单测各 `4 passed`，冒烟的 `build_exit_code` 均为 1、`make_error_line` 均含 `make: not found`、`"passed": true`，密钥扫描均未发现问题。两次均使用模板提交 `06a883180c6c0ffee940c667fb0e0047ac67fa8a`，证据目录分别为 `work/20260929-030934/`、`work/20260929-031236/`。随后两份 `toolchain.lock` 用 `diff -u` 比较，退出码为 0；假 Key 被扫描器检出，清理后再次扫描通过且 `git status --short` 为空。两份克隆共用服务器 Docker 缓存；正式教学仍需各组员自己留证据。学生操作与网络排错详见 B 组全流程命令手册。
