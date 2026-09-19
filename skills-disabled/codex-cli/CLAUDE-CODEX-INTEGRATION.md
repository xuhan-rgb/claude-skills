# Claude + Codex Integration Guide

Complete guide for AI-to-AI collaboration between Claude Code and OpenAI Codex CLI.

## Table of Contents

1. [The Think-Act-Observe Loop](#the-think-act-observe-loop)
2. [Integration Patterns](#integration-patterns)
3. [Model Selection Strategy](#model-selection-strategy)
4. [Complete Feature Development](#complete-feature-development)
5. [Safety Patterns](#safety-patterns)
6. [Structured Communication](#structured-communication)
7. [Error Handling](#error-handling)
8. [Best Practices](#best-practices)

## The Think-Act-Observe Loop

**Core Principle**: Claude orchestrates, Codex executes. Claude makes strategic decisions, Codex handles tactical implementation with full automation.

### Basic Pattern

```bash
#!/bin/bash
# Claude THINKS: What needs to be done?
# Goal: Add user caching system

# Claude directs Codex to ACT (with full automation):
codex exec --dangerously-bypass-approvals-and-sandbox \
  "List all functions in ./src/auth.js" \
  > auth-functions.txt

# Claude OBSERVES results:
cat auth-functions.txt

# Claude THINKS: Need to add caching to login function

# Claude directs atomic action:
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Add Redis caching to login function in ./src/auth.js"

# Claude directs verification:
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Run auth tests and report results"

# Loop continues...
```

### Advanced Loop with JSON

```bash
#!/bin/bash
# Claude THINKS: Need structured analysis for decision-making

# ACT: Get JSON output for reliable parsing
codex exec --json --dangerously-bypass-approvals-and-sandbox \
  "Analyze ./src/auth.js and return JSON:
  {
    'functions': [...],
    'complexity': {...},
    'issues': [...],
    'recommendations': [...]
  }" \
  > analysis.json

# OBSERVE: Parse JSON reliably
echo "Functions found: $(jq '.functions | length' analysis.json)"
echo "Critical issues: $(jq '.issues[] | select(.severity == "critical")' analysis.json)"

# THINK: Based on analysis, decide next action

# ACT: Execute decision with full automation
for issue in $(jq -r '.issues[].id' analysis.json); do
  codex exec --dangerously-bypass-approvals-and-sandbox \
    "Fix issue $issue from analysis and run tests"
done
```

## Integration Patterns

### Pattern 1: Research-Driven Development

Claude orchestrates research, Codex executes with web search:

```bash
#!/bin/bash
# Phase 1: RESEARCH (Claude directs, Codex searches)
codex exec --search --dangerously-bypass-approvals-and-sandbox \
  --json \
  "Research GraphQL best practices 2025 and return structured findings" \
  > research.json

# Phase 2: ANALYZE (Claude processes research)
echo "Claude reviews research findings..."
jq '.findings' research.json

# Phase 3: PLAN (Claude creates plan, Codex validates)
codex exec --search --full-auto \
  "Based on @research.json, create implementation plan for GraphQL API" \
  > plan.md

# Phase 4: IMPLEMENT (Codex executes with full automation)
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Implement GraphQL API according to @plan.md with tests"

# Phase 5: VERIFY (Claude checks results)
codex exec --json --dangerously-bypass-approvals-and-sandbox \
  "Run all tests and return results as JSON" \
  > test-results.json
```

### Pattern 2: Sequential Task Decomposition

Claude breaks complex goals into safe atomic steps:

```bash
#!/bin/bash
# Complex Goal: Implement complete OAuth2 authentication

# STEP 1: Research (safe, read-only)
echo "=== Step 1: Research ==="
codex exec --search --full-auto \
  "Research OAuth2 best practices and security considerations 2025" \
  > oauth-research.md

# STEP 2: Plan (Claude reviews)
echo "=== Step 2: Planning ==="
codex exec --json \
  "Create detailed OAuth2 implementation plan based on @oauth-research.md" \
  > oauth-plan.json

read -p "Review plan. Continue? [y/N] " -r
[[ ! $REPLY =~ ^[Yy]$ ]] && exit 1

# STEP 3: Dependencies
echo "=== Step 3: Install Dependencies ==="
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Install OAuth2 packages per plan: passport, passport-oauth2, express-session"

# STEP 4: Implementation (full automation)
echo "=== Step 4: Core Implementation ==="
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Implement OAuth2 strategy according to @oauth-plan.json:
  1. Create OAuth2 config
  2. Implement auth routes
  3. Add session management
  4. Create middleware"

# STEP 5: Security (critical step)
echo "=== Step 5: Security Hardening ==="
codex exec --search --dangerously-bypass-approvals-and-sandbox \
  "Research OAuth2 security vulnerabilities and harden implementation:
  1. CSRF protection
  2. State parameter validation
  3. Secure token storage
  4. Rate limiting"

# STEP 6: Tests (verification)
echo "=== Step 6: Testing ==="
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Generate comprehensive OAuth2 tests:
  1. Unit tests for strategy
  2. Integration tests for flow
  3. Security tests
  4. Run all tests and fix failures"

# STEP 7: Documentation
echo "=== Step 7: Documentation ==="
codex exec --full-auto \
  "Generate OAuth2 setup documentation and API docs"

echo "=== OAuth2 implementation complete ==="
```

### Pattern 3: Continuous Verification

Every action followed by verification:

```bash
#!/bin/bash
# Pattern: ACT → VERIFY → DECIDE → ACT

verify_action() {
  local description="$1"
  local verification="$2"

  echo "Action: $description"

  # Codex verifies
  if codex exec --json --dangerously-bypass-approvals-and-sandbox "$verification" \
    | jq -e '.success == true' > /dev/null; then
    echo "✓ Verified"
    return 0
  else
    echo "✗ Verification failed"
    return 1
  fi
}

# Execute with verification
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Add input validation to user registration"

verify_action \
  "Input validation added" \
  "Run validation tests and return JSON with success field"

if [ $? -eq 0 ]; then
  # Continue to next step
  codex exec --dangerously-bypass-approvals-and-sandbox \
    "Add rate limiting to registration endpoint"
else
  # Fix the issue
  codex exec --dangerously-bypass-approvals-and-sandbox \
    "Debug validation test failures and fix"
fi
```

### Pattern 4: Parallel Execution with Synchronization

Claude coordinates multiple Codex tasks:

```bash
#!/bin/bash
# Execute independent tasks in parallel

# Task 1: Update backend
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Update backend API with new endpoints" \
  > backend-log.txt 2>&1 &
backend_pid=$!

# Task 2: Update frontend (independent)
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Update frontend to consume new API" \
  > frontend-log.txt 2>&1 &
frontend_pid=$!

# Task 3: Update tests (independent)
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Generate integration tests for new endpoints" \
  > tests-log.txt 2>&1 &
tests_pid=$!

# Wait for all tasks
wait $backend_pid
wait $frontend_pid
wait $tests_pid

# Claude synchronizes: Run integration tests
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Run full integration test suite and fix any failures"
```

## Model Selection Strategy

Choose the right Codex model for each task:

### Decision Matrix

```bash
#!/bin/bash
# Quick tasks: o4-mini (fastest, cheapest)
quick_task() {
  codex exec -m o4-mini --dangerously-bypass-approvals-and-sandbox "$@"
}

# Standard development: GPT-5.1-Codex (optimized for code)
dev_task() {
  codex exec -m gpt-5.1-codex --dangerously-bypass-approvals-and-sandbox "$@"
}

# Complex reasoning: o3 (smartest)
complex_task() {
  codex exec -m o3 --dangerously-bypass-approvals-and-sandbox "$@"
}

# General purpose: GPT-5 (balanced)
general_task() {
  codex exec -m gpt-5 --dangerously-bypass-approvals-and-sandbox "$@"
}

# Examples:
quick_task "Format code with Prettier"
dev_task "Implement user authentication module"
complex_task "Design scalable microservices architecture"
general_task "Generate project documentation"
```

### Model Characteristics

**GPT-5.1-Codex** (Recommended for most tasks)
- Optimized for software engineering
- Latest model (November 2025)
- Best for: Implementation, refactoring, testing
- Use when: Building features, writing code

**GPT-5.1-Codex-Mini**
- 4x more usage quota
- Cost-efficient
- Best for: Quick fixes, formatting, simple tasks
- Use when: High volume of simple operations

**o3**
- Smartest reasoning model
- Best for: Architecture, complex decisions, debugging
- Use when: Need deep analysis or reasoning

**o4-mini**
- Fast reasoning
- Best for: Quick decisions, simple reasoning
- Use when: Need speed over depth

**GPT-5**
- General purpose
- Best for: Mixed tasks (code + docs + analysis)
- Use when: Varied workflow

### Dynamic Model Selection

```bash
#!/bin/bash
# Claude chooses model based on task complexity

select_model_for_task() {
  local task="$1"
  local complexity="$2"  # simple, standard, complex, reasoning

  case $complexity in
    simple)
      echo "o4-mini"
      ;;
    standard)
      echo "gpt-5.1-codex"
      ;;
    complex)
      echo "gpt-5.1-codex"
      ;;
    reasoning)
      echo "o3"
      ;;
    *)
      echo "gpt-5.1-codex"  # Default
      ;;
  esac
}

# Example usage
model=$(select_model_for_task "Design database schema" "reasoning")
codex exec -m "$model" --dangerously-bypass-approvals-and-sandbox \
  "Design normalized database schema for e-commerce platform"
```

## Complete Feature Development

End-to-end example: Building a real-time notification system

```bash
#!/bin/bash
# Complete feature: Real-time notifications with WebSocket

echo "========================================="
echo "Feature: Real-time Notification System"
echo "========================================="

# PHASE 1: Research & Planning (5 minutes)
echo ""
echo "=== PHASE 1: Research & Planning ==="

# Research (o3 for reasoning)
codex exec -m o3 --search --dangerously-bypass-approvals-and-sandbox \
  "Research real-time notification architectures 2025:
  1. WebSocket vs SSE vs Long Polling
  2. Scaling strategies
  3. Security best practices
  4. Return recommendation with reasoning" \
  > notifications-research.md

# Plan (GPT-5.1-Codex for implementation planning)
codex exec -m gpt-5.1-codex --json --dangerously-bypass-approvals-and-sandbox \
  "Create detailed implementation plan based on @notifications-research.md:
  1. Technology choices
  2. Architecture design
  3. File structure
  4. Implementation steps
  5. Testing strategy
  Return as JSON" \
  > notifications-plan.json

echo "✓ Research and planning complete"
cat notifications-plan.json | jq '.architecture'

# PHASE 2: Setup & Dependencies (2 minutes)
echo ""
echo "=== PHASE 2: Setup & Dependencies ==="

codex exec -m gpt-5.1-codex-mini --dangerously-bypass-approvals-and-sandbox \
  "Install dependencies from @notifications-plan.json:
  - socket.io for WebSocket
  - redis for pub/sub
  - Required types and dev dependencies"

echo "✓ Dependencies installed"

# PHASE 3: Backend Implementation (15 minutes)
echo ""
echo "=== PHASE 3: Backend Implementation ==="

# WebSocket server (GPT-5.1-Codex for complex code)
codex exec -m gpt-5.1-codex --dangerously-bypass-approvals-and-sandbox \
  "Implement WebSocket notification server per @notifications-plan.json:
  1. Create NotificationService class
  2. Implement connection handling
  3. Add authentication middleware
  4. Create notification queuing with Redis
  5. Add reconnection logic
  6. Implement clean shutdown
  Create file: ./src/services/notifications.js"

# API endpoints (GPT-5.1-Codex)
codex exec -m gpt-5.1-codex --dangerously-bypass-approvals-and-sandbox \
  "Create notification REST API in ./src/routes/notifications.js:
  1. POST /notifications - Send notification
  2. GET /notifications/history - Get user notifications
  3. PUT /notifications/:id/read - Mark as read
  4. DELETE /notifications/:id - Dismiss
  Add proper validation and error handling"

# Database models (GPT-5.1-Codex-Mini for simple models)
codex exec -m gpt-5.1-codex-mini --dangerously-bypass-approvals-and-sandbox \
  "Create Notification model in ./src/models/notification.js with fields:
  - user, type, title, message, data, read, createdAt
  Add indexes for performance"

echo "✓ Backend implementation complete"

# PHASE 4: Frontend Implementation (10 minutes)
echo ""
echo "=== PHASE 4: Frontend Implementation ==="

# React hook (GPT-5.1-Codex)
codex exec -m gpt-5.1-codex --dangerously-bypass-approvals-and-sandbox \
  "Create useNotifications React hook in ./src/hooks/useNotifications.js:
  1. Manage WebSocket connection
  2. Handle incoming notifications
  3. Provide send/dismiss methods
  4. Auto-reconnect on disconnect
  5. TypeScript types included"

# UI components (GPT-5.1-Codex)
codex exec -m gpt-5.1-codex --dangerously-bypass-approvals-and-sandbox \
  "Create notification UI components:
  1. NotificationBell.tsx - Bell icon with badge
  2. NotificationList.tsx - Dropdown list
  3. NotificationItem.tsx - Individual notification
  4. Toast.tsx - Toast notifications
  Use Tailwind CSS for styling"

echo "✓ Frontend implementation complete"

# PHASE 5: Security Hardening (5 minutes)
echo ""
echo "=== PHASE 5: Security ==="

# Security analysis (o3 for reasoning)
codex exec -m o3 --search --dangerously-bypass-approvals-and-sandbox \
  "Analyze notification system for security vulnerabilities:
  1. Review authentication
  2. Check authorization (users see only their notifications)
  3. Validate XSS prevention
  4. Check rate limiting
  5. Implement fixes for any issues found"

echo "✓ Security hardening complete"

# PHASE 6: Testing (10 minutes)
echo ""
echo "=== PHASE 6: Testing ==="

# Generate tests (GPT-5.1-Codex)
codex exec -m gpt-5.1-codex --dangerously-bypass-approvals-and-sandbox \
  "Generate comprehensive test suite:
  1. Unit tests for NotificationService
  2. Integration tests for API endpoints
  3. WebSocket connection tests
  4. Frontend hook tests
  5. E2E tests for notification flow
  Achieve >90% coverage"

# Run tests (GPT-5.1-Codex-Mini for execution)
codex exec -m gpt-5.1-codex-mini --json --dangerously-bypass-approvals-and-sandbox \
  "Run all notification tests and return results as JSON:
  1. Run unit tests
  2. Run integration tests
  3. Run E2E tests
  4. Fix any failures
  5. Return coverage report" \
  > test-results.json

echo "Test results:"
cat test-results.json | jq '{passed: .passed, failed: .failed, coverage: .coverage}'

# PHASE 7: Documentation (5 minutes)
echo ""
echo "=== PHASE 7: Documentation ==="

codex exec -m gpt-5.1-codex --dangerously-bypass-approvals-and-sandbox \
  "Generate documentation:
  1. API documentation (OpenAPI/Swagger)
  2. WebSocket protocol documentation
  3. Frontend usage guide
  4. Deployment guide
  5. Add JSDoc comments to all functions
  Create: ./docs/notifications/"

echo "✓ Documentation complete"

# PHASE 8: Git Workflow (3 minutes)
echo ""
echo "=== PHASE 8: Git Workflow ==="

codex exec -m gpt-5.1-codex-mini --dangerously-bypass-approvals-and-sandbox \
  "Complete git workflow:
  1. Review all changes
  2. Create semantic commits:
     - feat: add WebSocket notification service
     - feat: add notification REST API
     - feat: add notification UI components
     - test: add notification test suite
     - docs: add notification documentation
  3. Push feature branch
  4. Create PR with detailed description"

echo "✓ Git workflow complete"

# PHASE 9: Final Verification (2 minutes)
echo ""
echo "=== PHASE 9: Final Verification ==="

codex exec -m o3 --json --dangerously-bypass-approvals-and-sandbox \
  "Final verification checklist:
  1. All tests passing
  2. Security checks passed
  3. Documentation complete
  4. Code quality metrics
  5. Performance benchmarks
  Return JSON report" \
  > final-verification.json

echo ""
echo "========================================="
echo "Feature Development Complete!"
echo "========================================="
cat final-verification.json | jq .

# Total time: ~60 minutes
# Total automation: 100%
# Human intervention: Code review only
```

## Safety Patterns

### Pattern 1: Git Backup Before Automation

```bash
#!/bin/bash
safe_automation() {
  local task="$1"

  # Create git backup
  git stash push -m "pre-codex-$(date +%s)"

  if codex exec --dangerously-bypass-approvals-and-sandbox "$task"; then
    echo "✓ Success! Backup: git stash list"
  else
    echo "✗ Failed! Restoring..."
    git stash pop
    return 1
  fi
}

# Usage
safe_automation "Refactor authentication module completely"
```

### Pattern 2: Dry-Run First

```bash
#!/bin/bash
# Generate plan without executing
codex exec \
  "Plan how to refactor database layer to use TypeORM" \
  > refactor-plan.md

# Review plan
cat refactor-plan.md

# Execute if approved
read -p "Execute this plan? [y/N] " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
  codex exec --dangerously-bypass-approvals-and-sandbox \
    "Execute refactoring plan in @refactor-plan.md"
fi
```

### Pattern 3: Checkpoint Commits

```bash
#!/bin/bash
# Create checkpoints during long refactoring
checkpoint_refactor() {
  local scope="$1"

  codex exec --dangerously-bypass-approvals-and-sandbox \
    "Refactor $scope with checkpoint commits:
    1. Create WIP commit at start
    2. Make incremental changes
    3. Commit after each logical step
    4. Run tests after each commit
    5. Revert if tests fail
    6. Continue until complete"
}

checkpoint_refactor "./src/database"
```

### Pattern 4: Scoped Automation

```bash
#!/bin/bash
# Limit blast radius
codex exec --dangerously-bypass-approvals-and-sandbox \
  -C ./src/auth \
  "Only modify files in authentication module"

# Multiple scoped directories
codex exec --dangerously-bypass-approvals-and-sandbox \
  --add-dir ./docs \
  --add-dir ./tests \
  "Can write to workspace, docs, and tests only"
```

## Structured Communication

### JSON for Reliability

```bash
#!/bin/bash
# Always use JSON for AI-to-AI communication

# Request structured output
codex exec --json --dangerously-bypass-approvals-and-sandbox \
  "Analyze ./src and return JSON:
  {
    'files': number,
    'functions': [{name, complexity, issues}],
    'recommendations': [{priority, description, impact}]
  }" \
  > analysis.json

# Parse reliably
high_priority=$(jq -r '.recommendations[] | select(.priority == "high") | .description' analysis.json)

# Execute based on structured data
for rec in $high_priority; do
  codex exec --dangerously-bypass-approvals-and-sandbox "Implement: $rec"
done
```

### Structured Workflows

```bash
#!/bin/bash
# Define workflow as JSON
cat > workflow.json << 'EOF'
{
  "workflow": "feature-development",
  "steps": [
    {"step": 1, "action": "research", "model": "o3"},
    {"step": 2, "action": "plan", "model": "gpt-5.1-codex"},
    {"step": 3, "action": "implement", "model": "gpt-5.1-codex"},
    {"step": 4, "action": "test", "model": "gpt-5.1-codex"},
    {"step": 5, "action": "document", "model": "gpt-5.1-codex-mini"}
  ]
}
EOF

# Execute workflow from JSON
for step in $(jq -r '.steps[] | @base64' workflow.json); do
  _jq() {
    echo "$step" | base64 --decode | jq -r "$1"
  }

  action=$(_jq '.action')
  model=$(_jq '.model')

  echo "Step: $action (using $model)"
  codex exec -m "$model" --dangerously-bypass-approvals-and-sandbox \
    "Execute $action step for current feature"
done
```

## Error Handling

### Pattern 1: Automatic Retry

```bash
#!/bin/bash
retry_codex() {
  local task="$1"
  local max_attempts=3
  local attempt=1

  while [ $attempt -le $max_attempts ]; do
    echo "Attempt $attempt of $max_attempts..."

    if codex exec --json --dangerously-bypass-approvals-and-sandbox "$task" \
      > result.json 2>error.log; then
      echo "✓ Success on attempt $attempt"
      return 0
    else
      echo "✗ Failed attempt $attempt"
      cat error.log

      if [ $attempt -lt $max_attempts ]; then
        echo "Retrying..."
        attempt=$((attempt + 1))
      fi
    fi
  done

  echo "✗ Failed after $max_attempts attempts"
  return 1
}

# Usage
retry_codex "Run tests and fix any failures"
```

### Pattern 2: Fallback Strategy

```bash
#!/bin/bash
# Try complex approach, fallback to simple

if ! codex exec -m o3 --dangerously-bypass-approvals-and-sandbox \
  "Optimize database queries using advanced techniques"; then

  echo "Complex optimization failed, trying simpler approach..."

  codex exec -m gpt-5.1-codex --dangerously-bypass-approvals-and-sandbox \
    "Add basic database indexes to improve performance"
fi
```

### Pattern 3: Error Analysis and Fix

```bash
#!/bin/bash
# Capture errors and let Codex analyze and fix

codex exec --dangerously-bypass-approvals-and-sandbox \
  "Run all tests" \
  > test-output.txt 2>&1

if grep -q "FAILED" test-output.txt; then
  echo "Tests failed, analyzing..."

  # Let Codex analyze failures
  codex exec -m o3 --dangerously-bypass-approvals-and-sandbox \
    "Analyze test failures in @test-output.txt:
    1. Identify root causes
    2. Fix all issues
    3. Run tests again
    4. Repeat until all pass"
fi
```

## Best Practices

### 1. Start with Planning

```bash
# Always start complex tasks with planning
codex exec -m o3 --json \
  "Analyze requirement and create detailed plan" \
  > plan.json

# Then execute plan
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Implement according to @plan.json"
```

### 2. Use Appropriate Models

```bash
# Research: o3 with web search
codex exec -m o3 --search "Research best approach"

# Implementation: GPT-5.1-Codex
codex exec -m gpt-5.1-codex "Implement feature"

# Simple tasks: GPT-5.1-Codex-Mini
codex exec -m gpt-5.1-codex-mini "Format code"
```

### 3. Always Verify

```bash
# After every significant change
codex exec --json --dangerously-bypass-approvals-and-sandbox \
  "Run tests and return results"
```

### 4. Atomic Changes

```bash
# Break large tasks into atomic steps
codex exec --dangerously-bypass-approvals-and-sandbox "Step 1: Add validation"
codex exec --dangerously-bypass-approvals-and-sandbox "Step 2: Add error handling"
codex exec --dangerously-bypass-approvals-and-sandbox "Step 3: Add tests"
```

### 5. Use Git for Safety

```bash
# Work on branches
git checkout -b feature/new-feature
codex exec --dangerously-bypass-approvals-and-sandbox "Build feature"

# Review changes
git diff

# Commit
codex exec --full-auto "Create semantic commits"
```

### 6. Document Everything

```bash
# Always generate documentation
codex exec --dangerously-bypass-approvals-and-sandbox \
  "Add comprehensive documentation to all new code"
```

### 7. Monitor Progress

```bash
#!/bin/bash
# Track progress with JSON reports
codex exec --json --dangerously-bypass-approvals-and-sandbox \
  "Report progress on current task:
  {
    'completed': [...],
    'in_progress': [...],
    'remaining': [...],
    'blockers': [...]
  }" \
  > progress.json
```

## Complete Example: Microservice Development

Building a complete microservice with Claude + Codex:

```bash
#!/bin/bash
# Complete microservice: User Profile Service

echo "Building User Profile Microservice..."

# 1. Architecture (o3 reasoning)
codex exec -m o3 --search --json \
  "Design microservice architecture for user profiles:
  - API design
  - Data model
  - Caching strategy
  - Security
  Return detailed architecture" \
  > architecture.json

# 2. Setup (GPT-5.1-Codex-Mini)
codex exec -m gpt-5.1-codex-mini --dangerously-bypass-approvals-and-sandbox \
  "Setup project structure per @architecture.json:
  - Initialize Node.js project
  - Install dependencies
  - Setup TypeScript
  - Configure ESLint/Prettier"

# 3. Database (GPT-5.1-Codex)
codex exec -m gpt-5.1-codex --dangerously-bypass-approvals-and-sandbox \
  "Implement database layer:
  - Create User model
  - Create Profile model
  - Add migrations
  - Setup connection pool"

# 4. API (GPT-5.1-Codex)
codex exec -m gpt-5.1-codex --dangerously-bypass-approvals-and-sandbox \
  "Implement REST API:
  - CRUD endpoints for profiles
  - Validation middleware
  - Error handling
  - OpenAPI documentation"

# 5. Caching (GPT-5.1-Codex)
codex exec -m gpt-5.1-codex --dangerously-bypass-approvals-and-sandbox \
  "Add Redis caching layer per @architecture.json"

# 6. Security (o3 analysis)
codex exec -m o3 --search --dangerously-bypass-approvals-and-sandbox \
  "Implement security:
  - JWT authentication
  - Rate limiting
  - Input sanitization
  - CORS configuration"

# 7. Tests (GPT-5.1-Codex)
codex exec -m gpt-5.1-codex --dangerously-bypass-approvals-and-sandbox \
  "Generate test suite with >90% coverage"

# 8. Docker (GPT-5.1-Codex-Mini)
codex exec -m gpt-5.1-codex-mini --dangerously-bypass-approvals-and-sandbox \
  "Create Docker setup:
  - Dockerfile with multi-stage build
  - docker-compose.yml
  - .dockerignore"

# 9. CI/CD (GPT-5.1-Codex)
codex exec -m gpt-5.1-codex --dangerously-bypass-approvals-and-sandbox \
  "Create GitHub Actions:
  - Test pipeline
  - Build and push Docker image
  - Deploy to staging"

# 10. Documentation (GPT-5.1-Codex)
codex exec -m gpt-5.1-codex --dangerously-bypass-approvals-and-sandbox \
  "Generate complete documentation:
  - API docs
  - Architecture diagram
  - Deployment guide
  - Development guide"

# 11. Verification (o3 final check)
codex exec -m o3 --json --dangerously-bypass-approvals-and-sandbox \
  "Final verification:
  - Run all tests
  - Check code quality
  - Verify security
  - Performance benchmarks
  Return complete report" \
  > final-report.json

echo "Microservice complete!"
cat final-report.json | jq .
```

---

**Result**: Complete production-ready microservice in ~30-45 minutes with 100% automation, Claude orchestrating strategic decisions, and Codex handling tactical implementation.
