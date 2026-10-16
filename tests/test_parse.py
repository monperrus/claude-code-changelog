from __future__ import annotations

import pytest

from claude_code_changelog._parse import parse

SAMPLE = """# Claude Code changelog

<Update label="2.1.2" description="October 15, 2026">
  **Added**

  * Added X

  <Expandable title="2 bug fixes">
    * Fixed Y
  </Expandable>
</Update>

<Update label="2.1.1" description="October 14, 2026">
  * Fixed Z
</Update>
"""


def test_parse_order_and_fields():
    rs = parse(SAMPLE)
    assert [r.version for r in rs] == ["2.1.2", "2.1.1"]
    assert rs[0].date == "October 15, 2026"
    assert "**2 bug fixes**" in rs[0].body and "<Expandable" not in rs[0].body
    assert rs[1].body == "* Fixed Z"


def test_no_blocks_raises():
    with pytest.raises(ValueError):
        parse("<html>changed</html>")


def test_bad_label_skipped():
    rs = parse(SAMPLE + '<Update label="../x" description="d">a</Update>')
    assert len(rs) == 2
