# Apple Container Operator

<p align="center">
  <a href="./README.en.md">English</a> | 简体中文
</p>

Apple Container Operator 是一个厂商中立的 AI agent skill pack，用来帮助 AI 从自然语言、Docker 风格命令和容器配置请求中理解用户意图，并安全地操作 Apple 原生 `container` 运行时。

它不是围绕某个特定 AI 平台设计的插件，而是一组可被 Codex、Claude Code、Cursor、Gemini 和其他 agentic coding tools 复用的说明、参考文档和小脚本。

## 它能做什么

- 处理自然语言容器操作，比如运行、停止、查看、进入和调试容器。
- 把 Docker 风格命令当作“意图语言”进行保守翻译。
- 管理本地容器和镜像生命周期。
- 引导安装 Apple 原生 `container`，默认使用官方签名安装包。
- 规划端口、环境变量、卷挂载、命令、名称、工作目录、镜像 tag 等配置变更。
- 排查 CLI、系统服务、镜像拉取、启动失败、端口、挂载和权限问题。
- 对删除、清理、重建、有状态服务迁移等动作执行安全规则。

## Setup

### 安装这个 Skill Pack

把下面这段发给你的 AI coding agent：

```text
Install the Apple Container Operator skill pack from https://github.com/lizhelang/apple-container-operator.

Clone the repository, inspect its README and skills/apple-container/SKILL.md, then install or reference the apple-container skill in your local agent skill/rules system so future requests about Apple container use this skill automatically. Keep it vendor-neutral and do not convert it into an OpenAI-only plugin.
```

### 安装 Apple Container

装好 skill pack 后，把下面这段发给 AI：

```text
Use the apple-container skill to install Apple's native container runtime on this Mac.

Follow the skill's installation workflow: verify this is an Apple silicon Mac, check the macOS version, download the latest official signed installer package from apple/container GitHub Releases, install it with the macOS installer, run container --version, start the system service with container system start, and verify the result. Do not install Docker Desktop as a substitute.
```

### 一次性安装 Skill Pack 和 Apple Container

如果想一步完成，把下面这段发给 AI：

```text
Set up Apple Container Operator end to end.

First install the Apple Container Operator skill pack from https://github.com/lizhelang/apple-container-operator into your local agent skill/rules system. Then use that skill to install Apple's native container runtime on this Mac from the official apple/container GitHub Releases signed installer package. Verify Apple silicon and macOS support, install the package, run container --version, start container system service, and report the final status. Keep the workflow vendor-neutral and do not install Docker Desktop as a substitute.
```

### 把 Docker 上部署的服务迁移到 Apple Container

把下面这句话发给 AI，它会帮你盘点 Docker 侧的服务并迁移到 Apple `container`：

```text
Use Apple Container Operator to inspect my Docker-based service setup, identify images, ports, env vars, volumes, commands, dependencies, and stateful data, then create and execute a safe migration plan to Apple's native container runtime without assuming full Docker or Compose parity.
```

## 安装与使用

### 通用 AI Agent

把 `skills/apple-container/SKILL.md` 复制、引用或安装到你的 agent skill / rules 系统里。这个 skill 会把细节路由到 `skills/apple-container/references/`，并使用 `skills/apple-container/scripts/` 里的确定性小脚本。

常用检查脚本：

```sh
skills/apple-container/scripts/detect-container.sh
skills/apple-container/scripts/install-container.sh
skills/apple-container/scripts/inspect-state.sh
```

在假设本地命令或 flag 可用之前，agent 应该先检查 `container --help` 和相关子命令 help。

### Codex

Codex 可以使用根目录的 `AGENTS.md` 作为项目级说明。处理 Apple container 请求时，先加载 `skills/apple-container/SKILL.md`，再按需要阅读 reference 文件。

### Claude Code

Claude Code 可以参考 `agents/CLAUDE.md`。它保留了同样的可移植行为，不依赖 Codex 专用 API。

### Cursor

Cursor 可以使用 `agents/cursor-rules.md` 作为项目规则。修改 Docker 风格翻译行为时，应同步更新测试。

## 示例

用户：`帮我跑一个 postgres，密码设成 pass，端口暴露到本机`

Agent 行为：识别为 `run_container`，检查 `container run --help`，规划环境变量和端口映射，提醒数据库持久化风险，然后只生成经过本地 help 验证的 `container run` 命令。

用户：`docker ps`

Agent 行为：把它理解成 `list_containers`，翻译成 Apple container 的容器列表工作流，并在不确定时检查精确 list 语法。

用户：`docker logs -f app`

Agent 行为：把它理解成 `view_logs`，如果 Apple container 支持 logs follow，再使用 follow flag；否则给出安全替代方案。

用户：`把 app 的端口从 3000 改成 8080`

Agent 行为：识别为 `configuration_change`，先检查当前配置；如果不能原地修改，就生成尽量保留镜像、环境变量、挂载、命令和名称的停止 / 重建计划。

用户：`这个容器启动不了，帮我 debug`

Agent 行为：按顺序检查系统、镜像、容器状态、日志、命令与配置、端口和挂载，然后给出最小复现建议。

用户：`帮我安装 Apple container`

Agent 行为：检查 Apple silicon 和 macOS 支持，从官方 `apple/container` GitHub Release 下载最新 signed installer package，用 macOS installer 安装，然后启动并验证 system service。

## 兼容性说明

Apple `container` 不是 Docker。Docker 风格命令在本项目里只是“意图来源”，不是 Apple container 支持相同 flag 或工作流的证明。Agent 和维护者在假设某个 flag 可用前，应先检查本地 `container` CLI help 和版本。
