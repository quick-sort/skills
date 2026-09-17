#!/usr/bin/env python3
"""Re-sync vendored skill/plugin directories from their upstream repositories.

Mapping lives in upstream.json (next to this script).

Usage:
  scripts/sync.py            # sync all sources to latest upstream branch head
  scripts/sync.py --check    # only report whether upstream has moved past recorded sha
  scripts/sync.py <name>     # sync a single source (matched by repo URL substring)

Locally maintained, never synced: skills/architecture-diagram, skills/odoo-19,
skills/find-skills, plugins/n8n-mcp-skills/.claude-plugin/plugin.json,
plugins/plugin-dev/.claude-plugin/plugin.json
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
UPSTREAM_JSON = SCRIPT_DIR / "upstream.json"

SPARSE = {
    "anthropics/claude-code": ["plugins"],
    "anthropics/skills": ["skills"],
    "yang0/handraw-style": ["handdraw-style-prompter", "LICENSE", "README.md", "MANIFEST.md"],
}


def run(cmd, **kw):
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)


def main():
    check_only = "--check" in sys.argv
    filter_str = next((a for a in sys.argv[1:] if not a.startswith("-")), "")
    config = json.loads(UPSTREAM_JSON.read_text())
    sources = config["sources"]

    with tempfile.TemporaryDirectory(prefix="skills-sync.") as work:
        work = Path(work)
        changed = False
        for idx, src in enumerate(sources):
            repo, branch, sha = src["repo"], src["branch"], src["sha"]
            if filter_str and filter_str not in repo:
                continue
            print(f"==> {repo} (branch: {branch}, recorded: {sha[:12]})")

            clone = work / f"src{idx}"
            sparse_dirs = next((v for k, v in SPARSE.items() if k in repo), None)
            if sparse_dirs:
                run(["git", "clone", "-q", "--depth", "1", "--filter=blob:none",
                     "--sparse", "--branch", branch, repo, str(clone)])
                run(["git", "-C", str(clone), "sparse-checkout", "set", "--skip-checks"] + sparse_dirs)
            else:
                run(["git", "clone", "-q", "--depth", "1", "--branch", branch, repo, str(clone)])

            head = run(["git", "-C", str(clone), "rev-parse", "HEAD"]).stdout.strip()
            if head == sha:
                print("    up to date")
                continue
            if check_only:
                print(f"    UPDATE AVAILABLE: upstream {head[:12]} != recorded {sha[:12]}")
                continue

            for d in src["dirs"]:
                sub = clone / d["subdir"]
                dest = REPO_ROOT / d["dest"]
                exclude = set(d.get("exclude", []))
                renames = d.get("renames", {})

                if sub.is_file():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(sub, dest)
                    print(f"    copied file {d['subdir']} -> {d['dest']}")
                    continue

                if dest.exists() and not dest.is_dir():
                    raise SystemExit(f"dest is not a directory: {dest}")
                dest.mkdir(parents=True, exist_ok=True)
                for item in sub.iterdir():
                    if item.name in exclude:
                        continue
                    target = dest / renames.get(item.name, item.name)
                    if target.exists():
                        shutil.rmtree(target) if target.is_dir() else target.unlink()
                    if item.is_dir():
                        shutil.copytree(item, target, ignore=shutil.ignore_patterns(".DS_Store"))
                    else:
                        shutil.copy2(item, target)
                print(f"    synced {d['subdir']}/ -> {d['dest']}/")

            # Remove upstream-named dirs that were renamed locally
            for d in src["dirs"]:
                for old in d.get("renames", {}):
                    stale = REPO_ROOT / d["dest"] / old
                    if stale.exists():
                        shutil.rmtree(stale)
                        print(f"    removed stale renamed dir {d['dest']}/{old}")

            sources[idx]["sha"] = head
            changed = True
            print(f"    recorded new sha {head[:12]}")

    if changed and not check_only:
        UPSTREAM_JSON.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
        print("\nDone. Review with: git status && git diff --stat")
        print("Remember to update .claude-plugin/marketplace.json if upstream versions changed.")


if __name__ == "__main__":
    main()
