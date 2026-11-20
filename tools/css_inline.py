# -*- coding: utf-8 -*-
"""Shared stylesheets, minus their comments, as they are inlined into pages.

The shared CSS files carry their design rationale as comments -- why a
column is 9%, which contrast ratio a colour was chosen against -- and that is
where it belongs. But every character page inlines those files, and the
comments came to 19 KB of a 44 KB stylesheet: measured 2026-11-19, a page
went from 29 KB to 20 KB gzipped without them, on every one of 129 pages.
Lighthouse flagged it as "Minify CSS".

Only comments go; rules, whitespace and order are untouched, so a page reads
the same in devtools. None of the sources has a comment marker inside a
string or url() (checked when this was written; a stray one would leave the
open and close counts unequal, which `strip_css_comments` refuses).
"""

from __future__ import annotations

import re

COMMENT = re.compile(r"/\*.*?\*/", re.S)
# the blank lines a removed block comment leaves behind
EMPTY_LINES = re.compile(r"\n(?:[ \t]*\n)+")


def strip_css_comments(css: str) -> str:
    if css.count("/*") != css.count("*/"):
        raise ValueError("unbalanced CSS comment markers; is one inside a string?")
    return EMPTY_LINES.sub("\n", COMMENT.sub("", css))
