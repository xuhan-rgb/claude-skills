# Claude Code + Codex 跨电脑配置

本目录保存可迁移配置；根目录 `install.sh` 同时配置两个客户端。
启用的技能放在 `skills/`，本机已关闭的技能暂存在 `skills-disabled/`，安装器只链接 `skills/` 中的技能目录；`config/`、`scripts/` 和 `tests/` 不会被安装成技能。
支持 Linux、macOS、Windows WSL；不支持 Windows 原生 PowerShell 安装。
客户端和账号需事先准备：脚本不安装 Claude Code/Codex 二进制，也不复制登录状态。

## 一条命令安装

需要 Git、Python 3.9+，以及 Python venv/pip 或 uv。SSH 克隆需要目标电脑已配置 GitHub SSH key。
Ubuntu/Debian 缺少 venv 时先安装 `python3-venv`，或使用已有 uv。

```bash
git clone git@github.com:xuhan-rgb/claude-skills.git "$HOME/.local/share/claude-skills" && bash "$HOME/.local/share/claude-skills/install.sh"
```

如果已经克隆过，更新并重新应用配置：

```bash
git -C "$HOME/.local/share/claude-skills" pull --ff-only && bash "$HOME/.local/share/claude-skills/install.sh"
```

请把仓库保留在稳定位置：技能通过软链接使用仓库内容。不要克隆到临时目录后安装再删除仓库。
推荐将整个仓库放在 `~/.local/share/claude-skills`，不要直接放在 `~/.claude/skills`。
若旧电脑已经把技能目录当作 Git 仓库，请先保留其中未提交的修改，再在独立位置准备新仓库并安装；本脚本不会自动迁移旧 checkout。
安装器不修改原来的技能仓库 checkout；更新遇到本地改动时，由 Git 正常报错，不会 reset。

预览（不改目标配置；shell 入口可能先创建安装器环境并下载 tomlkit）：

```bash
bash install.sh --dry-run
```

## 同时配置 claude-manager

`claude-manager` 负责 Kitty 配置、通知 hooks、shell 函数、Codex wrapper 和终端管理工具。
它不负责本仓库的规则、技能或 Codex `[agents]` 设置。

需要 Linux、uv、Kitty >= 0.26.0；WSL 需要能运行 Kitty 的图形环境。
TUI 运行还需要 tmux，看板跳转需要 wmctrl；这些系统软件不由本脚本安装。

```bash
git clone git@github.com:xuhan-rgb/claude-skills.git "$HOME/.local/share/claude-skills" && bash "$HOME/.local/share/claude-skills/install.sh" --with-manager
```

这会克隆 `git@github.com:xuhan-rgb/claude-manager.git` 到 `~/.local/share/claude-manager`，
分别从正确工作目录调用 `manager/install.sh` 与 `kitty-enhance/install.sh --full`。
若该目录已经存在，直接复用，不自动 pull/reset。也可以指定已有 checkout：

```bash
bash install.sh --with-manager --manager-dir /path/to/claude-manager
```

`--with-manager` 会使用上游的 **full** 安装：替换 Kitty 主配置和同名脚本、安装 hooks 和 wrapper、
向已有 shell rc 添加引用。调用前会备份这些文件。上游 shell 函数还定义了
`CLAUDE_DEFAULT_FLAGS=--dangerously-skip-permissions` 的默认值；是否通过这些函数启动 Claude
会影响权限行为。只需要规则/技能时使用不带此选项的命令。
安装后按上游提示重新加载 shell/Kitty；本安装器不会自动重启它们。

Manager 已有安装器负责自己的依赖下载。其失败会让本命令返回非零；此前已完成的核心配置不会自动回滚。
本仓库不复制 Manager 源码，不迁移飞书密钥、服务端口或运行中的任务。

## 本次从本机整理了什么

| 本地来源 | 仓库内容 / 处理方式 |
|---|---|
| `~/.claude/CLAUDE.md`、`~/.codex/AGENTS.md` | `config/CLAUDE.md` 保存共享规则；Codex 委派规则单独保存。移除指向本机知识库记录的索引，避免新电脑引用不存在的内容。 |
| `~/.codex/agents/luna_explorer.toml` | 原样保存只读 Luna 探索角色，medium。 |
| `~/.codex/agents/luna_worker.toml` | 原样保存局部实现 Luna 角色，medium、workspace-write。 |
| `~/.codex/config.toml` 的 `[agents]` | 开启代理，并发上限 4，默认模型 `gpt-5.6-luna`，推理 medium，启用中断消息。 |
| Codex 主模型和偏好 | 新配置默认 `gpt-6-astra`、medium、pragmatic；已有主模型不覆盖。 |
| Codex 权限 | 新电脑默认 on-request + workspace-write；本机的 danger-full-access 不直接复制。已有目标电脑设置保持不变。 |
| Claude 设置 | 新配置默认 opus；保留已有设置。 |
| 本地未提交技能 | 加入 agent-reach、brainstorming、desktop-app-design、domain-modeling、grill-me、grill-with-docs、grilling、handoff、tdd；补齐 Graphviz 依赖 domain-variable-explainer。同步本地 Graphviz 技能修改。 |
| 技能启用选择 | Codex 默认启用 `codex/enabled-skills.json` 中的 7 项；关闭的技能暂存在 `skills-disabled/`，不安装。Claude 同样只安装 `skills/` 中的技能，遵循其已有启用设置。 |
| `claude-manager` hooks / wrapper | 可选调用其安装器，不复制本机带绝对路径的 hooks 配置。 |

Luna 配置源自本机；Codex 配置已用本机 CLI 0.155.1 的 strict-config 检查。
其他版本需要支持 `~/.codex/agents/*.toml` 及模板中的 agents 字段。
模型能否调用取决于目标账号/服务商，不自动切换到其他付费模型。
Claude 使用自己的默认子代理能力，本机没有 `~/.claude/agents/` 自定义角色，故没有虚构对应配置。

以下内容不迁移：auth/token、服务商 URL/密钥、项目 trust、会话/历史/日志/数据库、
插件登录态、MCP 私有端点、浏览器绑定、系统技能禁用列表、全局权限白名单和平台专用环境变量。
外部管理的 Lark/插件技能没有打包；登录对应平台后单独安装。
`agent-reach` 等技能的 CLI、账号和运行依赖也需要按各自说明准备，安装 SKILL.md 不等于安装其工具。

## 合并与备份

- 已有 JSON/TOML 先解析，解析失败不会用默认文件覆盖。
- TOML 尽量保留注释，现有 provider、MCP、项目与其他字段保持原值；模板仅补缺失设置。
- 全局指令以 `claude-skills managed` 标记块追加/更新，保留块外内容。已有同义规则不会自动删除。
- 两个 Luna 角色文件由本仓库管理，同名文件先备份再更新。
- `skills/` 中的技能链接到 `~/.claude/skills/<name>` 和 `~/.agents/skills/<name>`；同名本地目录先备份再替换。
- Codex 只更新上述规范路径的启用项。旧电脑如另有技能副本或自定义启用列表，不自动删除。
- 自定义 `CODEX_HOME` 暂不支持；请取消该覆盖后安装到默认 `~/.codex`。
- 核心安装重复运行不会重复插入规则、技能项或无变化的备份；可选 Manager 部分遵循上游安装器行为，每次调用前另做备份。

备份位置：`~/.local/share/claude-skills-backups/<时间戳>/`，内部保持相对 HOME 的原路径，
例如 `.codex/config.toml`、`.claude/settings.json`。
恢复时先退出客户端，再把所需备份复制回同名位置；恢复技能实体目录前，先移除对应新软链接。
首次安装的新文件没有旧副本；需要撤销时只删除本次新增的文件/链接或 managed 标记块。
备份可能包含旧的本机账号设置，应留在本地。

## 验证

```bash
bash -n install.sh
"$HOME/.local/share/claude-skills-installer/bin/python" -m unittest discover -s tests -v
```

自动化检查使用临时目录，覆盖新安装、已有配置保留、重复执行、备份、dry-run 与无效配置拒绝。
Manager 接入仅做命令调用测试；不会在测试时重装真实桌面环境或启动 GUI。
