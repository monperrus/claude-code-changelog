# claude-code-changelog

Mirror of the [Claude Code changelog](https://code.claude.com/docs/en/changelog),
one file per version in `versions/`. Updated automatically.

Source: the docs page served as markdown (`Accept: text/markdown`), parsed from its
`<Update label="VERSION" description="DATE">` blocks.

## Usage

    claude-code-changelog --to you@example.org --json

Writes `versions/<version>.md` for each unseen version, commits, pushes and emails
the new entries. The email starts with the full path of the script that sent it,
then an LLM-ranked list of the most important changes (`best-effort-completions.py
--tier medium`; omitted if every backend fails). Silent when nothing is new; the
first run seeds without email.
Options: `--repo`, `--dir`, `--no-push`, `--dry-run`, `--json`.

## Dev

    python -m venv .venv && .venv/bin/pip install -e '.[dev]' && .venv/bin/pytest
