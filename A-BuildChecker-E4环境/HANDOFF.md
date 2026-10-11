# E4 BuildChecker 交接说明

**交出方：** A 组 BuildChecker 负责人  
**模板来源：** 教师实验包中的官方 `A-buildchecker/`（未改写）  
**分工依据：** `docs/E4分工.jpg`  
**ECS：** `47.97.163.61`（密码不写入本文）  
**个人目录：** `/root/241880353/buildchecker`  
**本地 Git 身份：** `user.name=241880353`，`user.email=241880353@smail.nju.edu.cn`（仅 `--local`）

本文交接 **① 仓库模板与接口确认**（对接 B3）和 **③ DRAFT 容器与安全**（对接 B2）。③ 的模板约束已按官方 `compose.yaml` 写明；镜像层扫描等 Docker 上机后再补。

## 1. 请先看哪份文件

| 你是谁 | 先读 | 要做什么 |
| --- | --- | --- |
| B3 接口与 README | 第 3 节 + [`../A-buildchecker/README.md`](../A-buildchecker/README.md) | 按该 README 取得模板，确认目录与命令 |
| B2 容器运行与安全 | 第 4 节 + [`../A-buildchecker/compose.yaml`](../A-buildchecker/compose.yaml) | 确认 A 与 B 的 sock/GID 差异、资源限制、`.env`、扫描入口 |
| A 组环境负责人 / B1 | 教师包 `setup/bootstrap_ubuntu.sh`（属 ②，本次不入库） | 服务器未装 Docker 时再初始化 |
| A 组复核 / B4 | 官方 README「重跑对照」 | 等两人 `make all` |

实验包总说明：[`../E4实验包-README.md`](../E4实验包-README.md)。B 组 `B-draft/` 不在本次 ① 提交里。

## 2. ① 状态

| 项 | 值 |
| --- | --- |
| 仓库地址 | https://github.com/Rowan-hhh/devops_lab1 |
| 模板目录 | `A-buildchecker/`（教师包原文，已去掉外层 `E4实验包/`） |
| README | `A-buildchecker/README.md` |
| 构建 / 验证 | 在该目录执行 `make doctor`、`make all` |
| 模板 SHA | `eb317899420d8a11303f2273c6701b9ab6413fbb`（官方 `A-buildchecker/` 入库提交） |
| 服务器 `make all` | 未做（ECS 尚无 Docker）。属 ② 之后 |

本组远程仓库还有 E3 材料，所以模板不能铺在仓库最外层根目录（那里没有单独给 E4 腾空）。B3 克隆后进入 `A-buildchecker/` 再跑命令。

## 3. 给 B3：仓库、README、命令（①）

| 项 | 值 |
| --- | --- |
| 仓库地址 | https://github.com/Rowan-hhh/devops_lab1 |
| 进入目录 | `A-buildchecker/` |
| 模板 SHA | `eb317899420d8a11303f2273c6701b9ab6413fbb` |
| 构建 / 验证 | `make doctor`；`make all`（doctor → build → test → smoke → scan） |
| 冒烟内部 | `fixtures/md-rd/`：`make` + `./app`，`app_output` 为 `1` |
| 基础镜像 | `m.daocloud.io/docker.io/library/python@sha256:f82c96458eedc847b233e582eb31336f4954b39cae020b6dcf5b3ed0e5cbcd74` |

```sh
git clone https://github.com/Rowan-hhh/devops_lab1.git
cd devops_lab1/A-buildchecker
git rev-parse HEAD
ls Makefile compose.yaml services/buildchecker fixtures/md-rd scripts
```

**请回：** 能否按官方 README 取得本模板；命令是否就是 `make doctor` / `make all`。不要改 `fixtures/md-rd/`。

## 4. 给 B2：容器与安全（③）

模板 SHA：`eb317899420d8a11303f2273c6701b9ab6413fbb`（与 ① 同一份官方 `A-buildchecker/`）。请对照课件「Compose：A 组与 B 组的差别」。

| 交互项 | A 组（BuildChecker） | B 组 DRAFT（对照，不在本次提交） |
| --- | --- | --- |
| `docker.sock` | **不挂载** | 挂载 `/var/run/docker.sock` |
| `DOCKER_GID` / `group_add` | **不使用** | `group_add: ["${DOCKER_GID}"]` |
| 资源限制 | `cpus: 2`，`mem_limit: 1g`，`pids_limit: 256` | 同左（只限制容器本身） |
| 网络 | `network_mode: none` | 需访问宿主机 Docker，无 `network_mode: none` |
| 额外能力 | `cap_add: [SYS_PTRACE]`（冒烟 strace） | 无 SYS_PTRACE |
| `.env` | `make` 从 `.env.example` 生成、权限 600；**无** `env_file`；A 组不填 API Key | `env_file: .env` 运行时注入 |
| 密钥扫描 | `make scan` → `scripts/secret_scan.py . --history --image <镜像>` | 同类脚本 |

仓库约束（已在 `eb31789` 中）：

- `.gitignore` / `.dockerignore` 忽略 `.env`、`.env.*`（保留 `.env.example`）
- `git ls-files A-buildchecker/.env` 无输出
- 本机对 `A-buildchecker/` 工作区扫描：`密钥检查：未发现问题（文件 21 个）`，退出码 0  
  （Windows 下 `--history` 因编码未跑；镜像层扫描需 Docker，属 ② 之后）

**请回：** A 组不挂 sock、不用 GID、有资源限制、`.env` 不入库、扫描入口为 `make scan` —— 是否与 DRAFT 侧约定一致。不要把 B 组的 sock 写法抄进 A 组 compose。

## 5. 回执

| 角色 | 结论 | SHA | 日期 | 签名 |
| --- | --- | --- | --- | --- |
| B3 | （待填） |  |  |  |
| B2 | （待填：安全约束是否一致） |  |  |  |
