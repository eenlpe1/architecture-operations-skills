#!/usr/bin/env python3
"""Share this checkout's skills across local Codex, Claude, and Antigravity."""

import argparse
import copy
import json
import os
from pathlib import Path
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]


def skill_dirs(directory):
    if not directory.exists():
        return {}
    return {
        path.name: path
        for path in sorted(directory.iterdir())
        if not path.name.startswith(".") and (path / "SKILL.md").is_file()
    }


def check_parent(directory):
    for path in (directory, *directory.parents):
        if path.is_symlink() and not path.exists():
            raise ValueError(f"Broken directory link: {path}")
        if path.exists() and not path.is_dir():
            raise ValueError(f"Expected a directory: {path}")


def expected_link(destination, source, missing, canonical=None):
    target = (canonical or source).resolve()
    physical = destination.parent.resolve() / destination.name
    if physical in missing:
        if missing[physical][2] != target:
            raise ValueError(f"Conflicting planned skill target: {destination}")
        return
    if destination.exists() and destination.resolve() == target:
        return
    if destination.exists() or destination.is_symlink():
        raise ValueError(f"Conflicting skill path: {destination}; move it aside explicitly before installing")
    missing[physical] = (destination, source, target)


def manifest_for(home, shared, manifest, canonical_skills):
    if manifest.is_symlink():
        raise ValueError(f"Refusing to replace a symlinked manifest: {manifest}")
    old = manifest.read_bytes() if manifest.exists() else None
    data = json.loads(old) if old is not None else {"entries": []}
    if not isinstance(data, dict) or not isinstance(data.get("entries", []), list):
        raise ValueError("Antigravity skills.json must be an object with an entries array")
    updated = copy.deepcopy(data)
    entries = updated.setdefault("entries", [])
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str):
            raise ValueError("Each Antigravity skill entry must have a string path")
        path = entry["path"]
        if path == "~" or path.startswith("~/"):
            entry["path"] = str(home / path[2:]) if path != "~" else str(home)
    aliases = {home / ".gemini/config/skills", home / ".claude/skills"}
    retained = []
    for entry in entries:
        directory = Path(entry["path"])
        discovered = skill_dirs(directory) if directory in aliases else {}
        entirely_shared = all(
            name in canonical_skills and source.resolve() == canonical_skills[name].resolve()
            for name, source in discovered.items()
        )
        if directory in aliases and directory.exists():
            entirely_shared = entirely_shared and not any(
                path.parent.parent != directory for path in directory.rglob("SKILL.md")
            )
        # Collapse only unfiltered, known alias directories; preserve custom discovery.
        if directory in aliases and set(entry) == {"path"} and entirely_shared:
            continue
        retained.append(entry)
    updated["entries"] = entries = retained
    if not any(entry["path"] == str(shared) and not entry.get("exclude") and not entry.get("include_only") for entry in entries):
        entries.append({"path": str(shared)})
    return old, updated, updated != data


def write_manifest(manifest, content, old):
    manifest.parent.mkdir(parents=True, exist_ok=True)
    if old is not None:
        with tempfile.NamedTemporaryFile(prefix="skills.json.backup-", dir=manifest.parent, delete=False) as backup:
            backup.write(old)
            backup.flush()
            os.fsync(backup.fileno())
        print(f"Private manifest backup: {backup.name}")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=".skills-", dir=manifest.parent, delete=False) as handle:
            temporary = Path(handle.name)
            handle.write((json.dumps(content, indent=2) + "\n").encode())
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, manifest)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def install(home, check=False):
    home = home.expanduser().resolve()
    shared = home / ".agents/skills"
    claude = home / ".claude/skills"
    manifest = home / ".gemini/config/skills.json"
    for directory in (shared, claude, manifest.parent):
        check_parent(directory)
    sources = skill_dirs(ROOT / "skills")
    if not sources:
        raise ValueError(f"No canonical skills found under {ROOT / 'skills'}")
    missing = {}
    for name, source in sources.items():
        expected_link(shared / name, source, missing)
    all_skills = skill_dirs(shared)
    all_skills.update({name: shared / name for name in sources})
    for name, source in all_skills.items():
        # A planned shared link does not exist yet; compare against its canonical target.
        expected_link(claude / name, source, missing, sources.get(name))
    canonical_skills = {name: sources.get(name, source) for name, source in all_skills.items()}
    old, updated, changed = manifest_for(home, shared, manifest, canonical_skills)
    if check:
        for destination, _, _ in missing.values():
            print(f"Missing skill link: {destination}", file=sys.stderr)
        if changed or old is None:
            print(f"Antigravity discovery needs update: {manifest}", file=sys.stderr)
        if missing or changed or old is None:
            return 1
        print(f"Global discovery verified for {len(all_skills)} shared skills.")
        return 0
    # Preflight every conflict and parse the configuration before changing any paths.
    for destination, source, _ in missing.values():
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.symlink_to(source.resolve(), target_is_directory=True)
    if changed or old is None:
        write_manifest(manifest, updated, old)
    print(f"Global discovery configured for {len(all_skills)} shared skills; {len(missing)} links added.")
    print("Restart your clients. Rerun this installer after adding shared skills.")
    return 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Verify discovery without changing files")
    parser.add_argument("--home", type=Path, default=Path.home(), help="Alternate home directory for isolated tests")
    args = parser.parse_args()
    try:
        return install(args.home, args.check)
    except (OSError, ValueError) as error:
        print(f"Global skill setup failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
