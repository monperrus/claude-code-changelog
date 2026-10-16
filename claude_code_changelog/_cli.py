"""Fetch the changelog, write new versions to files, commit, push and email them.

Silent when nothing is new. The first run (empty versions dir) seeds the files
without emailing.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.request
from pathlib import Path

from ._parse import Release, parse

URL = "https://code.claude.com/docs/en/changelog"
AUTHOR = "Martin Monperrus (AI-assisted) <martin.monperrus+ai@gnieh.org>"


def fetch(url: str = URL) -> str:
    req = urllib.request.Request(
        url, headers={"Accept": "text/markdown", "User-Agent": "claude-code-changelog"}
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read().decode()


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), *args], check=True, capture_output=True, text=True
    ).stdout


def new_releases(releases: list[Release], vdir: Path) -> list[Release]:
    return [r for r in releases if not (vdir / f"{r.version}.md").exists()]


def send_mail(to: str, new: list[Release]) -> None:
    newest = new[0].version
    subject = f"Claude Code {newest} changelog"
    if len(new) > 1:
        subject = f"Claude Code changelog: {len(new)} new versions ({newest})"
    body = "\n\n---\n\n".join(r.to_markdown() for r in new)
    subprocess.run(
        ["kuzymail", "send", "--to", to, "--subject", subject, "--markdown-stdin"],
        input=body, text=True, check=True, capture_output=True,
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        prog="claude-code-changelog", description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--repo", type=Path, default=Path.cwd(), help="git repo to write into")
    p.add_argument("--dir", default="versions", help="subdir holding one file per version")
    p.add_argument("--url", default=URL)
    p.add_argument("--to", help="email recipient for new versions (omit: no email)")
    p.add_argument("--no-push", action="store_true")
    p.add_argument("--dry-run", action="store_true", help="report only, change nothing")
    p.add_argument("--json", action="store_true", help="print a JSON report when something is new")
    a = p.parse_args(argv)

    releases = parse(fetch(a.url))
    vdir = a.repo / a.dir
    seeding = not vdir.exists() or not any(vdir.glob("*.md"))
    new = new_releases(releases, vdir)
    if not new:
        return 0
    if not a.dry_run:
        vdir.mkdir(parents=True, exist_ok=True)
        for r in new:
            (vdir / f"{r.version}.md").write_text(r.to_markdown())
        _git(a.repo, "add", a.dir)
        msg = f"Add {new[0].version}" if len(new) == 1 else f"Add {len(new)} versions ({new[-1].version}..{new[0].version})"
        _git(a.repo, "-c", f"user.name={AUTHOR.split(' <')[0]}",
             "-c", f"user.email={AUTHOR.split('<')[1][:-1]}", "commit", "-q", "-m", msg)
        if not a.no_push:
            _git(a.repo, "push", "-q")
        if a.to and not seeding:
            send_mail(a.to, new)
    if a.json:
        print(json.dumps({"new": [r.version for r in new], "seeded": seeding, "dry_run": a.dry_run}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
