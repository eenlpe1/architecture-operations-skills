"""Exercise validation failures against disposable repositories."""

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "validate_repository", Path(__file__).resolve().parents[1] / "scripts" / "validate.py"
)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class RepositoryValidationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        for directory in (".codex-plugin", ".claude-plugin", "skills/devops-operations"):
            (self.root / directory).mkdir(parents=True)
        self.skill = self.root / "skills/devops-operations/SKILL.md"
        self.skill.write_text(
            "---\nname: devops-operations\ndescription: >-\n"
            "  Diagnose failed operational workflows using evidence.\n---\n\n"
            "# Operations\n\nRead [the guide](guide.md#recover-a-service).\n"
        )
        (self.skill.parent / "guide.md").write_text("# Recover a service\n\nUse verified evidence.\n")
        self.plugin = {"name": "example", "version": "1.2.3", "skills": "./skills/"}
        for relative in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json"):
            self.write_json(relative, self.plugin)
        self.write_json("marketplace.json", {
            "name": "example-author", "plugins": [{"name": "example", "source": {"source": "local", "path": "."}}]
        })
        self.write_json(".claude-plugin/marketplace.json", {
            "name": "example-author", "plugins": [{"name": "example", "source": "./"}]
        })

    def write_json(self, relative, value):
        (self.root / relative).write_text(json.dumps(value))

    def errors(self):
        return "\n".join(VALIDATOR.validate(self.root))

    def test_valid_repository_including_folded_description_and_anchor(self):
        self.assertEqual(self.errors(), "")

    def test_manifest_parent_traversal_is_rejected_even_if_target_exists(self):
        self.write_json(".codex-plugin/plugin.json", {**self.plugin, "skills": "../"})
        self.assertIn("unsafe relative path", self.errors())

    def test_manifest_absolute_path_is_rejected(self):
        self.write_json(".codex-plugin/plugin.json", {**self.plugin, "skills": str(self.root / "skills")})
        self.assertIn("unsafe relative path", self.errors())

    def test_manifest_symlink_cannot_escape_repository(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.root / "outside").symlink_to(outside, target_is_directory=True)
            self.write_json(".codex-plugin/plugin.json", {**self.plugin, "skills": "outside"})
            self.assertIn("path escapes repository", self.errors())

    def test_malformed_manifest_types_report_errors_instead_of_crashing(self):
        self.write_json(".codex-plugin/plugin.json", [])
        self.write_json(".claude-plugin/marketplace.json", {"plugins": ["not-an-object"]})
        self.assertIn("manifest must be a JSON object", self.errors())
        self.assertIn("plugin entry must be an object", self.errors())

    def test_plugin_version_and_name_mismatch(self):
        self.write_json(".claude-plugin/plugin.json", {**self.plugin, "version": "1.2.4", "name": "different"})
        self.assertIn("names/versions differ", self.errors())

    def test_missing_frontmatter_and_unterminated_frontmatter(self):
        for content, expected in (("# No metadata", "must begin with frontmatter"),
                                  ("---\nname: devops-operations\n", "closing delimiter missing")):
            with self.subTest(content=content):
                self.skill.write_text(content)
                self.assertIn(expected, self.errors())

    def test_missing_description_and_duplicate_name(self):
        for metadata, expected in (("name: devops-operations", "field: description"),
                                   ("name: devops-operations\nname: another\ndescription: Diagnose", "duplicate frontmatter")):
            with self.subTest(metadata=metadata):
                self.skill.write_text(f"---\n{metadata}\n---\n# Operations\n")
                self.assertIn(expected, self.errors())

    def test_frontmatter_description_cannot_be_a_collection(self):
        self.skill.write_text("---\nname: devops-operations\ndescription: [not, text]\n---\n")
        self.assertIn("must be a string scalar", self.errors())

    def test_frontmatter_plain_booleans_and_numbers_are_not_strings(self):
        for field in ("name", "description"):
            for value in ("true", "FALSE", "yes", "off", "42", "-1.5", "1e3",
                          "0x2a", "0o52", "0b101010", ".inf", ".NaN", "42 # a comment"):
                with self.subTest(field=field, value=value):
                    fields = {"name": "example", "description": "Investigate failures."}
                    fields[field] = value
                    text = "---\n" + "\n".join(f"{key}: {item}" for key, item in fields.items()) + "\n---\n"
                    with self.assertRaisesRegex(ValueError, "must be a string scalar"):
                        VALIDATOR.frontmatter(text)

    def test_frontmatter_quoted_and_block_values_remain_strings(self):
        for value in ("true", "42", "null", "~"):
            for encoded in (f'"{value}"', f"'{value}'", f"|-\n  {value}", f">-\n  {value}"):
                with self.subTest(encoded=encoded):
                    fields = VALIDATOR.frontmatter(f"---\nname: example\ndescription: {encoded}\n---\n")
                    self.assertEqual(fields["description"], value)
        for value in ("true", "42", "null"):
            fields = VALIDATOR.frontmatter(f'---\nname: "{value}"\ndescription: Investigate failures.\n---\n')
            self.assertEqual(fields["name"], value)

    def test_escaped_reference_is_rejected_before_placeholder_scan_reads_it(self):
        with tempfile.TemporaryDirectory() as outside:
            external = Path(outside) / "private.md"
            external.write_text("TODO: private content must not be examined.\n")
            (self.skill.parent / "escaped.md").symlink_to(external)
            original_read = Path.read_text

            def guarded_read(path, *args, **kwargs):
                if path.resolve() == external:
                    raise AssertionError("validator read an escaped reference")
                return original_read(path, *args, **kwargs)

            with patch.object(Path, "read_text", guarded_read):
                errors = self.errors()
            self.assertIn("Markdown path escapes repository", errors)
            self.assertNotIn("unfinished placeholder", errors)

    def test_skill_symlink_cannot_escape_the_declared_skill_directory(self):
        with tempfile.TemporaryDirectory() as outside:
            external = Path(outside) / "SKILL.md"
            external.write_text("---\nname: external\ndescription: External instruction.\n---\n")
            (self.root / "skills/external").symlink_to(outside, target_is_directory=True)
            self.assertIn("skill path escapes repository", self.errors())

    def test_missing_reference_and_missing_anchor(self):
        self.skill.write_text(self.skill.read_text() + "\n[Missing](absent.md)\n[Wrong section](guide.md#absent)\n")
        self.assertIn("missing link target", self.errors())
        self.assertIn("missing heading anchor", self.errors())

    def test_external_links_and_fenced_example_links_are_not_fetched_or_checked(self):
        self.skill.write_text(self.skill.read_text() +
                              "\n[Remote](https://invalid.example/not-fetched)\n"
                              "```markdown\n[Example](not-real.md)\n```\n")
        self.assertEqual(self.errors(), "")

    def test_placeholder_checks_apply_only_to_new_operations_skill(self):
        (self.root / "README.md").write_text("Historical example: TODO.\n")
        self.assertEqual(self.errors(), "")
        (self.skill.parent / "guide.md").write_text("# Recover a service\n\nTODO\n")
        self.assertIn("unfinished placeholder", self.errors())


if __name__ == "__main__":
    unittest.main()
