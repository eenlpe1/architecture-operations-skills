import importlib.util
import json
from pathlib import Path
import stat
import tempfile
import unittest


SPEC = importlib.util.spec_from_file_location(
    "install_global", Path(__file__).resolve().parents[1] / "scripts/install-global.py"
)
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


class GlobalInstallerTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.home = self.base / "home"
        self.home.mkdir()
        self.repo = self.base / "repo"
        self.skill(self.repo / "skills/devops-operations")
        original = installer.ROOT
        installer.ROOT = self.repo
        self.addCleanup(setattr, installer, "ROOT", original)
        self.shared = self.home / ".agents/skills"
        self.claude = self.home / ".claude/skills"
        self.manifest = self.home / ".gemini/config/skills.json"

    def skill(self, directory):
        directory.mkdir(parents=True)
        (directory / "SKILL.md").write_text("---\nname: example\ndescription: Test skill\n---\n")

    def manifest_data(self, data):
        self.manifest.parent.mkdir(parents=True, exist_ok=True)
        self.manifest.write_text(json.dumps(data))
        return self.manifest.read_bytes()

    def test_shared_library_and_idempotent_install(self):
        self.skill(self.shared / "existing")
        self.assertEqual(installer.install(self.home), 0)
        self.assertEqual((self.shared / "devops-operations").resolve(), self.repo / "skills/devops-operations")
        self.assertEqual((self.claude / "existing").resolve(), self.shared / "existing")
        self.assertEqual((self.claude / "devops-operations").readlink(), self.repo / "skills/devops-operations")
        before = self.manifest.stat().st_mtime_ns
        self.assertEqual(installer.install(self.home), 0)
        self.assertEqual(installer.install(self.home, check=True), 0)
        self.assertEqual(self.manifest.stat().st_mtime_ns, before)
        self.assertEqual(list(self.manifest.parent.glob("skills.json.backup-*")), [])

    def test_check_is_read_only_and_detects_missing_setup(self):
        self.assertEqual(installer.install(self.home, check=True), 1)
        self.assertEqual(list(self.home.iterdir()), [])

    def test_preflight_conflict_preserves_everything(self):
        self.skill(self.claude / "devops-operations")
        original = self.manifest_data({"entries": [], "custom": True})
        with self.assertRaisesRegex(ValueError, "Conflicting skill path"):
            installer.install(self.home)
        self.assertFalse(self.shared.exists())
        self.assertEqual(self.manifest.read_bytes(), original)

    def test_claude_directory_alias_deduplicates_physical_destinations(self):
        self.skill(self.shared / "existing")
        self.claude.parent.mkdir(parents=True)
        self.claude.symlink_to(self.shared, target_is_directory=True)
        self.assertEqual(installer.install(self.home, check=True), 1)
        self.assertFalse((self.shared / "devops-operations").exists())
        self.assertFalse(self.manifest.exists())
        self.assertEqual(installer.install(self.home), 0)
        self.assertTrue(self.claude.is_symlink())
        self.assertEqual((self.claude / "devops-operations").resolve(), self.repo / "skills/devops-operations")
        self.assertFalse((self.shared / "existing").is_symlink())
        self.assertEqual(installer.install(self.home), 0)
        self.assertEqual(installer.install(self.home, check=True), 0)

    def test_wrong_link_in_aliased_directory_still_fails_preflight(self):
        self.shared.mkdir(parents=True)
        wrong = self.base / "wrong"
        self.skill(wrong)
        (self.shared / "devops-operations").symlink_to(wrong, target_is_directory=True)
        self.claude.parent.mkdir(parents=True)
        self.claude.symlink_to(self.shared, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "Conflicting skill path"):
            installer.install(self.home)
        self.assertEqual((self.shared / "devops-operations").resolve(), wrong)
        self.assertFalse(self.manifest.exists())

    def test_invalid_json_is_not_replaced_and_creates_no_links(self):
        self.manifest.parent.mkdir(parents=True)
        self.manifest.write_text("{invalid")
        with self.assertRaises(ValueError):
            installer.install(self.home)
        self.assertFalse(self.shared.exists())
        self.assertEqual(self.manifest.read_text(), "{invalid")

    def test_aliases_collapse_but_filters_and_unrelated_settings_survive(self):
        self.skill(self.shared / "existing")
        aliases = self.home / ".gemini/config/skills"
        aliases.mkdir(parents=True)
        (aliases / "existing").symlink_to(self.shared / "existing", target_is_directory=True)
        original = self.manifest_data({
            "entries": [
                {"path": "~/.gemini/config/skills"},
                {"path": "~/.claude/skills"},
                {"path": "~/.codex/skills"},
                {"path": "~/external", "exclude": ["private"]},
                {"path": "~/.claude/skills", "include_only": ["existing"]},
            ],
            "custom": {"enabled": True},
        })
        installer.install(self.home)
        data = json.loads(self.manifest.read_text())
        self.assertEqual(data["custom"], {"enabled": True})
        self.assertEqual(data["entries"], [
            {"path": str(self.home / ".codex/skills")},
            {"path": str(self.home / "external"), "exclude": ["private"]},
            {"path": str(self.claude), "include_only": ["existing"]},
            {"path": str(self.shared)},
        ])
        backups = list(self.manifest.parent.glob("skills.json.backup-*"))
        self.assertEqual(len(backups), 1)
        self.assertEqual(backups[0].read_bytes(), original)
        self.assertEqual(stat.S_IMODE(backups[0].stat().st_mode), 0o600)
        installer.install(self.home)
        self.assertEqual(len(list(self.manifest.parent.glob("skills.json.backup-*"))), 1)

    def test_alias_directory_with_unrelated_skill_is_preserved(self):
        self.skill(self.home / ".gemini/config/skills/unrelated")
        self.manifest_data({"entries": [{"path": "~/.gemini/config/skills"}]})
        installer.install(self.home)
        entries = json.loads(self.manifest.read_text())["entries"]
        self.assertIn({"path": str(self.home / ".gemini/config/skills")}, entries)

    def test_nested_unrelated_skill_keeps_alias_discovery(self):
        self.skill(self.home / ".gemini/config/skills/team/unrelated")
        self.manifest_data({"entries": [{"path": "~/.gemini/config/skills"}]})
        installer.install(self.home)
        entries = json.loads(self.manifest.read_text())["entries"]
        self.assertIn({"path": str(self.home / ".gemini/config/skills")}, entries)

    def test_new_shared_skills_are_linked_on_rerun(self):
        installer.install(self.home)
        self.skill(self.shared / "new-skill")
        self.assertEqual(installer.install(self.home, check=True), 1)
        installer.install(self.home)
        self.assertEqual((self.claude / "new-skill").resolve(), self.shared / "new-skill")
        self.assertEqual(installer.install(self.home, check=True), 0)

    def test_symlinked_manifest_is_rejected_without_changes(self):
        external = self.base / "external.json"
        external.write_text('{"entries": []}')
        self.manifest.parent.mkdir(parents=True)
        self.manifest.symlink_to(external)
        with self.assertRaisesRegex(ValueError, "symlinked manifest"):
            installer.install(self.home)
        self.assertFalse(self.shared.exists())
        self.assertEqual(external.read_text(), '{"entries": []}')


if __name__ == "__main__":
    unittest.main()
