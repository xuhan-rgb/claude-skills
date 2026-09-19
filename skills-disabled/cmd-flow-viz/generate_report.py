#!/usr/bin/env python3
"""
cmd-flow-viz: Report generator helper.

Claude only needs to fill in a structured dict (see ReportData below) and call
generate_report(data, output_path). This script handles:
  - Mermaid label escaping (avoids common syntax pitfalls)
  - Template rendering with placeholders
  - Empty section hiding
  - Filename + path management
  - HTML escaping for text fields

Usage from Claude:
    from generate_report import ReportData, TechCard, generate_report

    data = ReportData(
        title="train_xxx.sh",
        metadata_lines=["Source: ...", "Type: bash → python ML training"],
        purpose="...",
        inputs=["Dataset: ...", "Pretrained: ..."],
        outputs=["model_best.pth", "logs/"],
        tech_cards=[
            TechCard("Backbone", {"arch": "ResNet-18", ...}),
            ...
        ],
        logic_flow=[
            ("Img", "原图 (1080,1920,3)"),
            ("Aug", "数据增强"),
            ...
        ],
        logic_edges=[
            ("Img", "Aug", None),
            ...
        ],
    )
    generate_report(data, "/path/to/output.html")
"""

import os
import re
import html
import base64
import mimetypes
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple, Dict, Optional


# ─────────────────────────────────────────────────────────────────────────────
# Mermaid label sanitization
# ─────────────────────────────────────────────────────────────────────────────

# Characters that break Mermaid even inside double quotes.
# Replacements use safe Unicode equivalents.
_MERMAID_REPLACEMENTS = {
    '(': ' ',
    ')': ' ',
    '[': '【',
    ']': '】',
    '{': ' ',
    '}': ' ',
    '/': '／',  # full-width slash
    '\\': '＼',
    '"': "'",
    '`': "'",
    '|': '｜',
}


def safe_label(text: str) -> str:
    """Sanitize a string for use as a Mermaid node label.

    - Replaces characters that break Mermaid parser (even inside quotes)
    - Keeps <br/> tags (the only allowed HTML)
    - Strips leading/trailing whitespace per line
    """
    if not text:
        return " "
    # Preserve <br/> by temporarily masking it
    text = text.replace('<br/>', '\x00BR\x00').replace('<br>', '\x00BR\x00')
    for k, v in _MERMAID_REPLACEMENTS.items():
        text = text.replace(k, v)
    text = text.replace('\x00BR\x00', '<br/>')
    # Collapse runs of spaces (but keep <br/> structure)
    parts = text.split('<br/>')
    parts = [re.sub(r'  +', ' ', p.strip()) for p in parts]
    return '<br/>'.join(parts)


def safe_node_id(name: str) -> str:
    """Sanitize a node ID. Mermaid IDs must match [A-Za-z0-9_].

    For non-ASCII inputs, append a short hash so different inputs
    map to unique IDs.
    """
    cleaned = re.sub(r'[^A-Za-z0-9_]', '_', name)
    # If the original had non-ASCII or got mangled, append hash for uniqueness
    if cleaned != name or not cleaned:
        import hashlib
        h = hashlib.md5(name.encode('utf-8')).hexdigest()[:6]
        cleaned = f"{cleaned}_{h}" if cleaned else f"N_{h}"
    # Ensure leading char is letter or underscore
    if not cleaned or not (cleaned[0].isalpha() or cleaned[0] == '_'):
        cleaned = 'N_' + cleaned
    return cleaned


# ─────────────────────────────────────────────────────────────────────────────
# Data structures
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class TechCard:
    """One card in the Tech Stack section."""
    title: str           # e.g. "Backbone", "Loss"
    icon: str = ""       # optional emoji
    items: Dict[str, str] = field(default_factory=dict)
    # items maps "key" -> "value" (value may contain HTML like <code>)


@dataclass
class KeyInsight:
    """One highlighted insight in the 'Key Insights' section.

    Examples:
      - For ML: "Loss function design", "GT generation strategy"
      - For tracking: "Track association strategy", "Lifecycle management"
      - For SLAM: "Frontend feature extraction", "Backend optimization"

    body_html supports rich HTML including:
      - <p>...</p> paragraphs
      - <pre><code>...</code></pre> code blocks
      - <div class="formula">...</div> formula box
      - <img src="data:image/png;base64,..." /> embedded images
      - <div class="img-row"><div><img/><div class="img-caption">...</div></div>...</div>
        for side-by-side images with captions
    """
    title: str            # e.g. "💡 Loss Function Design"
    icon: str = ""        # optional emoji prefix
    body_html: str = ""   # rich HTML content


@dataclass
class ReportData:
    """All structured data needed to generate one report."""
    title: str
    metadata_lines: List[str]
    purpose: str                                # supports HTML
    inputs: List[str]                           # one bullet each (HTML allowed)
    outputs: List[str]                          # one bullet each (HTML allowed)

    # Key insights — the most important domain-specific knowledge points
    # (e.g. for ML: loss design + GT generation; for tracking: association strategy)
    key_insights: List[KeyInsight] = field(default_factory=list)

    # Tech stack (optional, hide if empty)
    tech_cards: List[TechCard] = field(default_factory=list)

    # Logic flowchart: list of (node_id, label) and (from_id, to_id, edge_label)
    # Optional subgraphs for grouping: {subgraph_name: [node_ids]}
    logic_nodes: List[Tuple[str, str]] = field(default_factory=list)
    logic_edges: List[Tuple[str, str, Optional[str]]] = field(default_factory=list)
    logic_subgraphs: Dict[str, List[str]] = field(default_factory=dict)
    logic_direction: str = "TD"  # TD, LR, BT, RL

    # Topic communication graph (multi-command only)
    topic_nodes: List[Tuple[str, str]] = field(default_factory=list)
    topic_edges: List[Tuple[str, str, Optional[str]]] = field(default_factory=list)

    # State machine (optional)
    state_transitions: List[Tuple[str, str, Optional[str]]] = field(default_factory=list)
    # Each tuple: (from_state, to_state, trigger)


# ─────────────────────────────────────────────────────────────────────────────
# Mermaid rendering
# ─────────────────────────────────────────────────────────────────────────────

def render_flowchart(
    nodes: List[Tuple[str, str]],
    edges: List[Tuple[str, str, Optional[str]]],
    subgraphs: Optional[Dict[str, List[str]]] = None,
    direction: str = "TD",
) -> str:
    if not nodes:
        return ""

    lines = [f"flowchart {direction}"]

    # If subgraphs given, render them; nodes inside subgraph are declared there
    used_in_subgraph = set()
    if subgraphs:
        for sg_name, sg_nodes in subgraphs.items():
            sg_id = safe_node_id(sg_name)
            lines.append(f'    subgraph {sg_id}["{safe_label(sg_name)}"]')
            for nid in sg_nodes:
                node = next((n for n in nodes if n[0] == nid), None)
                if node:
                    nid_safe = safe_node_id(node[0])
                    lbl = safe_label(node[1])
                    lines.append(f'        {nid_safe}["{lbl}"]')
                    used_in_subgraph.add(node[0])
            lines.append("    end")

    # Declare remaining nodes outside subgraphs
    for nid, label in nodes:
        if nid in used_in_subgraph:
            continue
        nid_safe = safe_node_id(nid)
        lbl = safe_label(label)
        lines.append(f'    {nid_safe}["{lbl}"]')

    # Edges
    for src, dst, lbl in edges:
        s = safe_node_id(src)
        d = safe_node_id(dst)
        if lbl:
            lines.append(f'    {s} -->|{safe_label(lbl)}| {d}')
        else:
            lines.append(f'    {s} --> {d}')

    return "\n".join(lines)


def render_state_diagram(
    transitions: List[Tuple[str, str, Optional[str]]],
) -> str:
    if not transitions:
        return ""
    lines = ["stateDiagram-v2"]
    for src, dst, trig in transitions:
        s = "[*]" if src == "[*]" else safe_node_id(src)
        d = "[*]" if dst == "[*]" else safe_node_id(dst)
        if trig:
            lines.append(f"    {s} --> {d}: {safe_label(trig)}")
        else:
            lines.append(f"    {s} --> {d}")
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# HTML rendering
# ─────────────────────────────────────────────────────────────────────────────

def render_io_list(items: List[str]) -> str:
    if not items:
        return '          <li><em style="color:#7d8590">无</em></li>'
    return "\n".join(f'          <li>{item}</li>' for item in items)


def image_to_data_url(image_path: str) -> str:
    """Convert a local image file to a base64 data URL for HTML embedding.

    Returns "" if the file doesn't exist or can't be read.
    """
    if not os.path.exists(image_path):
        return ""
    mime, _ = mimetypes.guess_type(image_path)
    if mime is None:
        ext = os.path.splitext(image_path)[1].lower()
        mime = {'.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
                '.png': 'image/png', '.gif': 'image/gif',
                '.webp': 'image/webp', '.svg': 'image/svg+xml'}.get(ext, 'image/png')
    with open(image_path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    return f"data:{mime};base64,{b64}"


def img_tag(image_path: str, alt: str = "", style: str = "") -> str:
    """Convenience: build an <img> tag with embedded data URL."""
    url = image_to_data_url(image_path)
    if not url:
        return f'<div style="color:#f87171">[image not found: {html.escape(image_path)}]</div>'
    style_attr = f' style="{style}"' if style else ""
    return f'<img src="{url}" alt="{html.escape(alt)}"{style_attr} />'


def img_row(items: List[Tuple[str, str]]) -> str:
    """Build a row of side-by-side images. Each tuple = (image_path, caption)."""
    if not items:
        return ""
    out = ['<div class="img-row">']
    for path, caption in items:
        out.append('  <div>')
        out.append(f'    {img_tag(path, alt=caption)}')
        out.append(f'    <div class="img-caption">{caption}</div>')
        out.append('  </div>')
    out.append('</div>')
    return "\n".join(out)


def render_insights(insights: List[KeyInsight]) -> str:
    if not insights:
        return ""
    out = []
    for ins in insights:
        title = (ins.icon + " " if ins.icon else "") + html.escape(ins.title)
        out.append('      <div class="insight-item">')
        out.append(f'        <h3>{title}</h3>')
        out.append(f'        <div class="insight-body">{ins.body_html}</div>')
        out.append('      </div>')
    return "\n".join(out)


def render_tech_cards(cards: List[TechCard]) -> str:
    if not cards:
        return ""
    out = []
    for c in cards:
        title = (c.icon + " " if c.icon else "") + html.escape(c.title)
        out.append('      <div class="stack-card">')
        out.append(f'        <h4>{title}</h4>')
        out.append('        <dl>')
        for k, v in c.items.items():
            # k is key (no HTML), v can contain HTML like <code>
            out.append(f'          <dt>{html.escape(k)}</dt><dd>{v}</dd>')
        out.append('        </dl>')
        out.append('      </div>')
    return "\n".join(out)


def render_metadata(lines: List[str]) -> str:
    return "\n".join(f'<div>{line}</div>' for line in lines)


# ─────────────────────────────────────────────────────────────────────────────
# Main entry
# ─────────────────────────────────────────────────────────────────────────────

def generate_report(data: ReportData, output_path: str) -> str:
    """Generate the HTML report. Returns the absolute output path."""
    template_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html")
    with open(template_path, "r") as f:
        tpl = f.read()

    gen_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Render sections
    metadata_html = render_metadata(data.metadata_lines)
    inputs_html = render_io_list(data.inputs)
    outputs_html = render_io_list(data.outputs)
    insights_html = render_insights(data.key_insights)
    insight_hide = "" if data.key_insights else "empty"
    tech_html = render_tech_cards(data.tech_cards)
    tech_hide = "" if data.tech_cards else "empty"

    logic_flow = render_flowchart(
        data.logic_nodes, data.logic_edges,
        data.logic_subgraphs, data.logic_direction,
    )

    topic_graph = render_flowchart(
        data.topic_nodes, data.topic_edges, direction="LR",
    )
    topic_hide = "" if topic_graph else "empty"

    state_diagram = render_state_diagram(data.state_transitions)
    state_hide = "" if state_diagram else "empty"

    # Substitute
    html_out = (
        tpl
        .replace("{{TITLE}}", html.escape(data.title))
        .replace("{{METADATA}}", metadata_html)
        .replace("{{PURPOSE}}", data.purpose)
        .replace("{{INPUTS_HTML}}", inputs_html)
        .replace("{{OUTPUTS_HTML}}", outputs_html)
        .replace("{{INSIGHTS_HTML}}", insights_html)
        .replace("{{INSIGHT_HIDE}}", insight_hide)
        .replace("{{TECH_STACK_HTML}}", tech_html)
        .replace("{{TECH_HIDE}}", tech_hide)
        .replace("{{LOGIC_FLOWCHART}}", logic_flow)
        .replace("{{TOPIC_GRAPH}}", topic_graph)
        .replace("{{TOPIC_HIDE}}", topic_hide)
        .replace("{{STATE_MACHINE}}", state_diagram)
        .replace("{{STATE_HIDE}}", state_hide)
        .replace("{{GEN_TIME}}", gen_time)
    )

    output_path = os.path.abspath(output_path)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        f.write(html_out)

    return output_path


def make_filename(cmd_name: str, save_dir: str = ".") -> str:
    """Generate a timestamped output filename."""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = re.sub(r'[^A-Za-z0-9_.-]', '_', cmd_name)
    safe = os.path.splitext(safe)[0]
    return os.path.join(save_dir, f"cmd_flow_{safe}_{ts}.html")
