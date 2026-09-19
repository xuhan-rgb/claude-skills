import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import ANY, call, patch

import tomlkit


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("portable_install", ROOT / "scripts/install.py")
INSTALL = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(INSTALL)


class InstallerIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.home = Path(self.tempdir.name)
        self.stdout = io.StringIO()
        self.stdout_redirect = redirect_stdout(self.stdout)
        self.stdout_redirect.__enter__()
        self.skills = sorted(path for path in ROOT.iterdir() if (path / "SKILL.md").is_file())
        self.enabled = set(json.loads((ROOT / "config/codex/enabled-skills.json").read_text()))

    def tearDown(self):
        self.stdout_redirect.__exit__(None, None, None)
        self.tempdir.cleanup()

    def install(self, dry_run=False):
        INSTALL.configure(INSTALL.Installer(self.home, dry_run=dry_run))

    def test_empty_home_installs_clients_skills_roles_and_parseable_configs(self):
        self.install()

        settings_path = self.home / ".claude/settings.json"
        config_path = self.home / ".codex/config.toml"
        settings = json.loads(settings_path.read_text())
        config = tomlkit.parse(config_path.read_text())
        self.assertIsInstance(settings, dict)
        self.assertEqual(config["model"], "gpt-6-astra")
        self.assertIn("skills", config)

        common = (ROOT / "config/CLAUDE.md").read_text()
        self.assertIn(INSTALL.START, (self.home / ".claude/CLAUDE.md").read_text())
        self.assertIn(INSTALL.END, (self.home / ".codex/AGENTS.md").read_text())
        self.assertIn(common, (self.home / ".claude/CLAUDE.md").read_text())
        self.assertIn(common, (self.home / ".codex/AGENTS.md").read_text())

        entries = config["skills"]["config"]
        entry_by_path = {entry["path"]: entry for entry in entries}
        for skill in self.skills:
            canonical = self.home / ".agents/skills" / skill.name
            self.assertTrue(canonical.is_symlink())
            self.assertEqual(canonical.resolve(), skill.resolve())
            claude_link = self.home / ".claude/skills" / skill.name
            self.assertTrue(claude_link.is_symlink())
            self.assertEqual(claude_link.resolve(), skill.resolve())
            root_entry = entry_by_path[str(canonical / "SKILL.md")]
            self.assertEqual(root_entry["enabled"], skill.name in self.enabled)

        role_names = {path.name for path in (ROOT / "config/codex/agents").glob("*.toml")}
        self.assertEqual(role_names, {"luna_explorer.toml", "luna_worker.toml"})
        for role in role_names:
            installed = self.home / ".codex/agents" / role
            self.assertTrue(installed.is_file())
            tomlkit.parse(installed.read_text())

    def test_existing_configuration_preserves_machine_values_and_adds_defaults(self):
        codex = self.home / ".codex/config.toml"
        claude = self.home / ".claude/settings.json"
        codex.parent.mkdir(parents=True)
        claude.parent.mkdir(parents=True)
        codex.write_text(
            "model = \"machine-model\"\n"
            "model_provider = \"private\"\n"
            "model_reasoning_effort = \"high\"\n"
            "[model_providers.private]\nname = \"Private\"\n"
            "base_url = \"https://provider.example\"\n"
            "[mcp_servers.docs]\ncommand = \"docs-mcp\"\n"
            "[projects.\"/workspace/project\"]\ntrust_level = \"trusted\"\n"
        )
        claude.write_text(
            json.dumps(
                {
                    "model": "machine-claude-model",
                    "env": {"PRIVATE_TOKEN": "keep"},
                    "permissions": {"allow": ["Read(*)"]},
                    "hooks": {"PreToolUse": [{"command": "keep-hook"}]},
                }
            )
        )

        self.install()
        config = tomlkit.parse(codex.read_text())
        settings = json.loads(claude.read_text())
        self.assertEqual(config["model"], "machine-model")
        self.assertEqual(config["model_provider"], "private")
        self.assertEqual(config["model_reasoning_effort"], "high")
        self.assertEqual(config["model_providers"]["private"]["name"], "Private")
        self.assertEqual(config["model_providers"]["private"]["base_url"], "https://provider.example")
        self.assertEqual(config["mcp_servers"]["docs"]["command"], "docs-mcp")
        self.assertEqual(config["projects"]["/workspace/project"]["trust_level"], "trusted")
        self.assertEqual(config["personality"], "pragmatic")
        self.assertEqual(config["sandbox_mode"], "workspace-write")
        self.assertEqual(settings["model"], "machine-claude-model")
        self.assertEqual(settings["env"], {"PRIVATE_TOKEN": "keep"})
        self.assertEqual(settings["permissions"], {"allow": ["Read(*)"]})
        self.assertEqual(settings["hooks"], {"PreToolUse": [{"command": "keep-hook"}]})

    def test_second_run_is_byte_idempotent_and_creates_no_new_backup(self):
        self.install()
        files_before = self._snapshot(self.home)
        backup_root = self.home / ".local/share/claude-skills-backups"
        backups_before = sorted(backup_root.iterdir()) if backup_root.exists() else []
        self.install()
        self.assertEqual(files_before, self._snapshot(self.home))
        backups_after = sorted(backup_root.iterdir()) if backup_root.exists() else []
        self.assertEqual(backups_before, backups_after)

    def test_managed_blocks_update_without_removing_custom_content(self):
        claude_rules = self.home / ".claude/CLAUDE.md"
        claude_rules.parent.mkdir(parents=True)
        claude_rules.write_text(
            "custom before\n"
            f"{INSTALL.START}\nold managed text\n{INSTALL.END}\n"
            "custom after\n"
        )
        self.install()
        result = claude_rules.read_text()
        self.assertIn("custom before", result)
        self.assertIn("custom after", result)
        self.assertIn((ROOT / "config/CLAUDE.md").read_text(), result)
        self.assertNotIn("old managed text", result)

    def test_existing_skill_directory_is_backed_up_before_replacement(self):
        skill = self.skills[0]
        target = self.home / ".agents/skills" / skill.name
        target.mkdir(parents=True)
        (target / "user-file.txt").write_text("keep me")
        self.install()
        self.assertTrue(target.is_symlink())
        backup_root = self.home / ".local/share/claude-skills-backups"
        backups = list(backup_root.glob("*/.agents/skills/" + skill.name + "/user-file.txt"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_text(), "keep me")

    def test_dry_run_does_not_write_anything(self):
        self.install(dry_run=True)
        self.assertEqual(list(self.home.rglob("*")), [])

    def test_malformed_json_or_toml_is_rejected_without_resetting_files(self):
        cases = [
            (self.home / ".claude/settings.json", "{bad json", json.JSONDecodeError),
            (self.home / ".codex/config.toml", "[bad", Exception),
        ]
        for path, content, error in cases:
            with self.subTest(path=path):
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content)
                before = self._snapshot(self.home)
                with self.assertRaises(error):
                    self.install()
                self.assertEqual(path.read_text(), content)
                self.assertEqual(self._snapshot(self.home), before)

    def test_manager_runs_both_scripts_with_expected_working_directories_and_backups(self):
        checkout = self._manager_checkout()
        existing = [
            ".config/kitty/kitty.conf",
            ".claude/hooks/keep-hook",
            ".claude/settings.json",
            ".bashrc",
            ".zshrc",
            ".local/bin/codex",
            ".local/bin/qq",
            ".local/bin/claude-manager",
            ".local/bin/agent-terminals",
            ".local/bin/work-status",
        ]
        for name in existing:
            path = self.home / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("preserve")
            path.chmod(0o644)

        installer = INSTALL.Installer(self.home)
        with patch.object(INSTALL.shutil, "which", return_value="/usr/bin/fake"), patch.object(
            INSTALL.subprocess, "run"
        ) as run:
            INSTALL.install_manager(installer, checkout)

        self.assertEqual(
            run.call_args_list,
            [
                call(["bash", "install.sh"], cwd=checkout / "manager", env=ANY, check=True),
                call(
                    ["bash", "install.sh", "--full"],
                    cwd=checkout / "kitty-enhance",
                    env=ANY,
                    check=True,
                ),
            ],
        )
        env = run.call_args_list[0].kwargs["env"]
        self.assertTrue(env["PATH"].startswith(str(self.home / ".local/bin") + ":"))
        self.assertEqual((self.home / ".claude/settings.json").stat().st_mode & 0o777, 0o600)

        backup_dir = next((self.home / ".local/share/claude-skills-backups").iterdir())
        for name in existing:
            self.assertEqual((backup_dir / name).read_text(), "preserve")

    def test_manager_propagates_subprocess_failure(self):
        checkout = self._manager_checkout()
        failure = INSTALL.subprocess.CalledProcessError(7, ["bash", "install.sh"])
        installer = INSTALL.Installer(self.home)
        with patch.object(INSTALL.shutil, "which", return_value="/usr/bin/fake"), patch.object(
            INSTALL.subprocess, "run", side_effect=failure
        ) as run:
            with self.assertRaises(INSTALL.subprocess.CalledProcessError) as raised:
                INSTALL.install_manager(installer, checkout)
        self.assertIs(raised.exception, failure)
        self.assertEqual(run.call_count, 1)

    def test_link_does_not_replace_source_when_source_equals_target(self):
        source = self.home / ".claude/skills/example"
        source.mkdir(parents=True)
        marker = source / "SKILL.md"
        marker.write_text("skill content")
        installer = INSTALL.Installer(self.home)

        with patch.object(INSTALL, "REPO", source.parent):
            installer.link(source, source)

        self.assertTrue(source.is_dir())
        self.assertFalse(source.is_symlink())
        self.assertEqual(marker.read_text(), "skill content")
        backup_root = self.home / ".local/share/claude-skills-backups"
        self.assertFalse(backup_root.exists())

    def _manager_checkout(self):
        checkout = self.home / "manager-checkout"
        for script in ("manager/install.sh", "kitty-enhance/install.sh"):
            path = checkout / script
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("#!/bin/sh\nexit 0\n")
        return checkout

    @staticmethod
    def _snapshot(root):
        snapshot = {}
        for path in sorted(root.rglob("*")):
            relative = path.relative_to(root)
            if path.is_symlink():
                snapshot[str(relative)] = ("symlink", path.readlink().as_posix())
            elif path.is_file():
                snapshot[str(relative)] = ("file", path.read_bytes())
            else:
                snapshot[str(relative)] = ("dir", None)
        return snapshot


if __name__ == "__main__":
    unittest.main()
