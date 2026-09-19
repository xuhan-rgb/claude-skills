#!/usr/bin/env python3
"""Install portable Claude/Codex configuration without exporting account state."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

REPO = Path(__file__).resolve().parents[1]
START = '<!-- claude-skills managed: start -->'
END = '<!-- claude-skills managed: end -->'


def merge_defaults(target, defaults):
    for key, value in defaults.items():
        if key not in target:
            target[key] = value
        elif isinstance(value, dict) and isinstance(target[key], dict):
            merge_defaults(target[key], value)


class Installer:
    def __init__(self, home, dry_run=False):
        self.home = home
        self.dry_run = dry_run
        self.backups = home / '.local/share/claude-skills-backups' / datetime.now().strftime('%Y%m%d-%H%M%S-%f')
        self.backed_up = set()

    def backup(self, path):
        if self.dry_run or path in self.backed_up or not os.path.lexists(path):
            return
        dst = self.backups / path.relative_to(self.home)
        dst.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        if path.is_symlink():
            dst.symlink_to(os.readlink(path))
        elif path.is_dir():
            shutil.copytree(path, dst, symlinks=True)
        else:
            shutil.copy2(path, dst)
            dst.chmod(0o600)
        self.backed_up.add(path)

    def write(self, path, content):
        if path.is_file() and path.read_text() == content:
            return
        print(f'WRITE {path}')
        if self.dry_run:
            return
        self.backup(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(path.name + '.claude-skills-tmp')
        with temp.open('w', encoding='utf-8') as stream:
            os.chmod(temp, 0o600)
            stream.write(content)
        temp.replace(path)

    def link(self, source, target):
        if target.exists() and target.resolve() == source.resolve():
            return
        # Never move a checkout that contains this running installer.
        if target.is_dir() and REPO.is_relative_to(target.resolve()):
            raise ValueError(f'Install from a checkout outside {target}')
        print(f'LINK {target} -> {source}')
        if self.dry_run:
            return
        self.backup(target)
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.is_symlink() or target.is_file():
            target.unlink()
        elif target.is_dir():
            shutil.rmtree(target)
        target.symlink_to(source, target_is_directory=True)

    def rules(self, path, content):
        old = path.read_text() if path.exists() else ''
        if START in old or END in old:
            if old.count(START) != 1 or old.count(END) != 1 or old.index(START) > old.index(END):
                raise ValueError(f'Invalid managed block: {path}')
            before, rest = old.split(START, 1)
            _, after = rest.split(END, 1)
        else:
            before, after = (old.rstrip() + '\n\n' if old.strip() else ''), '\n'
        self.write(path, before + START + '\n' + content.rstrip() + '\n' + END + after)


def configure(inst):
    import tomlkit
    home = inst.home
    codex = home / '.codex'
    claude = home / '.claude'
    cp = codex / 'config.toml'
    sp = claude / 'settings.json'
    # Parse both configs before performing any mutation. Never reset malformed files.
    cfg = tomlkit.parse(cp.read_text() if cp.exists() else '')
    settings = json.loads(sp.read_text()) if sp.exists() else {}
    if not isinstance(settings, dict):
        raise ValueError('Claude settings.json must contain an object')
    defaults = tomlkit.parse((REPO / 'config/codex/defaults.toml').read_text())
    merge_defaults(cfg, defaults)
    merge_defaults(settings, json.loads((REPO / 'config/claude/defaults.json').read_text()))
    enabled = set(json.loads((REPO / 'config/codex/enabled-skills.json').read_text()))
    entries = cfg.setdefault('skills', {}).setdefault('config', [])
    skills = sorted(p for p in REPO.iterdir() if (p / 'SKILL.md').is_file())
    for skill in skills:
        # Codex uses the shared skills directory; Claude uses its own search path.
        canonical = home / '.agents/skills' / skill.name
        for source_file in sorted(skill.rglob('SKILL.md')):
            dest_file = canonical / source_file.relative_to(skill)
            path = str(dest_file)
            active = skill.name in enabled and source_file == skill / 'SKILL.md'
            matches = [entry for entry in entries if entry.get('path') == path]
            if matches:
                for entry in matches:
                    entry['enabled'] = active
            else:
                entries.append({'path': path, 'enabled': active})
        inst.link(skill, canonical)
        inst.link(skill, claude / 'skills' / skill.name)
    common = (REPO / 'config/CLAUDE.md').read_text()
    inst.rules(claude / 'CLAUDE.md', common)
    inst.rules(codex / 'AGENTS.md', common + '\n' + (REPO / 'config/codex/delegation.md').read_text())
    for role in sorted((REPO / 'config/codex/agents').glob('*.toml')):
        tomlkit.parse(role.read_text())
        inst.write(codex / 'agents' / role.name, role.read_text())
    rendered = tomlkit.dumps(cfg)
    tomlkit.parse(rendered)
    inst.write(cp, rendered)
    inst.write(sp, json.dumps(settings, ensure_ascii=False, indent=2) + '\n')
    print(f'{len(skills)} skills installed; {len(enabled)} enabled by default in Codex.')


def install_manager(inst, checkout):
    if sys.platform != 'linux':
        raise ValueError('--with-manager currently requires Linux (or WSL with Kitty); core setup also supports macOS')
    for executable in ['git', 'uv', 'kitty']:
        if not shutil.which(executable):
            raise ValueError(f'--with-manager requires {executable}; see setup documentation')
    if inst.dry_run:
        print(f'MANAGER {checkout}: manager/install.sh + kitty-enhance/install.sh --full')
        return
    if not checkout.exists():
        checkout.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['git', 'clone', 'git@github.com:xuhan-rgb/claude-manager.git', str(checkout)], check=True)
    for script in ['manager/install.sh', 'kitty-enhance/install.sh']:
        if not (checkout / script).is_file():
            raise ValueError(f'Missing manager installer: {checkout / script}')
    # Upstream full installer overwrites these paths; take a complete backup first.
    for name in ['.config/kitty', '.claude/hooks', '.claude/settings.json', '.bashrc', '.zshrc']:
        inst.backup(inst.home / name)
    for name in ['codex', 'qq', 'claude-manager', 'agent-terminals', 'work-status']:
        inst.backup(inst.home / '.local/bin' / name)
    env = dict(os.environ, PATH=str(inst.home / '.local/bin') + os.pathsep + os.environ.get('PATH', ''))
    for folder, args in [('manager', []), ('kitty-enhance', ['--full'])]:
        subprocess.run(['bash', 'install.sh', *args], cwd=checkout / folder, env=env, check=True)
    # Upstream writes settings via a temporary file; keep account settings private.
    (inst.home / '.claude/settings.json').chmod(0o600)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dry-run', action='store_true', help='preview configuration changes; no target files written')
    parser.add_argument('--with-manager', action='store_true', help='also install manager and full Kitty enhancements (Linux)')
    parser.add_argument('--manager-dir', type=Path, help='reuse a claude-manager checkout without pulling or resetting it')
    args = parser.parse_args()
    if args.manager_dir and not args.with_manager:
        parser.error('--manager-dir requires --with-manager')
    if sys.version_info < (3, 9):
        parser.error('Python 3.9+ is required')
    inst = Installer(Path.home(), args.dry_run)
    if os.environ.get('CODEX_HOME') and Path(os.environ['CODEX_HOME']).expanduser() != inst.home / '.codex':
        parser.error('Custom CODEX_HOME is not supported; unset it before installing into ~/.codex')
    try:
        # Check optional dependencies before changing core configuration.
        if args.with_manager:
            if sys.platform != 'linux' or any(not shutil.which(x) for x in ['git', 'uv', 'kitty']):
                raise ValueError('--with-manager needs Linux, git, uv and Kitty; see setup documentation')
        configure(inst)
        if args.with_manager:
            checkout = (args.manager_dir or inst.home / '.local/share/claude-manager').expanduser().resolve()
            install_manager(inst, checkout)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f'Installation stopped: {exc}', file=sys.stderr)
        if inst.backed_up:
            print(f'Backups: {inst.backups}', file=sys.stderr)
        return 1
    print('Preview complete.' if args.dry_run else 'Configuration installed. Restart Claude Code and Codex to load it.')
    if inst.backed_up:
        print(f'Backups: {inst.backups}')
    print('Account login, provider/API keys, MCP services and skill dependencies are configured separately.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
