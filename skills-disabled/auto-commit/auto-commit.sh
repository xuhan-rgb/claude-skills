#!/bin/bash
# auto-commit - 自动整理、提交、推送 git 变更（带智能检测）
# 使用：auto-commit

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

# ==================== 检查暂存文件 ====================
echo -e "${BLUE}检查暂存文件...${NC}"
if ! git diff --cached --quiet; then
    echo -e "${GREEN}✅ 找到暂存变更${NC}"
else
    echo -e "${RED}❌ 错误：没有暂存的文件${NC}"
    echo ""
    echo "使用以下命令暂存文件："
    echo "  ${YELLOW}git add <文件>${NC}"
    echo "  ${YELLOW}git add .${NC}"
    echo ""
    echo "查看未暂存的变更："
    echo "  ${YELLOW}git status${NC}"
    exit 1
fi

# 显示暂存文件统计
echo ""
echo -e "${BLUE}暂存变更统计：${NC}"
git diff --cached --stat
echo ""

# ==================== 智能检测 ====================
CHANGED_FILES=$(git diff --cached --name-only)

# 检测潜在的不完善改动
echo -e "${BLUE}🔍 检测潜在问题...${NC}"
WARNINGS=()

# 1. 检测代码改动但配置/依赖没改
HAS_CODE_CHANGES=$(echo "$CHANGED_FILES" | grep -E '\.(py|js|ts|go|cpp|c|java|rs)$' || true)
HAS_CONFIG_CHANGES=$(echo "$CHANGED_FILES" | grep -E '(requirements\.txt|package\.json|\.env|\.yml|\.yaml|\.conf|\.config|Cargo\.toml|go\.mod)' || true)

if [ ! -z "$HAS_CODE_CHANGES" ] && [ -z "$HAS_CONFIG_CHANGES" ]; then
    # 检查工作目录中是否存在这些配置文件
    if [ -f "requirements.txt" ] || [ -f "package.json" ] || [ -f "Cargo.toml" ] || [ -f "go.mod" ]; then
        WARNINGS+=("⚠️  代码文件已修改，但依赖/配置文件未改动。请确认配置是否需要更新。")
    fi
fi

# 2. 检测配置改动但代码没改
if [ ! -z "$HAS_CONFIG_CHANGES" ] && [ -z "$HAS_CODE_CHANGES" ]; then
    WARNINGS+=("⚠️  配置/依赖文件已修改，但代码文件未改动。请确认是否需要更新代码。")
fi

# 3. 检测只改了文档（应该检查是否有文档对应的代码改动）
HAS_DOC_ONLY=$(echo "$CHANGED_FILES" | grep -E '\.(md|rst|txt)$|README|CHANGELOG|docs/' || true)
HAS_CODE=$(echo "$CHANGED_FILES" | grep -E '\.(py|js|ts|go|cpp|c|java|rs|sh)$' || true)

if [ ! -z "$HAS_DOC_ONLY" ] && [ -z "$HAS_CODE" ]; then
    WARNINGS+=("ℹ️  仅修改了文档/注释，没有代码改动。如有新功能实现，请检查是否需要添加代码。")
fi

# 4. 检测改动文件数量过多或过少
FILE_COUNT=$(echo "$CHANGED_FILES" | wc -l)
if [ $FILE_COUNT -eq 1 ]; then
    SINGLE_FILE=$(echo "$CHANGED_FILES" | head -1)
    # 如果只改了一个文件，提醒检查是否完整
    if [[ "$SINGLE_FILE" == *.py ]] || [[ "$SINGLE_FILE" == *.js ]] || [[ "$SINGLE_FILE" == *.ts ]]; then
        WARNINGS+=("⚠️  仅修改了 1 个源代码文件。请确认这是一个完整的改动。")
    fi
fi

# 5. 检测是否修改了特定项目关键文件而没改对应部分
if echo "$CHANGED_FILES" | grep -q "README.md"; then
    # 改了 README 但没改对应的代码或配置
    if ! echo "$CHANGED_FILES" | grep -qE '\.(py|js|ts|sh|yaml|yml|json)$|manager/|kitty-enhance/'; then
        WARNINGS+=("ℹ️  修改了 README，建议检查是否需要更新代码或配置。")
    fi
fi

# 显示警告信息
if [ ${#WARNINGS[@]} -gt 0 ]; then
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${YELLOW}⚠️  检测到潜在问题：${NC}"
    echo -e "${PURPLE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    for warning in "${WARNINGS[@]}"; do
        echo "  $warning"
    done
    echo ""
    read -p "继续提交？[y/n]: " continue_choice
    if [[ ! $continue_choice =~ ^[yY]$ ]]; then
        echo -e "${YELLOW}已取消。请检查并重新暂存文件。${NC}"
        exit 0
    fi
    echo ""
fi

# ==================== 生成 Commit Message ====================
echo -e "${BLUE}📝 生成 commit message...${NC}"

# 判断文件类型确定 prefix
PREFIX="chore"

if echo "$CHANGED_FILES" | grep -E '\.(md|txt|rst)$|README|CHANGELOG|COMMANDS' > /dev/null; then
    PREFIX="docs"
elif echo "$CHANGED_FILES" | grep -E '\.test\.|\.spec\.' > /dev/null; then
    PREFIX="test"
elif echo "$CHANGED_FILES" | grep -E '(src/|lib/)' > /dev/null; then
    PREFIX="feat"
fi

# 生成简要描述
SUMMARY=$(echo "$CHANGED_FILES" | head -3 | paste -sd',' - | sed 's/,/, /g')

# 默认 message
DEFAULT_MESSAGE="$PREFIX: update changes

- Updated: $SUMMARY"

# 显示生成的 message
echo ""
echo -e "${YELLOW}────────────────────────────────────────${NC}"
echo -e "${YELLOW}建议的 commit message:${NC}"
echo -e "${YELLOW}────────────────────────────────────────${NC}"
echo "$DEFAULT_MESSAGE"
echo -e "${YELLOW}────────────────────────────────────────${NC}"
echo ""

# ==================== 确认 Message ====================
read -p "使用此 message? [y/e/n] (y=使用, e=编辑, n=取消): " choice

case $choice in
    y|Y)
        COMMIT_MSG="$DEFAULT_MESSAGE"
        ;;
    e|E)
        # 使用编辑器编辑 message
        TEMP_FILE=$(mktemp)
        echo "$DEFAULT_MESSAGE" > "$TEMP_FILE"
        ${EDITOR:-nano} "$TEMP_FILE"
        COMMIT_MSG=$(cat "$TEMP_FILE")
        rm "$TEMP_FILE"
        ;;
    n|N)
        echo -e "${RED}已取消${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}无效选择，已取消${NC}"
        exit 1
        ;;
esac

# ==================== 执行 Commit ====================
echo ""
echo -e "${BLUE}⏳ 执行 commit...${NC}"
if git commit -m "$(printf '%s\n' "$COMMIT_MSG")

Co-Authored-By: Claude Haiku 4.5 <noreply@anthropic.com>"; then
    echo -e "${GREEN}✅ Commit 成功${NC}"
else
    echo -e "${RED}❌ Commit 失败${NC}"
    exit 1
fi

# ==================== 执行 Push ====================
CURRENT_BRANCH=$(git branch --show-current)
REMOTE=$(git config --get branch.$CURRENT_BRANCH.remote || echo "origin")

echo ""
echo -e "${BLUE}↑ 推送到 $REMOTE/$CURRENT_BRANCH...${NC}"

if git push $REMOTE $CURRENT_BRANCH 2>&1; then
    echo -e "${GREEN}✅ Push 成功${NC}"
    echo ""
    echo -e "${GREEN}🎉 完成！变更已推送到远程仓库${NC}"
else
    echo -e "${YELLOW}⚠️  Push 失败（可能需要 -u 参数）${NC}"
    echo "尝试使用："
    echo "  ${YELLOW}git push -u $REMOTE $CURRENT_BRANCH${NC}"
    exit 1
fi
