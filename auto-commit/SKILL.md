---
name: auto-commit
description: Use when you have staged changes and need to commit and push automatically with generated commit message
---

# Auto-Commit

## Overview

Automates the git workflow: analyze staged files → generate commit message → execute commit → push to remote. Saves repetitive manual work while maintaining quality through user confirmation.

## When to Use

- You have files staged (`git add` already done)
- Ready to commit those changes
- Want automatic commit message generation based on file diffs
- Ready to push immediately after commit
- Want to avoid manual message writing

## When NOT to Use

- Files are not yet staged
- Unsure about the changes
- Performing a complex commit with specific message requirements
- Need to review all diffs before committing

## Quick Reference

```bash
auto-commit
# Prompts: 1) Review generated message 2) Confirm push 3) Show results
```

**Flow:**
1. Check git status (errors if nothing staged)
2. Analyze file changes → generate message
3. Show message to user → ask confirmation
4. If yes: commit + push
5. Show results

## Implementation

### Step 0: Pre-Check - 智能检测

自动扫描暂存的文件，检测潜在的不完善改动：

| 检测项 | 警告场景 | 建议 |
|--------|--------|------|
| 代码 vs 配置 | 改了 `.py` 但没改 `requirements.txt` | 检查是否需要更新依赖 |
| 配置 vs 代码 | 改了 `package.json` 但没改代码 | 检查是否需要实现功能 |
| 文档孤立 | 仅改了 `.md` 文件，没有代码改动 | 确认文档对应的代码是否需要更新 |
| 单文件改动 | 仅修改一个源代码文件 | 检查改动是否完整 |
| 关键文件检测 | 改了 README 但没改对应的代码/配置 | 确认是否需要实现相应改动 |

**警告时的交互：**
```
⚠️  检测到潜在问题：
  ⚠️  代码文件已修改，但依赖/配置文件未改动。请确认配置是否需要更新。

继续提交？[y/n]:
```

### Step 1: Check Staged Files

```bash
git diff --cached --stat
```

**Success:** Shows file list and stats
**Error:** "No staged changes found" → 提醒用户执行 `git add`

### Step 2: Generate Commit Message

Analyze the diffs to suggest a category:
- `docs:` - documentation changes (README, COMMANDS, .md files)
- `fix:` - bug fixes
- `feat:` - new features
- `refactor:` - code refactoring
- `test:` - test additions/changes
- `chore:` - build, config, dependencies

**Command to analyze:**
```bash
git diff --cached --name-only | head -5
git diff --cached | head -100  # See what changed
```

### Step 3: Show Generated Message & Confirm

**Example generated message:**
```
docs: optimize README documentation structure and improve gitty-enhance section

- Reorganize docs to prioritize Kitty optimization approach
- Add configuration change warnings for each installation method
- Improve Kitty config loading with load-config command
- Complete Claude status indication flowchart
- Add Tmux development-in-progress notice
```

**User decision:**
- ✅ Accept → proceed to commit
- ✏️ Edit → modify message
- ❌ Cancel → exit without committing

### Step 4: Execute Commit

```bash
git commit -m "Your message here"
```

**Success check:**
```
[main abc1234] docs: optimize README...
 5 files changed, 243 insertions(+), 37 deletions(-)
```

### Step 5: Execute Push

```bash
git push origin $(git branch --show-current)
```

**Success output:**
```
Enumerating objects: 7, done.
...
 main -> main
```

**Common error:** "fatal: The current branch has no upstream branch"
- Solution: Push with `-u` flag

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Files not staged | Run `git add` first, then use auto-commit |
| Forget to review message | Always show message before committing |
| Push without commit | Commit MUST succeed before pushing |
| Generic message "update" | Analyze diffs to generate specific messages |
| Push fails silently | Check and show push output to user |

## Error Handling

**No staged changes:**
```
❌ Error: No files staged for commit
Use: git add <file> or git add .
```

**Commit fails:**
```
❌ Commit failed: [error message]
Fix the issue and try again
```

**Push fails (no upstream):**
```
❌ Push failed: no upstream branch
Use: git push -u origin [branch]
```

**Push fails (network):**
```
❌ Push failed: network error
Check your connection and try: git push origin [branch]
```

## Example Workflow

**Scenario:** You modified README.md, COMMANDS.md, and some hook files

```bash
$ auto-commit

✅ Staged changes found:
 COMMANDS.md                    |   7 +
 README.md                      | 253 ++++++++++
 kitty-enhance/hooks/*.sh       |  20 +-
 5 files changed, 243 insertions(+), 37 deletions(-)

📝 Generated commit message:
─────────────────────────────────────────
docs: optimize README documentation structure

- Reorganize docs for Kitty optimization priority
- Add installation configuration warnings
- Improve Kitty config loading instructions
- Complete Claude status flowchart
- Add Tmux development notice
─────────────────────────────────────────

Use this message? [y/e/n]
→ y

✅ Committed: [main abc1234]
↑ Pushing to origin/main...
✅ Pushed successfully

Done! Changes are on remote.
```

## Advanced: Custom Message

If you want to edit the auto-generated message:

```bash
auto-commit
# When prompted with message: press 'e' to edit
# Your editor opens → make changes → save and exit
# Message is used for commit
```

## Notes

- Always review the generated message before confirming
- Push only to current branch (no cross-branch pushes)
- If push fails due to rejected changes, pull first: `git pull --rebase`
- Co-author footer added automatically: `Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>`
