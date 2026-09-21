# Claude Code Skills

个人 Claude Code / Codex 技能与可迁移配置集。

## 一键配置 Claude Code 和 Codex

在新电脑准备 Git、Python 3.9+（含 venv/pip，或已有 uv）和两个客户端后执行：

```bash
git clone git@github.com:xuhan-rgb/claude-skills.git "$HOME/.local/share/claude-skills" && bash "$HOME/.local/share/claude-skills/install.sh"
```

安装共享规则、`skills/` 下的 8 个启用技能和 Codex Luna 子代理；已有配置先备份并合并，不复制账号密钥。
Linux 上同时安装 Claude Manager / Kitty 增强时，在命令末尾加 `--with-manager`（需 uv 和 Kitty）。
该选项会应用 Manager 的完整 Kitty 配置，默认命令不会改终端设置。

已经克隆过，更新后重新应用配置：

```bash
git -C "$HOME/.local/share/claude-skills" pull --ff-only && bash "$HOME/.local/share/claude-skills/install.sh"
```


## 配置改哪里？

运行 `bash install.sh` 后，主要就是下面几个文件：

| 要配置什么 | 本机文件 | 仓库里改哪里 |
|---|---|---|
| Claude / Codex 的通用做事规则 | `~/.claude/CLAUDE.md`、`~/.codex/AGENTS.md` | [config/CLAUDE.md](config/CLAUDE.md) |
| Codex 什么时候主动用子代理 | `~/.codex/AGENTS.md` | [config/codex/delegation.md](config/codex/delegation.md) |
| 子代理开关、默认模型、并发数 | `~/.codex/config.toml` 的 `[agents]` | [config/codex/defaults.toml](config/codex/defaults.toml) |
| 每个子代理的模型、权限和职责 | `~/.codex/agents/*.toml` | [config/codex/agents/](config/codex/agents/) |
| Codex 启用哪些技能 | `~/.codex/config.toml` 的技能条目 | [config/codex/enabled-skills.json](config/codex/enabled-skills.json) |

**AGENTS.md 写行为要求**，比如“只改相关代码”“有独立查找任务时主动用子代理”。
**子代理 TOML 写角色配置**，现在有两个：

- `luna_explorer`：只读查找、检查配置和日志。
- `luna_worker`：可以修改工作区，负责明确的局部修改。

两个角色都用 `gpt-5.6-luna`、推理强度 `medium`。
想换模型就改角色文件的 `model`，想改权限就改 `sandbox_mode`，想改职责就改 `description` 和 `developer_instructions`。

Codex 的代理开关在本机 `config.toml` 中是：

```toml
[agents]
enabled = true
max_concurrent_threads_per_session = 4
default_subagent_model = "gpt-5.6-luna"
default_subagent_reasoning_effort = "medium"
interrupt_message = true
```

### 改完怎么生效？

想把修改同步到其他电脑，就改仓库里的文件，再运行：

```bash
bash install.sh
```

然后重新打开 Claude / Codex 的新会话。
注意：`config.toml` 只补缺失项，已有的开关、模型等要直接改本机文件；两个角色文件则会用仓库版本更新。
只改 `[agents]` 的默认模型，不会改变角色文件里明确指定的模型。

`claude-manager` 管 Kitty、通知 hooks 和启动包装，不管这里的 `AGENTS.md` 与子代理。
需要它时执行 `bash install.sh --with-manager`；客户端登录、API 密钥和技能用到的外部工具仍需自行配置。
备份与其他细节见 [config/README.md](config/README.md)。

## 默认启用的技能

安装脚本只安装 `skills/` 中的 8 个技能，Claude 和 Codex 共用这些技能文件：

| 技能 | 用途 |
|---|---|
| [agent-reach](skills/agent-reach/) | 联网搜索、读取网页和平台内容 |
| [brainstorming](skills/brainstorming/) | 开发前梳理有歧义的需求和方案 |
| [domain-modeling](skills/domain-modeling/) | 整理项目术语、领域模型和架构决策 |
| [domain-variable-explainer](skills/domain-variable-explainer/) | 解释变量、张量维度和专业符号 |
| [graphviz-technical-flowchart](skills/graphviz-technical-flowchart/) | 绘制技术流程图和架构图 |
| [grilling](skills/grilling/) | 追问、检查方案漏洞 |
| [jev-delegation](skills/jev-delegation/) | 手动调用 Jev 进行任务路由与 Luna 委派 |
| [tdd](skills/tdd/) | 测试驱动开发 |

`jev-delegation` 只提供可手动调用的工作规则。Jev 的 hook、dispatcher 和执行脚本属于
独立的本地工程，不会由这个技能仓库自动安装或修改 Codex hook。

本机 Codex 已关闭的 35 个技能放在 [skills-disabled/](skills-disabled/README.md) 暂存，不删除，也不随脚本安装。
要恢复某个技能：把目录移回 `skills/`，需要在 Codex 启用时再将目录名加入
`config/codex/enabled-skills.json`，然后运行 `bash install.sh`。
安装器不会自动移除旧电脑上以前安装的技能。

## 📂 目录结构

```text
claude-skills/                     # 整个仓库，放在 ~/.local/share/claude-skills
├── README.md
├── install.sh                    # 一键安装入口
├── skills/                       # 当前启用的技能，每个目录有 SKILL.md
│   ├── graphviz-technical-flowchart/
│   ├── brainstorming/
│   ├── agent-reach/
│   └── ...
├── skills-disabled/              # 本机已关闭的技能，暂存、不安装
├── config/                       # 配置模板
│   ├── CLAUDE.md                 # Claude / Codex 共用规则
│   ├── claude/defaults.json
│   └── codex/
│       ├── defaults.toml         # 默认参数和代理开关
│       ├── delegation.md         # 主动委派规则
│       ├── enabled-skills.json   # 技能启用名单
│       └── agents/               # Luna 子代理角色
├── scripts/install.py            # 安装与备份逻辑
└── tests/                        # 安装器测试
```

仓库和安装位置分开，安装后是：

```text
~/.claude/skills/<技能名>  -> 仓库/skills/<技能名>
~/.agents/skills/<技能名>  -> 仓库/skills/<技能名>
~/.claude/CLAUDE.md       ← 安装脚本合并规则
~/.codex/AGENTS.md        ← 安装脚本合并规则
~/.codex/config.toml     ← 安装脚本合并配置
~/.codex/agents/*.toml    ← 安装脚本复制角色定义
```

不要把整个仓库直接克隆到 `~/.claude/skills`，这个目录只用于安装技能。
旧电脑如果已经这样放置，先保留本地修改，再在独立目录准备仓库；本次目录调整不会自动搬迁你的本机配置。
