---
name: cmd-flow-viz
description: Use when user wants a structured semantic analysis report of one or more commands - explaining the program's purpose, inputs/outputs, computational logic, and (for ML training scripts) tech stack including backbone/heads/losses/augmentation. Triggers include "/cmd-flow", "可视化命令流程", "分析这个命令", "画一下这个命令", "trace command flow". For wrapper scripts (bash calling python), recursively analyze the underlying program. Output is a single self-contained interactive HTML report with cards + Mermaid diagrams.
---

# Command Flow Visualizer

对一个或多个可执行命令做**语义级分析**，输出**结构化分析报告 HTML**。重点是数据流（tensor shape 演化）+ 技术栈，不是逐行翻译。

## 触发条件

- `/cmd-flow <cmd1> [cmd2] ...`
- "分析一下 xxx 命令"
- "画一下 xxx 的流程"
- "可视化命令流程"
- "trace command flow for xxx"

## 核心理念

**不要做的事**：
- ❌ 把每个 `cv2.imread` / `if/else` 都画成节点
- ❌ 把节点数搞到 40+
- ❌ 只看表面命令名就生成流程图（wrapper 脚本要追到真实程序）
- ❌ **找不到源码就编内容**（必须诚实报错）
- ❌ 手写 Mermaid 字符串拼接（用 `generate_report.py` 助手）

**要做的事**：
- ✅ **理解程序本质**：解决什么问题？吃什么？吐什么？
- ✅ **数据流为主线**：标注每个 tensor 的 shape 演化
- ✅ **5-15 个有意义的节点**，宁可少不可乱
- ✅ **追溯 wrapper**：bash → python 时，深入读 python 源码

## 工作流程

```
1. 读源码：
   - bash wrapper → 解析出真正的 python 入口 → 读 python
   - 训练脚本 → 同时读 dataset/sampler/trainer 相关代码
   - 推理脚本 → 同时读 model/preprocessing 相关代码
   - 找不到 → 立即停下，告诉用户原因

2. 提取结构化信息（在脑里整理为 ReportData）

3. 调用 generate_report.py 助手生成 HTML
   import sys
   sys.path.insert(0, "~/.claude/skills/cmd-flow-viz")
   from generate_report import ReportData, TechCard, generate_report, make_filename

   data = ReportData(...)
   path = generate_report(data, make_filename("xxx.sh"))

4. 返回路径给用户
```

## 必须使用 generate_report.py

**不要手写字符串拼接 HTML**。`generate_report.py` 提供：
- `safe_label()`：自动转义 Mermaid 危险字符（括号、斜杠、方括号等）
- `safe_node_id()`：合法化节点 ID
- `render_flowchart()`：从 (nodes, edges, subgraphs) 生成 Mermaid
- `generate_report(data, path)`：从 `ReportData` 一键生成 HTML

### 使用示例

```python
import sys
sys.path.insert(0, "/home/qwer/.claude/skills/cmd-flow-viz")
from generate_report import ReportData, TechCard, generate_report, make_filename

data = ReportData(
    title="train_xxx.sh",
    metadata_lines=[
        'Source: <span class="mono">/path/to/script.sh</span>',
        'Type: Bash → Python ML training',
        'Real entry: <span class="mono">src/main.py</span>',
    ],
    purpose="训练 XXX 模型，使用 ResNet-18 backbone + ...",
    inputs=[
        '<span class="label">Dataset:</span> <code>data/xxx/</code> 800 张图',
        '<span class="label">Hyperparams:</span> <code>--lr 1e-4 --bs 8</code>',
    ],
    outputs=[
        '<span class="label">Best:</span> <code>exp/.../model_best.pth</code>',
        '<span class="label">Logs:</span> TensorBoard',
    ],
    tech_cards=[
        TechCard("Backbone", "🧱", {
            "arch": "<code>res_18</code>",
            "预训练": "ImageNet",
            "下采样": "×32",
        }),
        TechCard("Heads", "🎯", {
            "line_hm": "<code>1ch</code> 线条热力图",
            "ep_hm": "<code>2ch</code> 端点",
        }),
        # ... more cards
    ],
    logic_nodes=[
        ("Img", "原图<br/>(1080, 1920, 3)"),
        ("Aug", "数据增强<br/>仿射 + 翻转"),
        ("Tensor", "(B, 3, 320, 640)"),
        ("BB", "Backbone ResNet-18"),
        ("FM", "(B, 256, 80, 160)"),
        ("H1", "Head line_hm"),
        ("Loss", "FocalLoss × 2"),
    ],
    logic_edges=[
        ("Img", "Aug", None),
        ("Aug", "Tensor", None),
        ("Tensor", "BB", None),
        ("BB", "FM", None),
        ("FM", "H1", None),
        ("H1", "Loss", None),
    ],
    logic_subgraphs={
        "数据准备": ["Img", "Aug", "Tensor"],
        "前向传播": ["BB", "FM", "H1"],
    },
    logic_direction="TD",
)

path = generate_report(data, make_filename("train_xxx.sh"))
print(f"Saved: {path}")
```

## 自适应输出结构

| 区块                       | 何时启用                 |
|----------------------------|--------------------------|
| **程序目的** Purpose       | 总是                     |
| **输入/输出** I/O          | 总是                     |
| **💡 关键洞察** Key Insights | 总是（最重要的章节！） |
| **技术栈** Tech Stack      | ML 训练/推理 / 数据 ETL  |
| **计算逻辑** Logic         | 总是（5-15 节点）        |
| **Topic 通信图**           | 多命令 + 有 IPC 时       |
| **状态机**                 | 代码里有明确状态切换时   |

空区块通过 `*_hide` 自动隐藏，不需要手动处理。

## 💡 Key Insights —— 最重要的章节

**这是整个报告的灵魂**。Claude 必须首先思考：

> 这个程序里，哪 1-3 个知识点是「不看就完全没法理解」的？

然后把这些做成 KeyInsight 卡片，**放在显眼位置**（粉色高亮）。**不要只列代码事实，要解释 WHY**。

### 各类程序的"关键洞察候选"

| 程序类型     | 通常最重要的 1-3 个点                                       |
|--------------|-------------------------------------------------------------|
| **ML 训练**  | ① **GT/标签生成策略**（最常被忽视的"秘密武器"）<br/>② **损失函数设计**（包含权重、技巧、数学公式）<br/>③ 模型架构创新点（如有） |
| **ML 推理**  | ① 后处理坐标变换链<br/>② 阈值/解码策略<br/>③ 训练-推理预处理是否一致 |
| **跟踪算法** | ① **数据关联策略**（如何在帧间匹配 ID）<br/>② **跟踪生命周期**（init/update/lost/removed）<br/>③ 状态估计方法（Kalman / IoU / ReID） |
| **SLAM**     | ① 前后端拆分<br/>② 优化策略（BA / Pose Graph）<br/>③ 闭环检测 |
| **数据 ETL** | ① 数据清洗规则<br/>② schema 转换的关键映射<br/>③ 边缘情况处理 |
| **C++ 算法** | ① **整体算法框架**（用图说明）<br/>② 核心数据结构<br/>③ 关键参数对算法行为的影响 |
| **ROS 节点** | ① 关键 callback 的处理逻辑<br/>② 跨节点同步机制<br/>③ TF 坐标系转换 |

### 必须挖掘的事

- **WHY**：为什么这样设计？解决什么具体问题？
- **HOW**：算法/数据流的核心步骤是什么？
- **TRAP**：有什么"隐式约定"或"容易踩的坑"？
- **VISUAL**：能不能生成一张图来说明？

### KeyInsight body_html 支持的元素

- `<p>`、`<ul>`、`<ol>`：普通文本和列表
- `<code>`：行内代码
- `<pre><code>...</code></pre>`：代码块
- `<div class="formula">...</div>`：公式高亮框
- `<img>`：用 `img_tag(path)` 嵌入本地图片（自动转 base64）
- `img_row([(path1, caption1), (path2, caption2), ...])`：横排图片+说明

### 鼓励生成可视化图片

好报告 = 真实数据 + 可视化。**主动写临时 Python 脚本跑一张真实图片** 然后嵌入，远比只有文字说明更有说服力。

### 标准工作流：生成可视化图片

```python
# Step 1: 在 /tmp 下写一段 Python 临时跑真实数据
#         复用项目的现有函数（sampler / 后处理 / 模型推理）
# Step 2: 用 cv2.imwrite 保存为 /tmp/xxx_N.jpg
# Step 3: 在 KeyInsight 里用 img_row() 嵌入
```

### ML 训练脚本：GT 可视化（3 步）

```python
# 用真实一张图片复刻 sampler 里的 GT 生成步骤
from utils.image import draw_umich_gaussian, get_affine_transform, ...
img = cv2.imread(real_path)
# ... 按 sampler 相同的逻辑画 heatmap ...
cv2.imwrite('/tmp/insight_gt.jpg', cv2.applyColorMap(hm*255, cv2.COLORMAP_JET))
```

然后嵌入：
```python
body_html = f'''
{img_row([
    ("/tmp/insight_1_original.jpg", "原图 + GT 标注"),
    ("/tmp/insight_2_line_hm.jpg", "GT line_hm heatmap"),
    ("/tmp/insight_3_ep_hm.jpg", "GT ep_hm heatmap"),
])}
'''
```

### ML 推理脚本：后处理中间结果可视化（4 步）

对于有复杂后处理的推理脚本（如 Dijkstra 轨迹提取、NMS、坐标变换），**主动跑一次真实模型并可视化中间 tensor**：

```python
# Step 1: 加载真实模型 + 真实图片
model = create_model(...); model.cuda().eval()
with torch.no_grad():
    out = model(preprocessed_tensor)
    line_hm = out['line_hm'].sigmoid().cpu().numpy()[0, 0]

# Step 2: 复现后处理的关键中间态
cost = build_cost_map(line_hm)       # 代价图
path = dijkstra_path(cost, start, end)  # 原始路径
resampled = resample_polyline(path, 20) # 重采样

# Step 3: 每个中间态保存一张图
cv2.imwrite('/tmp/step1_linehm.jpg', cv2.applyColorMap(...))
cv2.imwrite('/tmp/step2_costmap.jpg', cv2.applyColorMap(...))
cv2.imwrite('/tmp/step3_path.jpg', ...)    # 路径叠加在 cost map 上
cv2.imwrite('/tmp/step4_resampled.jpg', ...) # 20 个点叠加在 heatmap 上

# Step 4: 嵌入 KeyInsight
body_html = f"""
{img_row([('/tmp/step1_linehm.jpg', '① 模型 line_hm 输出'),
          ('/tmp/step2_costmap.jpg', '② 代价图')])}
{img_row([('/tmp/step3_path.jpg', '③ Dijkstra 路径'),
          ('/tmp/step4_resampled.jpg', '④ 20 点重采样')])}
"""
```

**关键**：把后处理的**每一步中间结果**都画成图，让读者一眼看到算法是怎么"从混乱的 heatmap 走到清晰的折线"的。这比任何文字描述都清楚。

### C++ 算法

可以用 mermaid 在 KeyInsight 里画**算法核心步骤的流程图**，或者把关键数据结构画成 mermaid class diagram。

### KeyInsight 数量

- **最多 3-4 个**，宁缺毋滥
- 每个 insight 应该是「一个完整的故事」，不是零碎事实
- 顺序：最有"启发性"的放第一

## 如何抽象数据流（关键）

**ML 训练脚本** 的 logic 应该按四段抽象：

```
1. 数据准备 (subgraph)
   - 原图 shape
   - 标签结构
   - 数据增强
   - 输出 tensor shape

2. 前向传播 (subgraph)
   - Backbone 特征
   - Neck 上采样
   - 各 head 分支输出 (并行)

3. 损失计算 (subgraph)
   - GT 生成（dataset 里）
   - sigmoid + Loss
   - 多 loss 合并

4. 优化更新 (subgraph)
   - backward + optimizer step
   - LR schedule
   - checkpoint 保存
```

**ML 推理脚本** 的 logic 应该按三段抽象：

```
1. 预处理 (subgraph): 原图 → tensor
2. 推理 (subgraph): tensor → 各 head 输出
3. 后处理 (subgraph): 输出 → 坐标 → 可视化文件
```

**关键原则**：每个节点要写 **tensor shape**（如 `(B, 256, 80, 160)`），让用户一眼看到维度演化。

## 各类脚本的提取重点

### ML 训练脚本

**Tech Stack 至少 6 张卡片**：
1. **Backbone**: 架构名 / 预训练 / 下采样比例 / 参数量
2. **Neck**: 结构 / 通道演化 / 上采样比例
3. **Heads**: 每个 head 的名字 / 通道 / 含义 / 中间结构
4. **Loss**: 各 head 用什么 loss / 权重 / 总公式
5. **GT 生成**: 标签如何转 heatmap（如果有）
6. **Augmentation**: 仿射 / 翻转 / 颜色 / 归一化
7. **Optimizer**: 类型 / lr / scheduler / wd
8. **Training**: epochs / bs / GPU / AMP / val 频率 / checkpoint

### ML 推理 / 可视化脚本

1. **Model**: arch / heads / device / no_grad
2. **Preprocessing**: resize / crop / pad / normalize
3. **Postprocessing**: sigmoid / argmax / 坐标变换
4. **Visualization**: 绘制方式 / 输出格式

### 数据处理脚本

1. **Source**: 输入路径 / 格式 / 数量
2. **Transform**: 关键步骤
3. **Output**: 输出路径 / schema / 数量

### ROS 节点

1. **Node**: 节点名
2. **Publishers**: 每个 topic 名 + 类型
3. **Subscribers**: 每个 topic 名 + 类型 + callback
4. **Services / Actions**: 服务名 + 类型
5. **Parameters**: 关键参数

## Wrapper 脚本递归分析

如果命令是 `.sh` 且主要是调用别的程序：

```bash
#!/bin/bash
python src/main.py train --dataset xxx --arch yyy
```

**必须**：
1. 提取真正的入口（`src/main.py`）
2. **读取该 python 文件**做完整分析
3. shell 里的关键参数列入 Inputs
4. **不要**把 `cd "$(dirname "$0")"` 这种写进流程图

## 找不到源码时

**直接报错，不要瞎编**：

```
我无法找到 <cmd> 的源码：
- which <cmd>: 未找到
- 在 PATH 和当前目录都没有匹配
请提供源码路径或确认命令名。
```

## 输出文件

- 文件名：`cmd_flow_<sanitized_cmd_name>_<YYYYMMDD_HHMMSS>.html`
- 路径：当前 `pwd`（除非用户指定）
- 用 `make_filename()` 生成

## 报告完成后告诉用户

1. HTML 文件路径
2. 打开方式：`xdg-open <path>`
3. 简要总结：1 句话目的 + 节点数 + 卡片数

## Mermaid 语法陷阱（generate_report.py 已自动处理）

`safe_label()` 自动替换危险字符：
- `()` → 空格
- `[]` → 中文方括号
- `/` → 全角斜杠 `／`
- `"` `` ` `` → 单引号
- `|` → 全角竖线 `｜`
- 保留 `<br/>`

`safe_node_id()` 自动确保节点 ID 只含 `A-Za-z0-9_`。

**所以 Claude 可以放心传任意原文进去**，不需要手动转义。
