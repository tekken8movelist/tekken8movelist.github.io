# -*- coding: utf-8 -*-
"""docs/404.html -- what GitHub Pages serves for any path that does not exist.

Without one, a stale or mistyped link (an old bookmark, a forum post with a
typo, a crawler retrying a URL from before the locale trees) lands on GitHub's
generic page with no way back into the site. This one points at the three
hubs. It is served at whatever path was requested, so every link is a
full URL (the publication gate rejects root-relative ones); it carries
`noindex` and stays out of the sitemap.

    python tools/build_404.py
"""

from __future__ import annotations

import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
SITE = TOOLS.parent / "docs"
sys.path.insert(0, str(TOOLS))

from site_analytics import (  # noqa: E402
    CLOUDFLARE_WEB_ANALYTICS_TOKEN,
    inject_cloudflare_web_analytics,
)

PAGE = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>页面不存在 · Page not found｜TEKKEN 8 Move List</title>
<meta name="description" content="这个地址没有页面：链接可能已失效或拼写有误。从铁拳8全角色出招表重新选择角色，或前往繁體、English 版本。This page does not exist; pick a fighter from the TEKKEN 8 move list hub.">
<style>
:root{color-scheme:dark;--bg:#0e1116;--panel:#161c24;--ink:#dce3ea;--muted:#8b98a5;--line:#242c37;--acc:#6fb3ff}
*{box-sizing:border-box}
body{margin:0;min-height:100vh;display:flex;align-items:center;justify-content:center;
  padding:24px 16px;background:var(--bg);color:var(--ink);
  font-family:"Noto Sans SC","Microsoft YaHei",system-ui,sans-serif}
main{width:100%;max-width:520px;padding:28px 24px;border:1px solid var(--line);
  border-radius:12px;background:var(--panel);text-align:center}
.code{margin:0;color:var(--muted);font:700 13px/1 ui-monospace,Consolas,monospace;letter-spacing:4px}
h1{margin:12px 0 6px;font-size:22px}
p{margin:0 0 4px;color:var(--muted);font-size:14px;line-height:1.6}
nav{display:flex;flex-wrap:wrap;gap:10px;justify-content:center;margin-top:20px}
nav a{padding:8px 16px;border:1px solid var(--line);border-radius:999px;
  color:var(--ink);text-decoration:none;font-size:14px}
nav a:first-child{border-color:var(--acc);color:var(--acc)}
nav a:hover,nav a:focus-visible{border-color:var(--acc)}
</style>
</head>
<body>
<main>
  <p class="code">404</p>
  <h1>页面不存在</h1>
  <p>这个地址没有页面——链接可能已失效或拼写有误。</p>
  <p lang="en">This page does not exist. The link may be out of date or mistyped.</p>
  <nav aria-label="返回出招表 / Back to the move list">
    <a href="https://tekken8movelist.github.io/">全角色出招表</a>
    <a href="https://tekken8movelist.github.io/zh-Hant/" lang="zh-Hant">繁體版</a>
    <a href="https://tekken8movelist.github.io/en/" lang="en">English</a>
  </nav>
</main>
</body>
</html>
"""


def main() -> int:
    target = SITE / "404.html"
    html = inject_cloudflare_web_analytics(PAGE, CLOUDFLARE_WEB_ANALYTICS_TOKEN)
    current = target.read_text(encoding="utf-8") if target.is_file() else None
    if current != html:
        target.write_text(html, encoding="utf-8", newline="\n")
        print(f"built {target.relative_to(SITE.parent)}")
    else:
        print(f"unchanged {target.relative_to(SITE.parent)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
