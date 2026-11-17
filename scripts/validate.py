#!/usr/bin/env python3
"""Validate repository metadata and links without dependencies or network access."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import unquote, urlsplit


def contained_path(root: Path, value: str) -> Path:
    """Accept repository-relative paths only, including through symlinks."""
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError(f"invalid relative path: {value!r}")
    relative = PurePosixPath(value)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"unsafe relative path: {value!r}")
    path = (root / value).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError(f"path escapes repository: {value!r}")
    if not path.exists():
        raise ValueError(f"missing path: {value}")
    return path


def frontmatter(text: str) -> dict[str, str]:
    """Extract essential scalar fields; this is not a general YAML parser."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("SKILL.md must begin with frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("frontmatter closing delimiter missing") from exc
    fields: dict[str, str] = {}
    for index in range(1, end):
        match = re.match(r"^(name|description):\s*(.*)$", lines[index])
        if not match:
            continue
        key, value = match.groups()
        if key in fields:
            raise ValueError(f"duplicate frontmatter field: {key}")
        if value in {">", "|", ">-", "|-", ">+", "|+"}:
            continuation = []
            for line in lines[index + 1:end]:
                if line and not line[0].isspace():
                    break
                continuation.append(line.strip())
            value = " ".join(continuation).strip()
        elif value.startswith(('"', "'")):
            if len(value) < 2 or value[-1] != value[0]:
                raise ValueError(f"unclosed quoted frontmatter field: {key}")
            value = value[1:-1].strip()
        elif value.startswith(("[", "{", "&", "*", "!")):
            raise ValueError(f"frontmatter field must be a string scalar: {key}")
        else:
            value = re.split(r"\s+#", value, maxsplit=1)[0].rstrip()
            # YAML resolves unquoted booleans/numbers to non-string metadata.
            number = r"[-+]?(?:[0-9][0-9_]*|0x[0-9a-f_]+|0o[0-7_]+|0b[01_]+|" \
                     r"(?:[0-9][0-9_]*\.[0-9_]*|\.[0-9_]+)(?:e[-+]?[0-9]+)?|" \
                     r"[0-9][0-9_]*e[-+]?[0-9]+|[0-9][0-9_]*(?::[0-5]?[0-9])+(?:\.[0-9_]+)?|\.(?:inf|nan))"
            if value.lower() in {"true", "false", "yes", "no", "on", "off"} or re.fullmatch(number, value, re.I):
                raise ValueError(f"frontmatter field must be a string scalar: {key}")
            if value.lower() in {"null", "~"}:
                value = ""
        fields[key] = value
    for key in ("name", "description"):
        if not fields.get(key):
            raise ValueError(f"missing or empty frontmatter field: {key}")
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", fields["name"]):
        raise ValueError("skill name must contain lowercase words separated by hyphens")
    if len(fields["name"]) > 64 or len(fields["description"]) > 1024:
        raise ValueError("skill name or description exceeds Agent Skills limits")
    return fields


def without_fences(text: str) -> str:
    output = []
    fence = None
    for line in text.splitlines():
        marker = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if marker:
            token = marker.group(1)
            if fence is None:
                fence = token
            elif token[0] == fence[0] and len(token) >= len(fence):
                fence = None
            continue
        if fence is None:
            output.append(line)
    return "\n".join(output)


def heading_ids(text: str) -> set[str]:
    ids = set(re.findall(r'(?:id|name)=["\']([^"\']+)["\']', text))
    counts: dict[str, int] = {}
    for line in without_fences(text).splitlines():
        match = re.match(r"^\s{0,3}#{1,6}\s+(.+?)(?:\s+#+)?$", line)
        if not match:
            continue
        heading = re.sub(r"<[^>]*>", "", match.group(1)).lower()
        slug = re.sub(r"[^\w\- ]", "", heading, flags=re.UNICODE).replace(" ", "-")
        count = counts.get(slug, 0)
        counts[slug] = count + 1
        ids.add(f"{slug}-{count}" if count else slug)
    return ids


def markdown_links(root: Path, source: Path) -> list[str]:
    text = without_fences(source.read_text(encoding="utf-8"))
    targets = re.findall(r"!?\[[^\]\n]*\]\((<[^>]+>|[^\s()]+)(?:\s+[^)]*)?\)", text)
    targets += re.findall(r"^\s{0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)", text, re.MULTILINE)
    errors = []
    for target in targets:
        target = target.strip("<>")
        parsed = urlsplit(target)
        if parsed.scheme or parsed.netloc:
            continue
        path = (source.parent / unquote(parsed.path)).resolve() if parsed.path else source
        label = str(source.relative_to(root))
        if not path.is_relative_to(root):
            errors.append(f"{label}: link escapes repository: {target}")
        elif not path.exists():
            errors.append(f"{label}: missing link target: {target}")
        elif parsed.fragment and path.is_file() and path.suffix.lower() == ".md":
            if unquote(parsed.fragment) not in heading_ids(path.read_text(encoding="utf-8")):
                errors.append(f"{label}: missing heading anchor: {target}")
    return errors


def validate(root: Path) -> list[str]:
    root = root.resolve()
    errors: list[str] = []
    manifests = {}
    for relative in (".codex-plugin/plugin.json", ".claude-plugin/plugin.json",
                     "marketplace.json", ".claude-plugin/marketplace.json"):
        try:
            value = json.loads((root / relative).read_text(encoding="utf-8"))
            if not isinstance(value, dict):
                raise ValueError("manifest must be a JSON object")
            manifests[relative] = value
        except (OSError, ValueError) as exc:
            errors.append(f"{relative}: {exc}")
    plugins = [manifests.get(path, {}) for path in
               (".codex-plugin/plugin.json", ".claude-plugin/plugin.json")]
    for plugin in plugins:
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", str(plugin.get("name", ""))):
            errors.append("plugin name is missing or invalid")
        if not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?",
                            str(plugin.get("version", ""))):
            errors.append("plugin version must be a semantic version")
        entries = plugin.get("skills", [])
        if isinstance(entries, str):
            entries = [entries]
        if not isinstance(entries, list) or not entries:
            errors.append("plugin skills must be a path or nonempty path list")
            continue
        for entry in entries:
            try:
                skill_path = contained_path(root, entry)
                if not skill_path.is_dir() or not any(skill_path.rglob("SKILL.md")):
                    raise ValueError(f"no skills in manifest path: {entry}")
            except (ValueError, TypeError) as exc:
                errors.append(str(exc))
    if (plugins[0].get("name"), plugins[0].get("version")) != (
            plugins[1].get("name"), plugins[1].get("version")):
        errors.append("Codex and Claude plugin names/versions differ")
    for relative in ("marketplace.json", ".claude-plugin/marketplace.json"):
        if relative not in manifests:
            continue
        catalog = manifests[relative]
        if not isinstance(catalog.get("name"), str) or not catalog["name"]:
            errors.append(f"{relative}: marketplace name missing")
        entries = catalog.get("plugins")
        if not isinstance(entries, list) or not entries:
            errors.append(f"{relative}: plugins must be a nonempty list")
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                errors.append(f"{relative}: plugin entry must be an object")
                continue
            if entry.get("name") != plugins[0].get("name"):
                errors.append(f"{relative}: plugin name does not match manifest")
            source = entry.get("source")
            if isinstance(source, dict):
                if source.get("source") != "local":
                    errors.append(f"{relative}: expected local plugin source")
                source = source.get("path")
            try:
                contained_path(root, source)
            except (ValueError, TypeError) as exc:
                errors.append(f"{relative}: {exc}")
    skill_files = sorted((root / "skills").glob("*/SKILL.md"))
    if not skill_files:
        errors.append("no skills found")
    names = set()
    for path in skill_files:
        try:
            if not path.resolve().is_relative_to(root):
                raise ValueError("skill path escapes repository through a symlink")
            text = path.read_text(encoding="utf-8")
            fields = frontmatter(text)
            if fields["name"] != path.parent.name:
                raise ValueError("skill name differs from directory name")
            if fields["name"] in names:
                raise ValueError("duplicate skill name")
            names.add(fields["name"])
            if path.parent.name == "devops-operations":
                for document in path.parent.rglob("*.md"):
                    if not document.resolve().is_relative_to(root):
                        errors.append(f"{document.relative_to(root)}: Markdown path escapes repository through a symlink")
                        continue
                    if re.search(r"\b(?:TODO|TBD|FIXME)\b|\[Your [^\]]+\]|Main logic here|Scenario 1|Tool 1:",
                                 document.read_text(encoding="utf-8")):
                        errors.append(f"{document.relative_to(root)}: unfinished placeholder content")
        except (OSError, ValueError) as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
    for path in sorted(root.rglob("*.md")):
        if any(part in {".git", "node_modules", ".venv"} for part in path.relative_to(root).parts):
            continue
        try:
            if not path.resolve().is_relative_to(root):
                raise ValueError("Markdown path escapes repository through a symlink")
            errors.extend(markdown_links(root, path))
        except (OSError, ValueError) as exc:
            errors.append(f"{path.relative_to(root)}: {exc}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.root)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Repository metadata, skill frontmatter, and local Markdown links are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
