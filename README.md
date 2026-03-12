# Claude Code Skills

个人 Claude Code 技能集，包含 23 个自定义 Skills，用于增强 AI 辅助开发体验。

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
