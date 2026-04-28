---
name: cmd-notes
description: Use when user wants to quickly memo a command they just used in the current project. Triggers include "/cmd-note", "记一下命令", "速记", "记住这个命令", "/cmd-note 查询". Stores per-project commands in a self-contained HTML file at the project root (cmd_notes.html). Both Claude (via /cmd-note) and the user (via in-browser editing) can add/edit/delete entries. Light bright theme.
---

# Command Notes (cmd-notes)

每个工程一个 `cmd_notes.html` 文件，放在工程根目录。Claude 和用户都能往里加命令——Claude 通过 `/cmd-note` 命令解析自然语言，用户通过浏览器内的编辑界面。**单文件自包含**：数据嵌入在 HTML 的 `<script type="application/json">` 标签里。

## 触发条件

| 触发 | 例子 |
|------|------|
| `/cmd-note <命令> [说明] [#标签]` | `/cmd-note docker exec -it det_docker bash 进入检测容器 #docker` |
| 自然语言 | "帮我记一下 nvidia-smi -l 1，看 GPU 占用" |
| 查询 | "我之前记的进入容器的命令是什么"、"/cmd-note 查询 容器" |

## 工作流程

```
1. 解析意图：是新增？是查询？是编辑？是删除？

2. 找项目根：
   - 从 cwd 向上找 .git → CLAUDE.md → pyproject.toml → package.json
   - 找不到就用 cwd
   - helper: cmd_notes_helper.find_project_root()

3. 找 cmd_notes.html：
   - 项目根下的 cmd_notes.html
   - 不存在 → 用 template.html 创建一个
   - helper: cmd_notes_helper.ensure_notes_file()

4. 操作（按意图分支）：
   - 新增 → cmd_notes_helper.add_note(...)
   - 查询 → cmd_notes_helper.query_notes(...)
   - 编辑 → cmd_notes_helper.update_note(...)
   - 删除 → cmd_notes_helper.delete_note(...)

5. 报告结果：
   - 新增/编辑/删除：告诉用户文件路径 + 当前总条数
   - 查询：列出匹配条目
```

## 用法

### 新增命令

**最简形式**（只有命令）：
```
/cmd-note nvidia-smi -l 1
```
Claude 会问标题和说明，或者自动从命令推断标题。

**完整形式**：
```
/cmd-note docker exec -it det_docker bash | 进入检测容器 | host 上调试 detection 时用 | docker, det
```
用 `|` 分隔字段：命令 | 标题 | 说明 | 标签

**自然语言**：
```
帮我记一下 nvidia-smi -l 1，每秒看 GPU 占用，标签 monitor
```
Claude 解析后调用 helper。

### 查询

```
/cmd-note 查询 容器
我之前记的进入容器的命令是什么
```
Claude 读 HTML，搜索匹配项，列出来。

### 编辑/删除

主要在浏览器内做。如果用户明确说"删掉那条 xxx"，可以走 helper。

## 必须使用 cmd_notes_helper.py

```python
import sys
sys.path.insert(0, "/home/qwer/.claude/skills/cmd-notes")
from cmd_notes_helper import (
    find_project_root, ensure_notes_file,
    add_note, update_note, delete_note,
    query_notes, suggest_tags, list_all_notes,
)

# Add a note
project = find_project_root(os.getcwd())
notes_path = ensure_notes_file(project)  # creates from template if missing
add_note(
    notes_path,
    title="进入检测容器",
    command="docker exec -it det_docker bash",
    description="host 上调试 detection 时进入 container",
    tags=["docker", "det"],
)

# Query
results = query_notes(notes_path, "容器")  # returns list of matching notes

# List all
all_notes = list_all_notes(notes_path)
```

## 自动推断字段

### 标题（如果用户没给）
- 优先使用用户的「说明」前 20 字
- 退化到命令的第一个动作词（`docker exec` → "docker exec"）

### 标签自动建议
基于命令首词或关键词：

| 命令包含 | 建议标签 |
|----------|---------|
| `docker` | `docker` |
| `git` | `git` |
| `ros2`, `colcon` | `ros2` |
| `nvidia-smi`, `gpustat` | `gpu`, `monitor` |
| `python xxx.py train` | `train`, `python` |
| `python xxx.py test` / `eval` | `test`, `python` |
| `bash xxx.sh` | `bash` |
| `pip`, `conda` | `env` |
| `tmux`, `screen` | `session` |
| `ssh`, `scp`, `rsync` | `remote` |
| `kubectl`, `helm` | `k8s` |

`suggest_tags(command)` 已实现这套规则，Claude 可以直接调用。

### 工作目录
自动捕获 `os.getcwd()`。

### 时间
自动 `datetime.now().isoformat()`。

## 输出格式

操作完成后告诉用户：
1. 文件路径（绝对路径）
2. 当前总条数
3. 用 `xdg-open` 打开

```
✅ 已记录命令到:
   /home/qwer/charger_program/CenterNet/cmd_notes.html
   当前共 12 条命令

   打开查看: xdg-open /home/qwer/charger_program/CenterNet/cmd_notes.html
```

查询时直接列出匹配项：

```
🔍 找到 2 条匹配 "容器" 的命令:

1. 进入检测容器
   docker exec -it det_docker bash
   tags: docker, det · 2026-04-11 19:30

2. 重启容器
   docker restart det_docker
   tags: docker · 2026-04-11 19:25
```

## 找不到项目根 / 文件冲突

- **找不到项目根**：直接用 cwd，告诉用户"未检测到项目标记，已使用当前目录"
- **HTML 文件解析失败**：报错，不要瞎覆盖；让用户检查文件
- **JSON 字段缺失**：用默认值补齐，不要崩
