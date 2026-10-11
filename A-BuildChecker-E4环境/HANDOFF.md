# E4 BuildChecker 交接说明

**交出方：** A 组 BuildChecker 负责人  
**模板来源：** 教师实验包中的官方 `A-buildchecker/`（未改写）  
**分工依据：** `docs/E4分工.jpg`  
**ECS：** `47.97.163.61`（密码不写入本文）  
**个人目录：** `/root/241880353/buildchecker`  
**本地 Git 身份：** `user.name=241880353`，`user.email=241880353@smail.nju.edu.cn`（仅 `--local`）

本文交接 **① 仓库模板与接口确认**（对接 B3）。

## 1. 请先看哪份文件

| 你是谁 | 先读 | 要做什么 |
| --- | --- | --- |
| B3 接口与 README | 第 3 节 + [`../A-buildchecker/README.md`](../A-buildchecker/README.md) | 按该 README 取得模板，确认目录与命令 |
| B2 容器运行与安全 | 第 4 节 + [`../A-buildchecker/compose.yaml`](../A-buildchecker/compose.yaml) | 确认 A 组无 docker.sock；活扫描等上机 |
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
| 模板 SHA | **把 `A-buildchecker/` 提交进 `main` 之后**，在该目录执行 `git rev-parse HEAD` |
| 服务器 `make all` | 未做（ECS 尚无 Docker）。属 ② 之后 |

本组远程仓库还有 E3 材料，所以模板不能铺在仓库最外层根目录（那里没有单独给 E4 腾空）。B3 克隆后进入 `A-buildchecker/` 再跑命令。

## 3. 给 B3：仓库、README、命令（①）

| 项 | 值 |
| --- | --- |
| 仓库地址 | https://github.com/Rowan-hhh/devops_lab1 |
| 进入目录 | `A-buildchecker/` |
| 模板 SHA | （提交后填写） |
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

## 4. 给 B2：容器与安全（③，模板已写明）

官方 `A-buildchecker/compose.yaml`：

- **不挂** `/var/run/docker.sock`，**不用** `DOCKER_GID`
- `network_mode: none`，`cap_add: [SYS_PTRACE]`
- `cpus: 2`，`mem_limit: 1g`，`pids_limit: 256`
- A 组无 `env_file`；`.env` 由 `.env.example` 生成、权限 600、不提交

活证据等 Docker 就绪后补。

## 5. 回执

| 角色 | 结论 | SHA | 日期 | 签名 |
| --- | --- | --- | --- | --- |
| B3 | （待填） |  |  |  |
| B2 | （待填：安全约束是否一致） |  |  |  |
