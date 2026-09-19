---
name: save-knowledge
description: Automatically extract knowledge from conversation history and save it into the user's local knowledge base with indexed query hints.
metadata:
  short-description: Save conversation knowledge
---

# Save Knowledge

Automatically extract knowledge from conversation history and save to knowledge base.

**User provides**: 1-2 keywords
**Claude does**: Extract, summarize, save, and index

## Usage

```
/save-knowledge
```

## Workflow

### Step 1: Ask for Keywords

Use AskUserQuestion with ONE simple question:

```
"What knowledge topic do you want to save from this conversation?"
```

- Single text input field
- Examples: "俯视图坐标", "UWB融合", "坐标系映射"
- User provides 1-3 keywords

### Step 2: Search Conversation History

**Task**: Find relevant content from the conversation related to the keywords.

**Look for**:
- Code snippets you wrote
- Problems solved
- Error messages and fixes
- Design decisions
- Configuration examples
- Best practices discussed

### Step 3: Generate Knowledge Document

**Create a structured document** using this template:

```markdown
# {Knowledge Topic Title}

## 问题场景
{When/why is this knowledge needed?}

## 关键知识点

### 1. {Concept 1}
{Explanation}

### 2. {Concept 2}
{Explanation}

## 代码示例

\`\`\`{language}
{Code from conversation}
\`\`\`

**说明**: {What this code does}

## 常见错误

❌ **错误**: {Bad approach}
\`\`\`{language}
{Wrong code}
\`\`\`

✅ **正确**: {Correct approach}
\`\`\`{language}
{Right code}
\`\`\`

## 实际案例

**项目**: {Project name if mentioned}
**文件**: {File paths from conversation}
**实现**: {Brief implementation description}

## 总结

- {Key takeaway 1}
- {Key takeaway 2}
- {Key takeaway 3}
```

**Guidelines**:
- Write in Chinese (except code/technical terms)
- Focus on WHY, not just WHAT
- Include concrete examples from the conversation
- Keep it actionable and reusable
- 2-5 pages max

### Step 4: Generate Metadata

**Automatically create**:

1. **Filename**:
   - Convert topic to English/pinyin
   - Lowercase, underscores, `.md` extension
   - Examples:
     - "俯视图坐标" → `bev_coordinate_mapping.md`
     - "UWB融合" → `uwb_fusion_strategy.md`

2. **Query Keywords**:
   - Extract from topic + add English equivalents
   - Example: "俯视图坐标, BEV, coordinate mapping"

3. **Description**:
   - One-line summary
   - Example: "机器人坐标系与图像坐标系的转换方法"

### Step 5: Save to Knowledge Base

```bash
mkdir -p ~/.claude/knowledge
# Write generated content to ~/.claude/knowledge/{filename}
```

Use Write tool to create the file.

### Step 6: Update CLAUDE.md Index

1. Read `~/.claude/CLAUDE.md`

2. Check if `<!-- KNOWLEDGE_INDEX_START -->` exists

3. If not, append to end of file:
   ```markdown
   ---

   ## 知识库索引

   当遇到特定场景时，参考对应知识文档：

   <!-- KNOWLEDGE_INDEX_START -->
   <!-- KNOWLEDGE_INDEX_END -->
   ```

4. Add entry before `<!-- KNOWLEDGE_INDEX_END -->`:
   ```markdown
   - **{Topic}**：`/knowledge-query {keywords}` - {description}
   ```

Use Edit tool to update.

### Step 7: Output Summary

```
✅ Knowledge extracted and saved!

📄 File: ~/.claude/knowledge/{filename}
🔍 Query: /knowledge-query {primary_keyword}
📝 Summary: {description}

Content includes:
- {Key point 1}
- {Key point 2}
- {Key point 3}
```

## Example

```
User: /save-knowledge

Claude: What knowledge topic do you want to save from this conversation?

User: 俯视图坐标映射

Claude: [Scanning conversation...found BEV visualization, coordinate transforms, OpenCV code...]
        [Generating knowledge document...]

✅ Knowledge extracted and saved!

📄 File: ~/.claude/knowledge/bev_coordinate_mapping.md
🔍 Query: /knowledge-query 俯视图坐标
📝 Summary: 机器人坐标系与图像坐标系的转换方法

Content includes:
- 机器人坐标系 (X-前方, Y-左侧) 到图像坐标的映射
- 极坐标到笛卡尔坐标转换公式
- OpenCV坐标系注意事项与常见错误
```

## Implementation Notes

### Content Extraction

**High priority sources**:
- Your (Claude's) explanations
- Code you wrote or modified
- Solutions to problems
- Error messages and fixes

**What to include**:
- Working code examples
- Before/after comparisons
- Common mistakes identified
- Design rationale

**What to skip**:
- Generic information
- One-off fixes
- User's private details
- Redundant content

### Filename Mapping

Common Chinese → English abbreviations:
- 俯视图 → bev (Bird's Eye View)
- 超宽带 → uwb (Ultra-Wideband)
- 机器人操作系统 → ros
- 相机 → camera
- 坐标系 → coordinate
- 融合 → fusion
- 调试 → debugging

Use pinyin if no standard abbreviation exists.

### Error Handling

**If conversation has no relevant content**:
```
❌ I couldn't find enough information about "{keywords}" in our conversation.

Would you like to:
1. Try different keywords
2. Skip and save manually later
```

**If CLAUDE.md doesn't exist**:
- Create it with index section

**If filename exists**:
```
⚠️  File ~/.claude/knowledge/{filename} already exists.

Options:
1. Overwrite (replace existing content)
2. Merge (append to existing)
3. Skip
```

## Quality Checklist

Before saving, ensure the document has:
- ✅ Clear problem statement
- ✅ At least 2 code examples
- ✅ Common errors section
- ✅ Practical use case
- ✅ Concise summary

If missing critical sections, note gaps in the output.
