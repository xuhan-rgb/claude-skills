# Claude Code Skills

个人 Claude Code / Codex 技能与可迁移配置集。

## 一键配置 Claude Code 和 Codex

在新电脑准备 Git、Python 3.9+（含 venv/pip，或已有 uv）和两个客户端后执行：

```bash
git clone git@github.com:xuhan-rgb/claude-skills.git "$HOME/.local/share/claude-skills" && bash "$HOME/.local/share/claude-skills/install.sh"
```

安装共享规则、仓库技能和 Codex Luna 子代理；已有配置先备份并合并，不复制账号密钥。
Linux 上同时安装 Claude Manager / Kitty 增强时，在命令末尾加 `--with-manager`（需 uv 和 Kitty）。
该选项会应用 Manager 的完整 Kitty 配置，默认命令不会改终端设置。

## 拿到工程后，需要手动做什么？

**必须手动准备的是运行环境、客户端和账号；规则、技能链接、Codex 子代理文件由安装脚本写入。**
仅安装配置不会自动获得模型调用权限，也不会安装所有技能使用的外部工具。

### 1. 安装前：必做准备

| 项目 | 你需要做什么 | 是否由本仓库自动完成 |
|---|---|---|
| 操作系统 | 使用 Linux、macOS 或 Windows WSL；Windows 原生 PowerShell 暂不支持 | 否 |
| 基础环境 | 安装 Git、Python 3.9+，以及 Python venv/pip 或 uv | 否；脚本只自动创建自己的隔离环境并安装 tomlkit |
| Claude Code / Codex | 安装两个客户端，确保 `claude --version` 和 `codex --version` 能运行 | 否；Manager 的 Codex wrapper 也不能替代真实客户端 |
| 账号与服务商 | 分别完成客户端登录；如用 API/中转服务，在新电脑配置自己的服务商地址、密钥和环境变量 | 否；不会复制旧电脑凭据 |
| 仓库访问 | 使用上方 SSH 克隆命令时，先配置 GitHub SSH key 和仓库访问权限；已取得完整工程则无需重新克隆 | 否 |
| 仓库存放位置 | 放在长期保留的位置，例如 `~/.local/share/claude-skills`；安装后不要移动或删除 | 手动选择；技能通过软链接引用这里 |
| Codex 配置目录 | 使用默认 `~/.codex`；若设置了其他 `CODEX_HOME`，先取消该覆盖 | 当前安装器不支持自定义 Codex 配置目录 |

Ubuntu/Debian 如果提示缺少 venv，可先执行 `sudo apt install python3-venv`，或准备 uv 后重试。

### 2. 已经拿到工程：选择安装方式

进入工程根目录，只需选择下面一种方式，不必手工复制配置文件：

```bash
# 只配置 Claude Code + Codex
bash install.sh

# 或：额外配置 Claude Manager + Kitty（Linux，需要先准备 uv 和 Kitty）
bash install.sh --with-manager

# 或：复用已经下载的 claude-manager 工程
bash install.sh --with-manager --manager-dir /path/to/claude-manager
```

可以先执行 `bash install.sh --dry-run` 查看计划。它不写目标配置，但可能先创建安装器环境并下载 tomlkit。

### 3. 脚本会自动配置什么？

| 自动配置 | 写入位置 | 具体内容 |
|---|---|---|
| Claude 全局规则 | `~/.claude/CLAUDE.md` | 追加/更新共享规则块，包含最小修改、验证、统计采样和证据要求等；保留块外内容 |
| Codex 全局规则 | `~/.codex/AGENTS.md` | 共享规则 + 主动委派子代理的条件与分工规则 |
| Claude 默认模型 | `~/.claude/settings.json` | 缺少 `model` 时补为 `opus`；保留已有模型、账号环境变量、权限和 hooks |
| Codex 默认设置 | `~/.codex/config.toml` | 缺失项补为 `gpt-6-astra`、推理 `medium`、`pragmatic`、`on-request`、`workspace-write` |
| Codex 代理设置 | 同上，`[agents]` | 缺失项补为开启代理、并发上限 4、默认 `gpt-5.6-luna` / `medium`、启用中断消息 |
| 只读子代理 | `~/.codex/agents/luna_explorer.toml` | Luna / medium / read-only，负责查找、日志检查和小范围代码梳理 |
| 实现子代理 | `~/.codex/agents/luna_worker.toml` | Luna / medium / workspace-write，负责明确、局部、低风险修改 |
| 技能安装 | `~/.claude/skills/<name>`、`~/.agents/skills/<name>` | 为仓库技能创建链接；同名已有目录先备份再替换 |
| Codex 技能启用 | `~/.codex/config.toml` 的技能条目 | 默认启用下面 7 项，其余仓库技能安装但禁用；不自动清理其他来源的技能 |
| 原文件备份 | `~/.local/share/claude-skills-backups/<时间戳>/` | 保留被修改/替换的已有文件与目录，按原相对路径存放 |

Codex 默认启用：`agent-reach`、`brainstorming`、`domain-modeling`、`domain-variable-explainer`、
`graphviz-technical-flowchart`、`grilling`、`tdd`。
Claude 安装全部仓库技能，保留客户端已有的启用限制。本仓库没有新增 Claude 自定义子代理角色。

**已有设置优先：** 例如目标电脑原来有其他主模型，或者 `[agents].enabled = false`，安装器不会替你改掉。
两个同名 Luna 角色文件和本仓库技能的启用项则由仓库更新，并不是仅补缺失值。

### 4. 安装后：按使用场景手动完成

| 场景 | 还需要手动配置什么 |
|---|---|
| 开始使用 | 重新启动 Claude Code / Codex，让新规则、技能和角色被加载；登录后先确认普通对话可以使用 |
| 默认模型不可用 | 在目标电脑选择账号支持的主模型；Codex 主模型在 `~/.codex/config.toml`，Claude 在其设置中。安装脚本不检查模型授权，也不会自动切换付费模型 |
| 要使用 Luna 子代理 | 确认当前 Codex 版本支持角色配置、服务商可调用 `gpt-5.6-luna`，并检查已有 `[agents]` 设置是否关闭了代理。本机模板曾用 CLI 0.155.1 验证，不能据此保证所有旧版本兼容 |
| 要调整子代理模型/规则 | 修改仓库的 `config/codex/agents/*.toml` 和 `config/codex/delegation.md` 后重装；直接改安装后的角色文件会在下次安装时被仓库版本覆盖 |
| 要启用其他 Codex 技能 | 修改仓库 `config/codex/enabled-skills.json` 后重装；手改对应安装条目的启用状态会被下次安装重设 |
| 要用联网/平台技能 | 按对应 `SKILL.md` 准备外部 CLI、登录态和平台授权。例如 agent-reach 需要自身工具与渠道配置，GitHub 操作需要 gh 及认证。技能文件存在不等于外部能力已经可用 |
| 要用 Graphviz 等本地工具 | 按技能实际需求安装 Graphviz 或其他运行依赖；本仓库不统一安装全部技能依赖 |
| 要用 MCP、插件、Lark 等 | 单独安装服务/插件，配置本机端点、密钥和登录态；这些外部能力不随配置包迁移 |
| 要用知识库或项目专用配置 | 准备自己的知识库、数据/模型路径、项目授权和项目级指令；不会复制旧电脑的目录与信任记录 |

### 5. 选择 `--with-manager` 时，多做哪些准备？

这部分只在选择 Manager 时需要，普通规则/技能安装不依赖它。

- **安装前手动准备：** Linux（或可运行 Kitty 的 WSL 图形环境）、uv、Kitty >= 0.26.0；运行任务 TUI 还需要 tmux，看板跳转需要 wmctrl。
- **脚本自动完成：** 克隆或复用 `claude-manager`，调用其安装器安装管理命令、Kitty 配置、Claude hooks、shell 函数和 Codex wrapper；调用前备份相关配置。
- **安装后手动完成：** 确保 `~/.local/bin` 在 PATH 中，按 Manager 提示重新加载 shell/Kitty；新 shell 没有加载对应 rc 时需要自行配置。脚本不自动重启终端。
- **已有 Manager 工程：** 使用 `--manager-dir` 指定；安装器不会自动更新或重置该工程，需要你自行同步其代码。
- **飞书桥接等可选功能：** 仍需在 Manager 中单独配置账号/密钥等，本仓库不迁移这部分状态。

`--with-manager` 使用上游 **full** 安装，会替换 Kitty 主配置与同名脚本。
上游 shell 函数还设置 `CLAUDE_DEFAULT_FLAGS=--dangerously-skip-permissions` 的默认值，
通过这些函数启动 Claude 时应了解该权限行为。只想安装规则和技能时，使用 `bash install.sh` 即可。

详细的合并、备份与恢复行为见 [跨电脑配置说明](config/README.md)。

以下技能目录是原有分类索引，完整安装集合由各目录的 `SKILL.md` 自动发现。

## 📚 Skills 目录

### 🔬 学术研究
| Skill | 描述 |
|-------|------|
| [arxiv-search](./arxiv-search) | 搜索 arXiv 预印本论文（物理、数学、计算机科学） |
| [paper-notes](./paper-notes) | 为论文生成结构化笔记（summary/method/results/limitations） |
| [lit-review-assistant](./lit-review-assistant) | 经济学文献综述助手 |
| [kaggle](./kaggle) | Kaggle 竞赛、数据集、Notebook、GPU/TPU |

### 🌐 Web 与数据
| Skill | 描述 |
|-------|------|
| [url-summarize](./url-summarize) | 总结/解读网页链接内容 |
| [web-scraping](./web-scraping) | 网页爬取（反爬、Paywall、社交媒体） |
| [xhs-topic-analysis](./xhs-topic-analysis) | 小红书话题深度分析 |

### 🤖 AI 模型集成
| Skill | 描述 |
|-------|------|
| [codex-cli](./codex-cli) | OpenAI Codex CLI 集成（GPT-5.2、o3、o4-mini） |
| [codex-skill](./codex-skill) | Codex 自主代码实现 |
| [hugging-face-datasets](./hugging-face-datasets) | Hugging Face 数据集管理 |

### 📁 文件与知识管理
| Skill | 描述 |
|-------|------|
| [file-organizer](./file-organizer) | 智能文件整理（去重、归类） |
| [knowledge-query](./knowledge-query) | 查询本地知识库（公式、易错点） |
| [save-knowledge](./save-knowledge) | 提取对话知识保存到知识库 |
| [obsidian-markdown](./obsidian-markdown) | Obsidian Markdown 语法 |
| [obsidian-bases](./obsidian-bases) | Obsidian Bases 数据库 |
| [json-canvas](./json-canvas) | Obsidian Canvas 画布 |

### 🛠️ 开发工作流
| Skill | 描述 |
|-------|------|
| [dev-plan](./dev-plan) | 功能开发方案设计 |
| [project-audit](./project-audit) | 项目审计（风险/优化/规范） |
| [document-project](./document-project) | 创建项目 CLAUDE.md 文档 |
| [auto-commit](./auto-commit) | 自动 git 提交推送 |
| [find-skills](./find-skills) | 发现安装新技能 |
| [my-skills](./my-skills) | 查看/更新技能速查表 |

### 🎨 UI 与设计
| Skill | 描述 |
|-------|------|
| [ui-mockup](./ui-mockup) | 生成 HTML 交互原型 |

## 🚀 快速开始

### 调用 Skills

使用 `/` 命令调用：
```
/dev-plan 新功能设计
/project-audit 风险项
/url-summarize https://...
/xhs 扫地机器人
/kaggle 竞赛列表
```

### 常用命令

| 命令 | 功能 |
|------|------|
| `/my-skills` | 查看所有可用技能 |
| `/my-skills 更新` | 重新扫描并更新技能列表 |
| `/find-skills` | 发现新技能 |

## 📂 目录结构

```
.
├── arxiv-search/          # 论文搜索
├── auto-commit/           # 自动提交
├── codex-cli/             # Codex CLI
├── codex-skill/          # Codex 实现
├── dev-plan/             # 开发方案
├── document-project/     # 项目文档
├── file-organizer/       # 文件整理
├── find-skills/          # 技能发现
├── hugging-face-datasets/# HF 数据集
├── json-canvas/          # Canvas 画布
├── kaggle/               # Kaggle
├── knowledge-query/      # 知识查询
├── lit-review-assistant/ # 文献综述
├── my-skills/            # 技能速查
├── obsidian-bases/       # Obsidian 数据库
├── obsidian-markdown/    # Obsidian MD
├── paper-notes/          # 论文笔记
├── project-audit/       # 项目审计
├── save-knowledge/       # 保存知识
├── ui-mockup/            # UI 原型
├── url-summarize/        # 链接总结
├── web-scraping/         # 网页爬取
└── xhs-topic-analysis/   # 小红书分析
```

## 📝 更新日志

### 2025-03-12
- 将软链接转换为实际目录：
  - arxiv-search
  - codex-cli
  - codex-skill
  - file-organizer
  - lit-review-assistant
  - paper-notes
