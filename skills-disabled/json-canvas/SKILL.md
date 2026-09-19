---
name: json-canvas
description: Create and edit JSON Canvas files (.canvas) with nodes, edges, groups, and connections. Use when working with .canvas files, creating visual canvases, mind maps, flowcharts, or when the user mentions Canvas files in Obsidian.
---

# JSON Canvas Skill

This skill enables skills-compatible agents to create and edit valid JSON Canvas files (`.canvas`) used in Obsidian and other applications.

## Overview

JSON Canvas is an open file format for infinite canvas data. Canvas files use the `.canvas` extension and contain valid JSON following the [JSON Canvas Spec 1.0](https://jsoncanvas.org/spec/1.0/).


## UI Review Canvas Convention

Use this convention when users want app/web UI visualization, SVG annotation, page-flow explanation, or iterative tuning in one canvas.

### Build a Hybrid Review Board

- Place page previews as `file` nodes (`.svg` preferred).
- Place editable review notes as `text` nodes beside each page.
- Keep one page and one note card as a pair to support quick iteration.
- Use a top summary card for navigation/tab explanation and a bottom card for iteration status.

### Prefer Vertical Layout for Multi-Page Flows

- Stack page previews top-to-bottom when there are many pages.
- Align note cards in the same vertical order as page previews.
- Reserve a dedicated area for code/API mapping cards if the user requests implementation linkage.

### Mode for dev-plan Frontend Only: SVG Background + Overlay Controls

- Do not use this mode by default; use it when `dev-plan` 前端设计明确要求“可拖拽控件驱动代码变更”.
- Keep each page preview as one `file` node (`.svg`) for visual reference only.
- Add draggable `text` nodes on top of SVG for interactive controls (`Tab`, button, entry point).
- Use control node text as the source of truth; avoid relying on SVG internal edits for comments.
- Keep SVG node earlier in `nodes[]` (lower z-index) and overlay nodes later (upper z-index).

Control node template:

```text
控件：数据目录 Tab
点击：切换到 /data-dirs
打开：B 页面（数据目录列表）
作用：统一管理可复用目录
```

Flow edge template:

- `A页面控件节点 -> B页面Group` with `label: 点击 Tab/按钮`
- For dense UIs, annotate only page-switch triggers first, then add detail cards as needed.

### Explain Tabs with Priority Levels

- Add a tab summary card with priority levels: `P0` / `P1` / `P2`.
- Use stronger style for higher priority (e.g., color + font weight).
- Include route and trigger action for each tab.
- Keep an extensible template for future tabs.

### Obsidian Path Rules (Critical)

- Prefer vault-readable relative paths in `file` nodes.
- Avoid absolute filesystem paths in `file` nodes when using Obsidian/canvas-edit.
- If canvas is opened via soft link, copy SVG assets into vault path (commonly `_canvas/`) and reference by basename or vault-relative path.
- Verify links by checking all `file` nodes resolve before finalizing.

### Iteration Policy

- Keep note cards structured: `current version`, `issues`, `changes`, `status`.
- Update only high-priority issues per round.
- Preserve old flow edges unless the user asks to change navigation logic.


## File Structure

A canvas file contains two top-level arrays:

```json
{
  "nodes": [],
  "edges": []
}
```

- `nodes` (optional): Array of node objects
- `edges` (optional): Array of edge objects connecting nodes

## Nodes

Nodes are objects placed on the canvas. There are four node types:
- `text` - Text content with Markdown
- `file` - Reference to files/attachments
- `link` - External URL
- `group` - Visual container for other nodes

### Z-Index Ordering

Nodes are ordered by z-index in the array:
- First node = bottom layer (displayed below others)
- Last node = top layer (displayed above others)

### Generic Node Attributes

All nodes share these attributes:

| Attribute | Required | Type | Description |
|-----------|----------|------|-------------|
| `id` | Yes | string | Unique identifier for the node |
| `type` | Yes | string | Node type: `text`, `file`, `link`, or `group` |
| `x` | Yes | integer | X position in pixels |
| `y` | Yes | integer | Y position in pixels |
| `width` | Yes | integer | Width in pixels |
| `height` | Yes | integer | Height in pixels |
| `color` | No | canvasColor | Node color (see Color section) |

### Text Nodes

Text nodes contain Markdown content.

```json
{
  "id": "6f0ad84f44ce9c17",
  "type": "text",
  "x": 0,
  "y": 0,
  "width": 400,
  "height": 200,
  "text": "# Hello World\n\nThis is **Markdown** content."
}
```

#### Newline Escaping (Common Pitfall)

In JSON, newline characters inside strings **must** be represented as `\n`. Do **not** use the literal sequence `\\n` in a `.canvas` file—Obsidian will render it as the characters `\` and `n` instead of a line break.

Examples:

```json
{ "type": "text", "text": "Line 1\nLine 2" }
```

```json
{ "type": "text", "text": "Line 1\\nLine 2" }
```

| Attribute | Required | Type | Description |
|-----------|----------|------|-------------|
| `text` | Yes | string | Plain text with Markdown syntax |

### File Nodes

File nodes reference files or attachments (images, videos, PDFs, notes, etc.).

```json
{
  "id": "a1b2c3d4e5f67890",
  "type": "file",
  "x": 500,
  "y": 0,
  "width": 400,
  "height": 300,
  "file": "Attachments/diagram.png"
}
```

```json
{
  "id": "b2c3d4e5f6789012",
  "type": "file",
  "x": 500,
  "y": 400,
  "width": 400,
  "height": 300,
  "file": "Notes/Project Overview.md",
  "subpath": "#Implementation"
}
```

| Attribute | Required | Type | Description |
|-----------|----------|------|-------------|
| `file` | Yes | string | Path to file within the system |
| `subpath` | No | string | Link to heading or block (starts with `#`) |

### Link Nodes

Link nodes display external URLs.

```json
{
  "id": "c3d4e5f678901234",
  "type": "link",
  "x": 1000,
  "y": 0,
  "width": 400,
  "height": 200,
  "url": "https://obsidian.md"
}
```

| Attribute | Required | Type | Description |
|-----------|----------|------|-------------|
| `url` | Yes | string | External URL |

### Group Nodes

Group nodes are visual containers for organizing other nodes.

```json
{
  "id": "d4e5f6789012345a",
  "type": "group",
  "x": -50,
  "y": -50,
  "width": 1000,
  "height": 600,
  "label": "Project Overview",
  "color": "4"
}
```

```json
{
  "id": "e5f67890123456ab",
  "type": "group",
  "x": 0,
  "y": 700,
  "width": 800,
  "height": 500,
  "label": "Resources",
  "background": "Attachments/background.png",
  "backgroundStyle": "cover"
}
```

| Attribute | Required | Type | Description |
|-----------|----------|------|-------------|
| `label` | No | string | Text label for the group |
| `background` | No | string | Path to background image |
| `backgroundStyle` | No | string | Background rendering style |

#### Background Styles

| Value | Description |
|-------|-------------|
| `cover` | Fills entire width and height of node |
| `ratio` | Maintains aspect ratio of background image |
| `repeat` | Repeats image as pattern in both directions |

## Edges

Edges are lines connecting nodes.

```json
{
  "id": "f67890123456789a",
  "fromNode": "6f0ad84f44ce9c17",
  "toNode": "a1b2c3d4e5f67890"
}
```

```json
{
  "id": "0123456789abcdef",
  "fromNode": "6f0ad84f44ce9c17",
  "fromSide": "right",
  "fromEnd": "none",
  "toNode": "b2c3d4e5f6789012",
  "toSide": "left",
  "toEnd": "arrow",
  "color": "1",
  "label": "leads to"
}
```

| Attribute | Required | Type | Default | Description |
|-----------|----------|------|---------|-------------|
| `id` | Yes | string | - | Unique identifier for the edge |
| `fromNode` | Yes | string | - | Node ID where connection starts |
| `fromSide` | No | string | - | Side where edge starts |
| `fromEnd` | No | string | `none` | Shape at edge start |
| `toNode` | Yes | string | - | Node ID where connection ends |
| `toSide` | No | string | - | Side where edge ends |
| `toEnd` | No | string | `arrow` | Shape at edge end |
| `color` | No | canvasColor | - | Line color |
| `label` | No | string | - | Text label for the edge |

### Side Values

| Value | Description |
|-------|-------------|
| `top` | Top edge of node |
| `right` | Right edge of node |
| `bottom` | Bottom edge of node |
| `left` | Left edge of node |

### End Shapes

| Value | Description |
|-------|-------------|
| `none` | No endpoint shape |
| `arrow` | Arrow endpoint |

## Colors

The `canvasColor` type can be specified in two ways:

### Hex Colors

```json
{
  "color": "#FF0000"
}
```

### Preset Colors

```json
{
  "color": "1"
}
```

| Preset | Color |
|--------|-------|
| `"1"` | Red |
| `"2"` | Orange |
| `"3"` | Yellow |
| `"4"` | Green |
| `"5"` | Cyan |
| `"6"` | Purple |

Note: Specific color values for presets are intentionally undefined, allowing applications to use their own brand colors.

## Complete Examples

### Simple Canvas with Text and Connections

```json
{
  "nodes": [
    {
      "id": "8a9b0c1d2e3f4a5b",
      "type": "text",
      "x": 0,
      "y": 0,
      "width": 300,
      "height": 150,
      "text": "# Main Idea\n\nThis is the central concept."
    },
    {
      "id": "1a2b3c4d5e6f7a8b",
      "type": "text",
      "x": 400,
      "y": -100,
      "width": 250,
      "height": 100,
      "text": "## Supporting Point A\n\nDetails here."
    },
    {
      "id": "2b3c4d5e6f7a8b9c",
      "type": "text",
      "x": 400,
      "y": 100,
      "width": 250,
      "height": 100,
      "text": "## Supporting Point B\n\nMore details."
    }
  ],
  "edges": [
    {
      "id": "3c4d5e6f7a8b9c0d",
      "fromNode": "8a9b0c1d2e3f4a5b",
      "fromSide": "right",
      "toNode": "1a2b3c4d5e6f7a8b",
      "toSide": "left"
    },
    {
      "id": "4d5e6f7a8b9c0d1e",
      "fromNode": "8a9b0c1d2e3f4a5b",
      "fromSide": "right",
      "toNode": "2b3c4d5e6f7a8b9c",
      "toSide": "left"
    }
  ]
}
```

### Project Board with Groups

```json
{
  "nodes": [
    {
      "id": "5e6f7a8b9c0d1e2f",
      "type": "group",
      "x": 0,
      "y": 0,
      "width": 300,
      "height": 500,
      "label": "To Do",
      "color": "1"
    },
    {
      "id": "6f7a8b9c0d1e2f3a",
      "type": "group",
      "x": 350,
      "y": 0,
      "width": 300,
      "height": 500,
      "label": "In Progress",
      "color": "3"
    },
    {
      "id": "7a8b9c0d1e2f3a4b",
      "type": "group",
      "x": 700,
      "y": 0,
      "width": 300,
      "height": 500,
      "label": "Done",
      "color": "4"
    },
    {
      "id": "8b9c0d1e2f3a4b5c",
      "type": "text",
      "x": 20,
      "y": 50,
      "width": 260,
      "height": 80,
      "text": "## Task 1\n\nImplement feature X"
    },
    {
      "id": "9c0d1e2f3a4b5c6d",
      "type": "text",
      "x": 370,
      "y": 50,
      "width": 260,
      "height": 80,
      "text": "## Task 2\n\nReview PR #123",
      "color": "2"
    },
    {
      "id": "0d1e2f3a4b5c6d7e",
      "type": "text",
      "x": 720,
      "y": 50,
      "width": 260,
      "height": 80,
      "text": "## Task 3\n\n~~Setup CI/CD~~"
    }
  ],
  "edges": []
}
```

### Research Canvas with Files and Links

```json
{
  "nodes": [
    {
      "id": "1e2f3a4b5c6d7e8f",
      "type": "text",
      "x": 300,
      "y": 200,
      "width": 400,
      "height": 200,
      "text": "# Research Topic\n\n## Key Questions\n\n- How does X affect Y?\n- What are the implications?",
      "color": "5"
    },
    {
      "id": "2f3a4b5c6d7e8f9a",
      "type": "file",
      "x": 0,
      "y": 0,
      "width": 250,
      "height": 150,
      "file": "Literature/Paper A.pdf"
    },
    {
      "id": "3a4b5c6d7e8f9a0b",
      "type": "file",
      "x": 0,
      "y": 200,
      "width": 250,
      "height": 150,
      "file": "Notes/Meeting Notes.md",
      "subpath": "#Key Insights"
    },
    {
      "id": "4b5c6d7e8f9a0b1c",
      "type": "link",
      "x": 0,
      "y": 400,
      "width": 250,
      "height": 100,
      "url": "https://example.com/research"
    },
    {
      "id": "5c6d7e8f9a0b1c2d",
      "type": "file",
      "x": 750,
      "y": 150,
      "width": 300,
      "height": 250,
      "file": "Attachments/diagram.png"
    }
  ],
  "edges": [
    {
      "id": "6d7e8f9a0b1c2d3e",
      "fromNode": "2f3a4b5c6d7e8f9a",
      "fromSide": "right",
      "toNode": "1e2f3a4b5c6d7e8f",
      "toSide": "left",
      "label": "supports"
    },
    {
      "id": "7e8f9a0b1c2d3e4f",
      "fromNode": "3a4b5c6d7e8f9a0b",
      "fromSide": "right",
      "toNode": "1e2f3a4b5c6d7e8f",
      "toSide": "left",
      "label": "informs"
    },
    {
      "id": "8f9a0b1c2d3e4f5a",
      "fromNode": "4b5c6d7e8f9a0b1c",
      "fromSide": "right",
      "toNode": "1e2f3a4b5c6d7e8f",
      "toSide": "left",
      "toEnd": "arrow",
      "color": "6"
    },
    {
      "id": "9a0b1c2d3e4f5a6b",
      "fromNode": "1e2f3a4b5c6d7e8f",
      "fromSide": "right",
      "toNode": "5c6d7e8f9a0b1c2d",
      "toSide": "left",
      "label": "visualized by"
    }
  ]
}
```

### Flowchart

```json
{
  "nodes": [
    {
      "id": "a0b1c2d3e4f5a6b7",
      "type": "text",
      "x": 200,
      "y": 0,
      "width": 150,
      "height": 60,
      "text": "**Start**",
      "color": "4"
    },
    {
      "id": "b1c2d3e4f5a6b7c8",
      "type": "text",
      "x": 200,
      "y": 100,
      "width": 150,
      "height": 60,
      "text": "Step 1:\nGather data"
    },
    {
      "id": "c2d3e4f5a6b7c8d9",
      "type": "text",
      "x": 200,
      "y": 200,
      "width": 150,
      "height": 80,
      "text": "**Decision**\n\nIs data valid?",
      "color": "3"
    },
    {
      "id": "d3e4f5a6b7c8d9e0",
      "type": "text",
      "x": 400,
      "y": 200,
      "width": 150,
      "height": 60,
      "text": "Process data"
    },
    {
      "id": "e4f5a6b7c8d9e0f1",
      "type": "text",
      "x": 0,
      "y": 200,
      "width": 150,
      "height": 60,
      "text": "Request new data",
      "color": "1"
    },
    {
      "id": "f5a6b7c8d9e0f1a2",
      "type": "text",
      "x": 400,
      "y": 320,
      "width": 150,
      "height": 60,
      "text": "**End**",
      "color": "4"
    }
  ],
  "edges": [
    {
      "id": "a6b7c8d9e0f1a2b3",
      "fromNode": "a0b1c2d3e4f5a6b7",
      "fromSide": "bottom",
      "toNode": "b1c2d3e4f5a6b7c8",
      "toSide": "top"
    },
    {
      "id": "b7c8d9e0f1a2b3c4",
      "fromNode": "b1c2d3e4f5a6b7c8",
      "fromSide": "bottom",
      "toNode": "c2d3e4f5a6b7c8d9",
      "toSide": "top"
    },
    {
      "id": "c8d9e0f1a2b3c4d5",
      "fromNode": "c2d3e4f5a6b7c8d9",
      "fromSide": "right",
      "toNode": "d3e4f5a6b7c8d9e0",
      "toSide": "left",
      "label": "Yes",
      "color": "4"
    },
    {
      "id": "d9e0f1a2b3c4d5e6",
      "fromNode": "c2d3e4f5a6b7c8d9",
      "fromSide": "left",
      "toNode": "e4f5a6b7c8d9e0f1",
      "toSide": "right",
      "label": "No",
      "color": "1"
    },
    {
      "id": "e0f1a2b3c4d5e6f7",
      "fromNode": "e4f5a6b7c8d9e0f1",
      "fromSide": "top",
      "fromEnd": "none",
      "toNode": "b1c2d3e4f5a6b7c8",
      "toSide": "left",
      "toEnd": "arrow"
    },
    {
      "id": "f1a2b3c4d5e6f7a8",
      "fromNode": "d3e4f5a6b7c8d9e0",
      "fromSide": "bottom",
      "toNode": "f5a6b7c8d9e0f1a2",
      "toSide": "top"
    }
  ]
}
```

## ID Generation

Node and edge IDs must be unique strings. Obsidian generates 16-character hexadecimal IDs:

```json
"id": "6f0ad84f44ce9c17"
"id": "a3b2c1d0e9f8g7h6"
"id": "1234567890abcdef"
```

This format is a 16-character lowercase hex string (64-bit random value).

## Layout Guidelines

### Positioning

- Coordinates can be negative (canvas extends infinitely)
- `x` increases to the right
- `y` increases downward
- Position refers to top-left corner of node

### Recommended Sizes

| Node Type | Suggested Width | Suggested Height |
|-----------|-----------------|------------------|
| Small text | 200-300 | 80-150 |
| Medium text | 300-450 | 150-300 |
| Large text | 400-600 | 300-500 |
| File preview | 300-500 | 200-400 |
| Link preview | 250-400 | 100-200 |
| Group | Varies | Varies |

### Height Estimation (Critical)

JSON Canvas does **not** support auto-height. You must calculate node heights based on content to avoid scrollbars.

#### Common Pitfall

If height is too small, Obsidian shows internal scrollbars in the node, making content hard to read. **Always estimate heights generously.**

#### Height Calculation Formula

```
height = title_height + content_height + padding
```

Where:
- `title_height` = 35px (for `## Title` or `# Title`)
- `padding` = 30px (node internal padding)

#### Per-Element Heights

| Element Type | Height (px) | Notes |
|--------------|-------------|-------|
| H1/H2 title line | 35 | `# Title` or `## Title` |
| Normal text line | 25 | Regular paragraph text |
| Code line (in block) | 22 | Monospace font, slightly smaller |
| Code block padding | 20 | Add once per code block |
| Table header row | 35 | Includes separator line |
| Table data row | 28 | Per row of data |
| Empty line | 15 | Blank line for spacing |
| List item | 25 | Same as text line |

#### Calculation Examples

**Example 1: Simple text node**
```
## Title              (35px)
                      (15px empty line)
Normal text line 1    (25px)
Normal text line 2    (25px)
+ node padding        (30px)
─────────────────────
Total: 130px → use height: 140
```

**Example 2: Node with code block**
```
## Function Name      (35px)
                      (15px empty line)
```python             (code block start)
line 1                (22px)
line 2                (22px)
line 3                (22px)
```                   (code block padding: 20px)
+ node padding        (30px)
─────────────────────
Total: 166px → use height: 180
```

**Example 3: Node with table**
```
## Table Title        (35px)
                      (15px empty line)
| Col1 | Col2 |       (35px header)
|------|------|
| data | data |       (28px)
| data | data |       (28px)
| data | data |       (28px)
+ node padding        (30px)
─────────────────────
Total: 199px → use height: 210
```

#### Width Considerations

- Code blocks need wider nodes (350-500px) to avoid horizontal scrolling
- Tables need width based on column count: `width ≈ columns × 100 + 50`
- CJK (Chinese/Japanese/Korean) text may need slightly more width per character

#### Safety Margin

Always add 10-20px extra to your calculated height. It's better to have slight extra space than scrollbars.

### Spacing

- Leave 20-50px padding inside groups
- Space nodes 50-100px apart for readability
- Align nodes to grid (multiples of 10 or 20) for cleaner layouts

## Validation Rules

1. All `id` values must be unique across nodes and edges
2. `fromNode` and `toNode` must reference existing node IDs
3. Required fields must be present for each node type
4. `type` must be one of: `text`, `file`, `link`, `group`
5. `backgroundStyle` must be one of: `cover`, `ratio`, `repeat`
6. `fromSide`, `toSide` must be one of: `top`, `right`, `bottom`, `left`
7. `fromEnd`, `toEnd` must be one of: `none`, `arrow`
8. Color presets must be `"1"` through `"6"` or valid hex color

## References

- [JSON Canvas Spec 1.0](https://jsoncanvas.org/spec/1.0/)
- [JSON Canvas GitHub](https://github.com/obsidianmd/jsoncanvas)
