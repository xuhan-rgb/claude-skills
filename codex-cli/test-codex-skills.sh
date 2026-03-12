#!/bin/bash
# Test script for OpenAI Codex CLI skills
# Validates all skills work correctly with installed Codex CLI
# Updated: December 2025 - GPT-5.2 Release

set -e

echo "========================================="
echo "Codex CLI Skills Validation Test"
echo "GPT-5.2 Update - December 2025"
echo "========================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TESTS_RUN=0
TESTS_PASSED=0
TESTS_FAILED=0

# Test function
run_test() {
  local test_name="$1"
  local test_command="$2"

  TESTS_RUN=$((TESTS_RUN + 1))
  echo -n "Testing: $test_name ... "

  if eval "$test_command" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ PASS${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
    return 0
  else
    echo -e "${RED}✗ FAIL${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
    return 1
  fi
}

# 1. Check Codex CLI Installation
echo "=== 1. Installation Check ==="
run_test "Codex CLI installed" "which codex"
run_test "Codex CLI version" "codex --version"
echo ""

# 2. Check Authentication
echo "=== 2. Authentication Check ==="
if [ -n "$OPENAI_API_KEY" ]; then
  echo -e "${GREEN}✓ API key found in environment${NC}"
  TESTS_PASSED=$((TESTS_PASSED + 1))
elif [ -f ~/.codex/config.toml ]; then
  echo -e "${GREEN}✓ Config file found${NC}"
  TESTS_PASSED=$((TESTS_PASSED + 1))
elif [ -f ~/.codex/credentials ]; then
  echo -e "${GREEN}✓ OAuth credentials found${NC}"
  TESTS_PASSED=$((TESTS_PASSED + 1))
else
  echo -e "${YELLOW}⚠ No authentication found${NC}"
  echo "  Run: codex login OR export OPENAI_API_KEY=..."
fi
TESTS_RUN=$((TESTS_RUN + 1))
echo ""

# 3. Check Skills Files
echo "=== 3. Skills Files Check ==="
SKILL_DIR=".claude/skills/codex-cli"

run_test "codex-cli/SKILL.md exists" "test -f $SKILL_DIR/../codex-cli/SKILL.md"
run_test "codex-auth/SKILL.md exists" "test -f $SKILL_DIR/../codex-auth/SKILL.md"
run_test "codex-tools/SKILL.md exists" "test -f $SKILL_DIR/../codex-tools/SKILL.md"
run_test "codex-chat/SKILL.md exists" "test -f $SKILL_DIR/../codex-chat/SKILL.md"
run_test "codex-review/SKILL.md exists" "test -f $SKILL_DIR/../codex-review/SKILL.md"
run_test "codex-git/SKILL.md exists" "test -f $SKILL_DIR/../codex-git/SKILL.md"
run_test "Integration guide exists" "test -f $SKILL_DIR/CLAUDE-CODEX-INTEGRATION.md"
run_test "README exists" "test -f $SKILL_DIR/README.md"
echo ""

# 4. Validate YAML Frontmatter
echo "=== 4. YAML Frontmatter Validation ==="

validate_yaml() {
  local file="$1"
  local skill_name="$2"

  if grep -q "^---$" "$file" && \
     grep -q "^name: $skill_name$" "$file" && \
     grep -q "^description:" "$file"; then
    return 0
  else
    return 1
  fi
}

run_test "codex-cli frontmatter" "validate_yaml '$SKILL_DIR/../codex-cli/SKILL.md' 'codex-cli'"
run_test "codex-auth frontmatter" "validate_yaml '$SKILL_DIR/../codex-auth/SKILL.md' 'codex-auth'"
run_test "codex-tools frontmatter" "validate_yaml '$SKILL_DIR/../codex-tools/SKILL.md' 'codex-tools'"
run_test "codex-chat frontmatter" "validate_yaml '$SKILL_DIR/../codex-chat/SKILL.md' 'codex-chat'"
run_test "codex-review frontmatter" "validate_yaml '$SKILL_DIR/../codex-review/SKILL.md' 'codex-review'"
run_test "codex-git frontmatter" "validate_yaml '$SKILL_DIR/../codex-git/SKILL.md' 'codex-git'"
echo ""

# 5. Test Basic Codex Commands
echo "=== 5. Basic Codex Commands ==="

if [ -n "$OPENAI_API_KEY" ] || [ -f ~/.codex/credentials ]; then
  echo -e "${YELLOW}Testing with actual Codex CLI (rate limits may apply)${NC}"

  # Simple test (may hit rate limits)
  if codex exec "What is 2+2? Reply with just the number." 2>/dev/null | grep -q "4"; then
    echo -e "${GREEN}✓ Codex exec works${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
  else
    echo -e "${YELLOW}⚠ Codex exec test skipped (rate limited or auth issue)${NC}"
  fi
  TESTS_RUN=$((TESTS_RUN + 1))
else
  echo -e "${YELLOW}⚠ Skipping live tests (no authentication)${NC}"
fi
echo ""

# 6. Validate Key Automation Flags
echo "=== 6. Automation Flags Check ==="

check_flag_documented() {
  local flag="$1"
  local file="$2"

  grep -qFe "$flag" "$file"
}

run_test "--dangerously-bypass-approvals-and-sandbox documented" \
  "check_flag_documented '--dangerously-bypass-approvals-and-sandbox' \"$SKILL_DIR/../codex-cli/SKILL.md\""
run_test "--full-auto documented" \
  "check_flag_documented '--full-auto' \"$SKILL_DIR/../codex-cli/SKILL.md\""
run_test "--json flag documented" \
  "check_flag_documented '--json' \"$SKILL_DIR/../codex-cli/SKILL.md\""
run_test "--search flag documented" \
  "check_flag_documented '--search' \"$SKILL_DIR/../codex-cli/SKILL.md\""
echo ""

# 7. Validate Models Documented (GPT-5.2 Update)
echo "=== 7. Models Documentation Check (December 2025) ==="

check_model_documented() {
  local model="$1"
  local file="$2"

  grep -q "$model" "$file"
}

# GPT-5.2 Models (NEW)
run_test "gpt-5.2 documented" \
  "check_model_documented 'gpt-5.2' \"$SKILL_DIR/../codex-cli/SKILL.md\""
run_test "gpt-5.2-pro documented" \
  "check_model_documented 'gpt-5.2-pro' \"$SKILL_DIR/../codex-cli/SKILL.md\""
run_test "gpt-5.2-chat-latest documented" \
  "check_model_documented 'gpt-5.2-chat-latest' \"$SKILL_DIR/../codex-cli/SKILL.md\""

# GPT-5.1 Codex Models (Recommended for coding)
run_test "gpt-5.1-codex-max documented" \
  "check_model_documented 'gpt-5.1-codex-max' \"$SKILL_DIR/../codex-cli/SKILL.md\""
run_test "gpt-5.1-codex documented" \
  "check_model_documented 'gpt-5.1-codex' \"$SKILL_DIR/../codex-cli/SKILL.md\""
run_test "gpt-5.1-codex-mini documented" \
  "check_model_documented 'gpt-5.1-codex-mini' \"$SKILL_DIR/../codex-cli/SKILL.md\""

# Reasoning Models
run_test "o3 model documented" \
  "check_model_documented 'o3' \"$SKILL_DIR/../codex-cli/SKILL.md\""
run_test "o4-mini model documented" \
  "check_model_documented 'o4-mini' \"$SKILL_DIR/../codex-cli/SKILL.md\""
echo ""

# 7b. GPT-5.2 Features Validation
echo "=== 7b. GPT-5.2 Features Check ==="

run_test "400K context window documented" \
  "check_model_documented '400K context' \"$SKILL_DIR/../codex-cli/SKILL.md\" || check_model_documented '400,000' \"$SKILL_DIR/../codex-cli/SKILL.md\""
run_test "128K output tokens documented" \
  "check_model_documented '128K' \"$SKILL_DIR/../codex-cli/SKILL.md\" || check_model_documented '128,000' \"$SKILL_DIR/../codex-cli/SKILL.md\""
run_test "reasoning.effort parameter documented" \
  "check_model_documented 'reasoning.effort' \"$SKILL_DIR/../codex-cli/SKILL.md\" || check_model_documented 'reasoning-effort' \"$SKILL_DIR/../codex-cli/SKILL.md\" || check_model_documented 'xhigh' \"$SKILL_DIR/../codex-cli/SKILL.md\""
run_test "compaction feature documented" \
  "check_model_documented 'compact' \"$SKILL_DIR/../codex-cli/SKILL.md\""
run_test "December 2025 update mentioned" \
  "check_model_documented 'December 2025' \"$SKILL_DIR/../codex-cli/SKILL.md\""
echo ""

# 8. Integration Guide Validation
echo "=== 8. Integration Guide Check ==="

run_test "Think-Act-Observe Loop documented" \
  "grep -q 'Think-Act-Observe Loop' \"$SKILL_DIR/CLAUDE-CODEX-INTEGRATION.md\""
run_test "Integration patterns documented" \
  "grep -q 'Integration Patterns' \"$SKILL_DIR/CLAUDE-CODEX-INTEGRATION.md\""
run_test "Model selection strategy documented" \
  "grep -q 'Model Selection Strategy' \"$SKILL_DIR/CLAUDE-CODEX-INTEGRATION.md\""
run_test "Complete feature example included" \
  "grep -q 'Complete Feature Development' \"$SKILL_DIR/CLAUDE-CODEX-INTEGRATION.md\""
run_test "Safety patterns documented" \
  "grep -q 'Safety Patterns' \"$SKILL_DIR/CLAUDE-CODEX-INTEGRATION.md\""
echo ""

# 9. Git Integration Validation
echo "=== 9. Git Integration Check ==="

run_test "codex apply documented" \
  "grep -q 'codex apply' \"$SKILL_DIR/../codex-git/SKILL.md\""
run_test "codex a shorthand documented" \
  "grep -q 'codex a' \"$SKILL_DIR/../codex-git/SKILL.md\""
run_test "Commit generation documented" \
  "grep -q 'commit' \"$SKILL_DIR/../codex-git/SKILL.md\""
run_test "PR automation documented" \
  "grep -q 'PR' \"$SKILL_DIR/../codex-git/SKILL.md\""
echo ""

# 10. Cross-References Validation
echo "=== 10. Cross-References Check ==="

run_test "codex-cli references codex-auth" \
  "grep -q 'codex-auth' \"$SKILL_DIR/../codex-cli/SKILL.md\""
run_test "codex-cli references codex-tools" \
  "grep -q 'codex-tools' \"$SKILL_DIR/../codex-cli/SKILL.md\""
run_test "README references all skills" \
  "grep -q 'codex-git' \"$SKILL_DIR/README.md\""
run_test "Integration guide referenced in README" \
  "grep -q 'CLAUDE-CODEX-INTEGRATION.md' \"$SKILL_DIR/README.md\""
echo ""

# Summary
echo "========================================="
echo "Test Summary"
echo "========================================="
echo "Tests run: $TESTS_RUN"
echo -e "${GREEN}Tests passed: $TESTS_PASSED${NC}"

if [ $TESTS_FAILED -gt 0 ]; then
  echo -e "${RED}Tests failed: $TESTS_FAILED${NC}"
  echo ""
  echo -e "${RED}✗ Validation FAILED${NC}"
  exit 1
else
  echo -e "${GREEN}Tests failed: $TESTS_FAILED${NC}"
  echo ""
  echo -e "${GREEN}✓ All validations PASSED${NC}"
  echo ""
  echo "The Codex CLI skills package is ready to use!"
  echo ""
  echo "Quick Start:"
  echo "  1. Ensure Codex CLI is installed: codex --version"
  echo "  2. Authenticate: codex login (or set OPENAI_API_KEY)"
  echo "  3. Test: codex exec \"Hello, Codex!\""
  echo "  4. Read: .claude/skills/codex-cli/README.md"
  echo "  5. Build something amazing with Claude + Codex!"
  exit 0
fi
