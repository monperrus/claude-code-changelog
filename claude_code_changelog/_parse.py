"""Parse the Mintlify markdown of the changelog page into per-version entries.

The page (served as markdown via ``Accept: text/markdown``) is a sequence of
``<Update label="VERSION" description="DATE">...</Update>`` blocks.
"""
from __future__ import annotations

import re
import textwrap
from dataclasses import dataclass

_UPDATE = re.compile(
    r'<Update\s+label="(?P<version>[^"]+)"\s+description="(?P<date>[^"]*)"[^>]*>'
    r"(?P<body>.*?)</Update>",
    re.DOTALL,
)
_TAG = re.compile(r"^\s*</?Expandable[^>]*>\s*$")
_EXPANDABLE = re.compile(r'<Expandable\s+title="([^"]*)"')
_VERSION = re.compile(r"^\d+(\.\d+)*([-.\w]*)$")


@dataclass(frozen=True)
class Release:
    version: str
    date: str
    body: str

    def to_markdown(self) -> str:
        return f"# {self.version}\n\n_{self.date}_\n\n{self.body}\n"


def _clean(body: str) -> str:
    """Dedent and turn <Expandable title="N bug fixes"> wrappers into headings."""
    out: list[str] = []
    for line in textwrap.dedent(body).strip("\n").splitlines():
        m = _EXPANDABLE.search(line)
        if m:
            out.append(f"**{m.group(1)}**")
        elif not _TAG.match(line):
            out.append(line)
    text = "\n".join(out)
    return re.sub(r"\n{3,}", "\n\n", textwrap.dedent(text)).strip()


def parse(markdown: str) -> list[Release]:
    """Return releases in page order (newest first). Raises if none are found."""
    releases = [
        Release(m["version"].strip(), m["date"].strip(), _clean(m["body"]))
        for m in _UPDATE.finditer(markdown)
        if _VERSION.match(m["version"].strip())
    ]
    if not releases:
        raise ValueError("no <Update> blocks found: page format changed?")
    return releases
