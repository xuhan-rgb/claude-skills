#!/usr/bin/env python3
"""
cmd-notes helper: read/write the per-project cmd_notes.html file.

Claude calls these functions to add/edit/delete/query commands without
manually parsing the HTML. Storage format: a single HTML file with the
notes data embedded as <script type="application/json" id="cmd-notes-data">.
"""

import os
import re
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional


# ─────────────────────────────────────────────────────────────────────────────
# Project root detection
# ─────────────────────────────────────────────────────────────────────────────

_ROOT_MARKERS = [
    ".git",
    "CLAUDE.md",
    "pyproject.toml",
    "package.json",
    "Cargo.toml",
    "go.mod",
    "cmd_notes.html",  # already initialized
]


def find_project_root(start: Optional[str] = None) -> str:
    """Walk up from `start` (or cwd) looking for a project marker.
    Falls back to the original start dir if nothing found.
    """
    cur = os.path.abspath(start or os.getcwd())
    original = cur
    while True:
        for marker in _ROOT_MARKERS:
            if os.path.exists(os.path.join(cur, marker)):
                return cur
        parent = os.path.dirname(cur)
        if parent == cur:
            return original
        cur = parent


# ─────────────────────────────────────────────────────────────────────────────
# File I/O
# ─────────────────────────────────────────────────────────────────────────────

DATA_BLOCK_RE = re.compile(
    r'(<script type="application/json" id="cmd-notes-data">)([\s\S]*?)(</script>)'
)


def _template_path() -> str:
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "template.html")


def _initial_data(project_root: str) -> dict:
    return {
        "version": "1.0",
        "project": os.path.basename(project_root.rstrip("/")) or "Project",
        "project_root": project_root,
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "notes": [],
    }


def ensure_notes_file(project_root: str) -> str:
    """Return the path to cmd_notes.html in project_root.
    Create it from the template if it doesn't exist.
    """
    notes_path = os.path.join(project_root, "cmd_notes.html")
    if os.path.exists(notes_path):
        return notes_path

    with open(_template_path(), "r", encoding="utf-8") as f:
        tpl = f.read()

    data = _initial_data(project_root)
    html = (
        tpl
        .replace("{{PROJECT_NAME}}", data["project"])
        .replace("{{PROJECT_PATH}}", data["project_root"])
        .replace("{{NOTES_JSON}}", json.dumps(data, indent=2, ensure_ascii=False))
    )
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write(html)
    return notes_path


def read_notes_data(notes_path: str) -> dict:
    """Extract the embedded JSON data from cmd_notes.html."""
    if not os.path.exists(notes_path):
        raise FileNotFoundError(f"Notes file not found: {notes_path}")
    with open(notes_path, "r", encoding="utf-8") as f:
        html = f.read()
    m = DATA_BLOCK_RE.search(html)
    if not m:
        raise ValueError(f"No <script id='cmd-notes-data'> block found in {notes_path}")
    try:
        return json.loads(m.group(2).strip())
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in {notes_path}: {e}")


def write_notes_data(notes_path: str, data: dict) -> None:
    """Update the embedded JSON data in cmd_notes.html in place."""
    with open(notes_path, "r", encoding="utf-8") as f:
        html = f.read()
    new_json = json.dumps(data, indent=2, ensure_ascii=False)

    def replace(match):
        return f"{match.group(1)}\n{new_json}\n{match.group(3)}"

    new_html = DATA_BLOCK_RE.sub(replace, html, count=1)
    if new_html == html:
        raise ValueError(f"Failed to update JSON block in {notes_path}")
    with open(notes_path, "w", encoding="utf-8") as f:
        f.write(new_html)


# ─────────────────────────────────────────────────────────────────────────────
# Tag auto-detection
# ─────────────────────────────────────────────────────────────────────────────

_TAG_RULES = [
    (r"\bdocker\b", "docker"),
    (r"\bgit\b", "git"),
    (r"\bcommit\b", "git"),
    (r"\b(ros2|colcon|rviz|rqt)\b", "ros2"),
    (r"\b(nvidia-smi|gpustat|nvtop)\b", ["gpu", "monitor"]),
    (r"\bpython\b.*\b(train|fit)\b", ["train", "python"]),
    (r"\bpython\b.*\b(test|eval|infer|predict)\b", ["test", "python"]),
    (r"\bpython\b", "python"),
    (r"\bbash\b.*\.sh\b", "bash"),
    (r"\b(pip|conda|venv|poetry)\b", "env"),
    (r"\b(tmux|screen)\b", "session"),
    (r"\b(ssh|scp|rsync)\b", "remote"),
    (r"\b(kubectl|helm|k9s)\b", "k8s"),
    (r"\b(curl|wget|httpie|http)\b", "http"),
    (r"\b(vim|nvim|nano|emacs|code)\b", "editor"),
    (r"\b(npm|yarn|pnpm|node)\b", "node"),
    (r"\bcargo\b", "rust"),
    (r"\bgo\s+(build|run|test)\b", "go"),
    (r"\bmake\b", "build"),
    (r"\b(systemctl|journalctl|service)\b", "systemd"),
    (r"\b(grep|find|awk|sed|jq)\b", "search"),
]


def suggest_tags(command: str) -> List[str]:
    """Suggest tags based on the command text."""
    cmd = command.lower()
    out = []
    for pattern, tag in _TAG_RULES:
        if re.search(pattern, cmd):
            if isinstance(tag, list):
                for t in tag:
                    if t not in out:
                        out.append(t)
            elif tag not in out:
                out.append(tag)
    return out


# ─────────────────────────────────────────────────────────────────────────────
# CRUD operations
# ─────────────────────────────────────────────────────────────────────────────

def _make_id() -> str:
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    return f"{ts}-{uuid.uuid4().hex[:4]}"


def _now_iso() -> str:
    return datetime.now().isoformat(timespec="seconds")


def add_note(
    notes_path: str,
    title: str,
    command: str,
    description: str = "",
    tags: Optional[List[str]] = None,
    cwd: Optional[str] = None,
) -> dict:
    """Add a new note. Returns the created note dict."""
    data = read_notes_data(notes_path)
    if tags is None:
        tags = []
    note = {
        "id": _make_id(),
        "title": title.strip(),
        "command": command.strip(),
        "description": description.strip(),
        "tags": [t.strip() for t in tags if t.strip()],
        "cwd": cwd or os.getcwd(),
        "created_at": _now_iso(),
        "updated_at": _now_iso(),
    }
    data.setdefault("notes", []).append(note)
    write_notes_data(notes_path, data)
    return note


def update_note(notes_path: str, note_id: str, **fields) -> Optional[dict]:
    """Update specific fields of an existing note. Returns the updated note or None."""
    data = read_notes_data(notes_path)
    for note in data.get("notes", []):
        if note["id"] == note_id:
            for k, v in fields.items():
                if k in ("title", "command", "description"):
                    note[k] = (v or "").strip()
                elif k == "tags":
                    note[k] = [t.strip() for t in (v or []) if t.strip()]
            note["updated_at"] = _now_iso()
            write_notes_data(notes_path, data)
            return note
    return None


def delete_note(notes_path: str, note_id: str) -> bool:
    """Delete a note by ID. Returns True if deleted."""
    data = read_notes_data(notes_path)
    before = len(data.get("notes", []))
    data["notes"] = [n for n in data.get("notes", []) if n["id"] != note_id]
    if len(data["notes"]) < before:
        write_notes_data(notes_path, data)
        return True
    return False


def query_notes(notes_path: str, search: str = "", tags: Optional[List[str]] = None) -> List[dict]:
    """Search notes by text and/or tags. Empty search returns all notes."""
    data = read_notes_data(notes_path)
    notes = data.get("notes", [])
    if search:
        s = search.lower()
        notes = [
            n for n in notes
            if s in (n.get("title", "") or "").lower()
            or s in (n.get("command", "") or "").lower()
            or s in (n.get("description", "") or "").lower()
            or any(s in t.lower() for t in (n.get("tags") or []))
        ]
    if tags:
        notes = [
            n for n in notes
            if all(t in (n.get("tags") or []) for t in tags)
        ]
    notes.sort(key=lambda n: n.get("updated_at", ""), reverse=True)
    return notes


def list_all_notes(notes_path: str) -> List[dict]:
    """Return all notes sorted by updated_at desc."""
    return query_notes(notes_path, "")


# ─────────────────────────────────────────────────────────────────────────────
# Convenience: parse a /cmd-note input string
# ─────────────────────────────────────────────────────────────────────────────

def parse_cmd_note_input(text: str) -> dict:
    """Parse a `/cmd-note` argument string into title/command/description/tags.

    Supported formats:
      1. Pipe-separated: 'cmd | title | description | tags'
         where tags is comma-separated. Any field can be empty.
      2. Plain command + free-text description that may contain #tags
         e.g. 'docker exec -it x bash 进入容器 #docker #debug'
    """
    text = text.strip()
    if not text:
        return {"command": "", "title": "", "description": "", "tags": []}

    if "|" in text:
        parts = [p.strip() for p in text.split("|")]
        command = parts[0] if len(parts) > 0 else ""
        title = parts[1] if len(parts) > 1 else ""
        description = parts[2] if len(parts) > 2 else ""
        tags_str = parts[3] if len(parts) > 3 else ""
        tags = [t.strip() for t in tags_str.split(",") if t.strip()]
        return {"command": command, "title": title, "description": description, "tags": tags}

    # Plain mode: extract #tags from text, command is everything before description.
    # Heuristic: command goes until end of line; let user split via pipes if needed.
    tag_matches = re.findall(r"#(\w[\w-]*)", text)
    text_no_tags = re.sub(r"#\w[\w-]*", "", text).strip()
    return {
        "command": text_no_tags,
        "title": "",
        "description": "",
        "tags": tag_matches,
    }
