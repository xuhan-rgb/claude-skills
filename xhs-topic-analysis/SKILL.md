---
name: xhs-topic-analysis
description: Use when user says "小红书分析", "分析小红书", "/xhs", "搜小红书", "红书话题", or wants to search Xiaohongshu by keyword and get a multi-angle analysis combining text, images, and comments. Also use when user provides an existing CSV/JSON file path for analysis.
---

# 小红书话题深度分析

两种使用模式：自动爬取+分析，或直接分析已有数据。

## 判断使用模式

根据用户输入判断：

- `/xhs 扫地机器人` → **模式 A**：先爬取，再分析
- `/xhs xiaohongshu_dumps/xhs_xxx.csv` → **模式 B**：直接分析已有文件
- `/xhs` + 用户提供文件路径 → **模式 B**

**判断规则**：参数包含 `/` 或以 `.csv`、`.json` 结尾 → 模式 B，否则 → 模式 A。

---

## 模式 A：爬取 + 分析

### 第 1 步：爬取数据

```bash
source ~/anaconda3/bin/activate && conda activate py310 && \
python /mnt/data/dev-scripts/tools/xiaohongshu/search_topic.py "<关键词>" \
  --max-notes 10
```

输出：
- CSV: `xiaohongshu_dumps/xhs_<关键词>_<时间戳>.csv`
- JSON: 同名 `.json`
- 图片: `xiaohongshu_dumps/images/<note_id>/`

选项：`--login` 重新扫码 | `--no-images` 不下载图片 | `--max-notes N` 笔记数

爬取完成后，自动进入第 2 步。

---

## 模式 B：直接分析已有文件

用户提供 CSV 或 JSON 文件路径，跳过爬取，直接进入第 2 步。

---

## 第 2 步：读取数据

1. **读 CSV/JSON**：用 Read 工具读取文件，解析笔记分隔行、正文行、评论行
2. **读图片**：CSV 分隔行中有图片目录路径（如 `图片(5张): xiaohongshu_dumps/images/abc123`），用 Glob 列出目录下所有图片，然后用 Read 逐张读取（Read 支持图片）
3. **关联图文**：将图片与对应笔记的正文、评论对应起来

## 第 3 步：多角度分析

根据话题类型自动选择分析框架：

#### A. 产品/消费类（如"扫地机器人"、"防晒霜"）

| 分析维度   | 数据来源                       |
|----------|------------------------------|
| 用户真实评价 | 评论文本 + 点赞数排序（高赞 = 共鸣） |
| 产品优缺点 | 正文提及的功能点 + 评论中的吐槽/夸赞   |
| 图片佐证   | 产品实拍图、使用效果图、对比图        |
| 购买建议   | 综合价格区间、适用场景、替代方案       |

#### B. 教程/技术类（如"claude使用技巧"、"Python入门"）

| 分析维度   | 数据来源                       |
|----------|------------------------------|
| 方法汇总   | 各笔记提出的不同方案              |
| 可行性判断 | 评论中的实践反馈（"试了有用"/"不行"） |
| 图片教程   | 步骤截图、配置界面、效果对比图        |
| 最佳实践   | 高赞笔记 + 高赞评论的共识          |

#### C. 决策/对比类（如"考研还是工作"、"iPhone vs 安卓"）

| 分析维度   | 数据来源                       |
|----------|------------------------------|
| 正反观点   | 按立场归类笔记和评论              |
| 论据强度   | 点赞数 + 评论互动量衡量认可度       |
| 图片证据   | 数据截图、对比图表、亲身经历图       |
| 综合建议   | 适用人群分类 + 条件式推荐          |

#### D. 经验/攻略类（如"日本旅游"、"装修避坑"）

| 分析维度   | 数据来源                       |
|----------|------------------------------|
| 经验提炼   | 多篇笔记的共同建议               |
| 避坑要点   | 评论中的踩坑反馈                 |
| 图片参考   | 实地照片、效果图、清单图           |
| 行动清单   | 按时间线/优先级整理可执行步骤       |

## 第 4 步：输出格式

输出格式可以是 Markdown（终端展示）或 PDF（正式报告）。

### Markdown 格式（终端展示）

```markdown
# 「<关键词>」小红书话题分析

## 数据概况
- 分析笔记数：X 篇，总评论：Y 条
- 数据时间：爬取日期

## 核心发现
（3-5 条最重要的结论，每条附图片引用）

## 详细分析
（按上面选定的框架展开）

## 高赞观点 TOP5
（点赞最高的评论原文 + 出处笔记）

## 争议与分歧
（评论中意见不一致的地方）

## 总结建议
（针对用户可能的使用场景给出建议）
```

### PDF 报告（正式报告）

分析完成后，生成一份包含图文混排的 PDF 报告：

```python
from tools.xiaohongshu.report_pdf import AnalysisReport

report = AnalysisReport(f"「{关键词}」小红书话题分析")

# 添加标题
report.h1("核心发现")
report.text_block("...")

# 添加图片（自动支持 webp）
report.image_block("图片路径/xxx.webp", caption="图1：xxx")

# 添加表格
report.table(
    headers=["维度", "结论"],
    rows=[["价格", "偏贵"], ["体验", "流畅"]]
)

# 添加引用（高赞评论）
report.quote("评论原文", "—— 用户名")

# 保存 PDF
report.save("xiaohongshu_dumps/analysis_report.pdf")
```

PDF 特性：
- 中文完整支持（使用 Pillow 渲染）
- 图片自动嵌入（支持 webp/jpg/png）
- 表格、引用、高亮框等排版元素
- 自动封面 + 页码

## 分析要点

- **图片不是装饰**：每个核心结论都应尝试关联图片作为佐证
- **点赞 = 权重**：高赞评论代表更多人的真实想法，分析时优先参考
- **主评论 vs 回复**：主评论是独立观点，回复是讨论深度，两者分开看
- **多篇交叉验证**：单篇笔记的观点可能有偏，多篇一致才是可靠结论
