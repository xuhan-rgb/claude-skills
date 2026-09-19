# OpenAI Codex CLI Skills for Claude Code

Complete integration between Claude Code and OpenAI Codex CLI, enabling powerful AI-to-AI collaboration with full automation capabilities.

**Last Updated**: December 2025 (GPT-5.2 Release)

## 📦 What's Included

This package provides 6 comprehensive skills for using OpenAI Codex CLI within Claude Code:

1. **codex-cli** - Main integration with full automation modes
2. **codex-auth** - Authentication management (OAuth + API keys)
3. **codex-tools** - Tool execution and automation patterns
4. **codex-chat** - Interactive REPL workflows
5. **codex-review** - Automated code review and PR workflows
6. **codex-git** - Git-aware development and commit automation

**Bonus**: Complete Claude + Codex integration guide (`CLAUDE-CODEX-INTEGRATION.md`)

## 🚀 Quick Start

### 1. Install Codex CLI

```bash
# Via NPM (recommended)
npm install -g @openai/codex

# Via Homebrew
brew install openai/tap/codex-cli

# Verify installation
codex --version  # Should show 0.60.1 or later
```

### 2. Authenticate

**Option A: ChatGPT Plus/Pro (Recommended)**
```bash
codex login
# Opens browser for OAuth authentication
# Includes GPT-5-Codex access with subscription
```

**Option B: API Key**
```bash
export OPENAI_API_KEY="sk-your-api-key-here"
# Or create ~/.codex/config.toml with api_key
```

### 3. Test Integration

```bash
# Simple test
codex exec "What is 2+2?"

# Full automation test
codex exec --dangerously-bypass-approvals-and-sandbox \
  "List all JavaScript files in current directory"

# With Claude orchestrating
# Claude can now direct Codex to perform tasks with full automation
```

## 🎯 Key Features

### Full Automation Mode

The `--dangerously-bypass-approvals-and-sandbox` flag provides **complete automation** with zero friction:

```bash
# Zero approvals, zero sandbox restrictions
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Refactor entire authentication module with tests"

# Shorter alternative: --full-auto (sandboxed)
codex exec --full-auto "Generate tests for all functions"
```

### Available Models (December 2025)

**GPT-5.2 Series (NEW - December 11, 2025):**
- `gpt-5.2` - Latest frontier model (400K context, 128K output)
- `gpt-5.2-pro` - Maximum accuracy (xhigh reasoning)
- `gpt-5.2-chat-latest` - Speed-optimized for routine queries

**GPT-5.1 Codex Series (Recommended for Coding):**
- `gpt-5.1-codex-max` - **DEFAULT** for Codex CLI (best for agentic coding)
- `gpt-5.1-codex` - Optimized for long-running agentic tasks
- `gpt-5.1-codex-mini` - Cost-efficient coding

**o-Series (Reasoning):**
- `o3` - Smartest reasoning model (for architecture, complex decisions)
- `o4-mini` - Efficient reasoning (for quick analysis)

**Model Selection Guide (December 2025):**
```bash
# Quick tasks → o4-mini or gpt-5.1-codex-mini
codex exec -m o4-mini "Format code with Prettier"

# Standard development → gpt-5.1-codex-max (DEFAULT)
codex exec -m gpt-5.1-codex-max "Implement user authentication"

# Long-context tasks → gpt-5.2 (400K context)
codex exec -m gpt-5.2 "Analyze entire codebase"

# Maximum accuracy → gpt-5.2-pro with xhigh reasoning
codex exec -m gpt-5.2-pro --reasoning-effort xhigh "Critical architecture"

# Complex reasoning → o3
codex exec -m o3 "Design scalable microservices architecture"
```

### Git-Aware Workflows

Codex understands git context and can manage commits automatically:

```bash
# Apply Codex changes as git patch
codex apply  # or: codex a

# Generate intelligent commits
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Review changes and create semantic commits"

# Complete PR workflow
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Create feature branch, implement auth, commit, and create PR"
```

### AI-to-AI Collaboration

Claude orchestrates, Codex executes - the **Think-Act-Observe Loop**:

```bash
#!/bin/bash
# Claude THINKS: What needs to be done?

# Claude directs Codex to ACT:
codex exec --json --dangerously-bypass-approvals-and-sandbox \
  "Analyze ./src and return structured data" \
  > analysis.json

# Claude OBSERVES results:
cat analysis.json | jq .

# Claude directs next action:
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Implement recommendations from @analysis.json"
```

## 📚 Skills Overview

### 1. codex-cli (Core Integration)

Main integration skill covering:
- Installation and setup
- All automation modes (`--dangerously-bypass-approvals-and-sandbox`, `--full-auto`, `-a`, `-s`)
- All available models (GPT-5.2, GPT-5.1-Codex-Max, o3, o4-mini)
- Claude + Codex collaboration patterns
- Configuration and best practices

**Key Commands (December 2025):**
```bash
# Direct execution
codex exec "prompt"

# Full automation
codex exec --dangerously-bypass-approvals-and-sandbox "task"

# With specific model
codex exec -m gpt-5.1-codex-max "complex code task"  # Default
codex exec -m gpt-5.2 "tasks needing 400K context"
codex exec -m gpt-5.2-pro "maximum accuracy tasks"

# With web search
codex exec --search "research and implement"

# JSON output
codex exec --json "structured output"
```

### 2. codex-auth (Authentication)

Complete authentication management:
- ChatGPT Plus/Pro OAuth setup
- API key configuration (environment, config file, per-project)
- Multi-account management
- Secure API key storage (pass, macOS Keychain)
- CI/CD integration (GitHub Actions, GitLab CI, Docker)
- Configuration profiles

**Key Commands:**
```bash
# Login with ChatGPT
codex login

# Set API key
export OPENAI_API_KEY="sk-..."

# Check status
codex exec "What account am I using?"

# Logout
codex logout
```

### 3. codex-tools (Tool Execution)

Comprehensive tool execution patterns:
- Full automation workflows
- Batch processing
- File operations (read, modify, generate, organize)
- Shell commands
- Web search integration
- Safety patterns (backups, scoped execution)

**Key Patterns:**
```bash
# Batch processing
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Add JSDoc comments to all *.js files"

# Scoped automation
codex exec --dangerously-bypass-approvals-and-sandbox \
  -C ./src/auth \
  "Only modify authentication module"

# With backup
git stash push -m "backup"
codex exec --dangerously-bypass-approvals-and-sandbox "refactor"
```

### 4. codex-chat (Interactive Mode)

Interactive REPL workflows:
- Session management (resume, apply changes)
- Multimodal support (code + images)
- Web search in interactive mode
- Automated development sessions
- Continuous development workflows

**Key Commands:**
```bash
# Start interactive session
codex "Let's work on authentication"

# With full automation
codex --dangerously-bypass-approvals-and-sandbox "Auto-execute everything"

# With images
codex -i design.png "Implement this UI"

# Resume last session
codex exec resume --last
```

### 5. codex-review (Code Review)

Automated code review workflows:
- Automated codebase review
- Git diff analysis
- PR review automation
- Apply Codex suggestions
- Complete review workflows with fixes

**Key Patterns:**
```bash
# Full automated review
codex exec --json --dangerously-bypass-approvals-and-sandbox \
  "Review entire codebase and generate prioritized report" \
  > review-report.json

# Review uncommitted changes
git diff | codex exec --dangerously-bypass-approvals-and-sandbox \
  "Review this diff and suggest improvements"

# PR review
gh pr view 123 --json diff | \
  codex exec --dangerously-bypass-approvals-and-sandbox \
  "Review PR and provide detailed feedback"
```

### 6. codex-git (Git Integration)

Git-aware development:
- Intelligent commit generation (conventional commits, semantic commits)
- PR automation (create branch, commit, push, create PR)
- Branch management
- Git history analysis
- Conflict resolution
- Changelog generation

**Key Patterns:**
```bash
# Apply Codex changes
codex apply  # or: codex a

# Generate commits
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Create semantic commits for all changes"

# Complete PR workflow
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Create feature branch feature/auth, implement OAuth2, commit, push, create PR"

# Resolve conflicts
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Resolve merge conflicts intelligently"
```

## 🎓 Claude + Codex Integration Guide

See `CLAUDE-CODEX-INTEGRATION.md` for comprehensive guide covering:

- **Think-Act-Observe Loop** - Claude orchestrates, Codex executes
- **Integration Patterns** - Research-driven, sequential decomposition, verification, parallel execution
- **Model Selection Strategy** - When to use o3 vs GPT-5.1-Codex vs o4-mini
- **Complete Feature Development** - Real-time notification system example (60 min, 100% automated)
- **Safety Patterns** - Git backups, dry-run, checkpoints, scoped automation
- **Structured Communication** - JSON for reliability, structured workflows
- **Error Handling** - Retry, fallback, automatic error analysis
- **Best Practices** - Planning, verification, atomic changes, documentation

## 💡 Usage Examples

### Example 1: Quick Code Fix

```bash
# Simple task with full automation
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Fix the race condition in user session handling and add tests"
```

### Example 2: Feature Development

```bash
#!/bin/bash
# Complete feature with Claude orchestrating

# 1. Research (Claude directs, Codex searches)
codex exec -m o3 --search --dangerously-bypass-approvals-and-sandbox \
  "Research OAuth2 best practices 2025" \
  > research.md

# 2. Plan (Claude reviews, Codex plans)
codex exec -m gpt-5.1-codex --json \
  "Create implementation plan based on @research.md" \
  > plan.json

# 3. Implement (Codex executes with full automation)
codex exec -m gpt-5.1-codex --dangerously-bypass-approvals-and-sandbox \
  "Implement OAuth2 according to @plan.json with comprehensive tests"

# 4. Verify (Claude checks results)
codex exec --json --dangerously-bypass-approvals-and-sandbox \
  "Run all tests and return results" \
  > results.json
```

### Example 3: Code Review Automation

```bash
# Automated PR review with fixes
gh pr view 123 --json diff > pr.json

codex exec --dangerously-bypass-approvals-and-sandbox \
  "Review PR in @pr.json, provide feedback, and auto-fix all issues"
```

### Example 4: Refactoring with Safety

```bash
# Safe refactoring with git backup
git stash push -m "pre-refactor"

codex exec --dangerously-bypass-approvals-and-sandbox \
  "Refactor authentication module:
  1. Apply modern patterns
  2. Add error handling
  3. Update tests
  4. Run tests and fix failures
  5. Create semantic commits"

# Review changes
git diff

# Keep or revert
git stash pop  # if needed
```

## ⚙️ Configuration

### Config File (~/.codex/config.toml)

```toml
# Default model (December 2025)
model = "gpt-5.1-codex-max"  # Best for agentic coding

# Full automation (no approvals)
ask_for_approval = "never"

# Workspace write access
sandbox = "workspace-write"

# Enable web search
search = true

# GPT-5.2 specific settings
reasoning_effort = "high"  # medium, high, xhigh
compact = false            # Enable context compaction

# Profiles for different workflows
[profiles.safe]
ask_for_approval = "untrusted"
sandbox = "read-only"

[profiles.auto]
ask_for_approval = "never"
sandbox = "workspace-write"
search = true

[profiles.danger]
ask_for_approval = "never"
sandbox = "danger-full-access"
search = true

# GPT-5.2 profiles (NEW)
[profiles.gpt52]
model = "gpt-5.2"
ask_for_approval = "never"
sandbox = "workspace-write"

[profiles.gpt52-pro]
model = "gpt-5.2-pro"
reasoning_effort = "xhigh"
ask_for_approval = "on-request"
```

### Environment Variables

```bash
# Authentication
export OPENAI_API_KEY="sk-your-api-key"

# Default model (December 2025)
export CODEX_MODEL="gpt-5.1-codex-max"

# GPT-5.2 specific
export CODEX_REASONING_EFFORT="high"  # medium, high, xhigh
```

## 🔒 Safety & Best Practices

### When to Use `--dangerously-bypass-approvals-and-sandbox`

**✅ Safe Scenarios:**
- Trusted, repeatable workflows
- CI/CD (externally sandboxed)
- Docker containers
- Feature branches (can revert)
- With git backups

**⚠️ Use with Caution:**
- Production environments
- Shared repositories
- Untested workflows
- Without backups

### Safety Checklist

1. **Always Have Backups**
   ```bash
   git stash push -m "backup"
   ```

2. **Work on Branches**
   ```bash
   git checkout -b experiment
   ```

3. **Review Changes**
   ```bash
   git diff
   codex apply  # Only after review
   ```

4. **Limit Scope**
   ```bash
   codex exec --dangerously-bypass-approvals-and-sandbox \
     -C ./specific/directory \
     "Only affect this directory"
   ```

## 🆚 Codex vs Gemini vs Claude

### When to Use Each

**Codex (OpenAI)**
- Best for: Code generation, refactoring, advanced reasoning
- Models: GPT-5.1-Codex, o3 (smartest reasoning)
- Strengths: Latest models, git-aware, multimodal
- Use when: Need cutting-edge models or complex reasoning

**Gemini (Google)**
- Best for: Fast iteration, Google ecosystem integration
- Models: Gemini 2.5 Pro, 2.5 Flash
- Strengths: Speed, web search, MCP servers
- Use when: Need Google integration or rapid development

**Claude (Anthropic)**
- Best for: Orchestration, planning, strategic decisions
- Models: Claude Sonnet 4.5
- Strengths: Context management, systematic thinking
- Use when: Complex workflows, quality-first development

**Recommended**: Use Claude to orchestrate both Codex and Gemini for maximum power!

## 📖 Documentation

- **codex-cli/SKILL.md** - Main integration guide
- **codex-auth/SKILL.md** - Authentication setup
- **codex-tools/SKILL.md** - Tool execution patterns
- **codex-chat/SKILL.md** - Interactive workflows
- **codex-review/SKILL.md** - Code review automation
- **codex-git/SKILL.md** - Git-aware development
- **CLAUDE-CODEX-INTEGRATION.md** - Complete integration guide

## 🔗 Related Skills

### Gemini CLI Skills
- `gemini-cli` - Gemini CLI integration
- `gemini-auth` - Gemini authentication
- `gemini-tools` - Gemini tool execution
- `gemini-chat` - Gemini interactive mode
- `gemini-mcp` - MCP server integration

### Ecosystem Skills
- `skill-builder-generic` - Build Claude Code skills
- `review-multi` - Multi-dimensional skill reviews
- `skill-researcher` - Research patterns and best practices

## 🚀 Getting Started

1. **Install Codex CLI**
   ```bash
   npm install -g @openai/codex
   ```

2. **Authenticate**
   ```bash
   codex login  # or set OPENAI_API_KEY
   ```

3. **Test Basic Usage**
   ```bash
   codex exec "List files in current directory"
   ```

4. **Try Full Automation**
   ```bash
   codex exec --dangerously-bypass-approvals-and-sandbox \
     "Analyze this codebase and suggest improvements"
   ```

5. **Read Integration Guide**
   - Open `CLAUDE-CODEX-INTEGRATION.md`
   - Review Think-Act-Observe Loop
   - Try the examples

6. **Build Something**
   - Use the complete feature development example
   - Let Claude orchestrate, Codex execute
   - Enjoy 100% automation!

## 📝 License

Created for Claude Code by the Skrillz ecosystem.

Part of the Self-Sustaining Skill Development Ecosystem.

## 🙏 Acknowledgments

- OpenAI for Codex CLI
- Anthropic for Claude Code
- The Claude Code community

---

**Ready to collaborate with AI?** Start with the integration guide and build your first fully automated feature! 🚀
