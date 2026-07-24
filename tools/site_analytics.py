"""Shared Cloudflare Web Analytics beacon rendering and HTML injection."""

from __future__ import annotations

import json
import re


CLOUDFLARE_BEACON_SOURCE = "https://static.cloudflareinsights.com/beacon.min.js"
CLOUDFLARE_WEB_ANALYTICS_TOKEN = "2b712855303a44c2ab09217bf6703fe1"
TOKEN_PATTERN = re.compile(r"^[0-9a-f]{32}$")


def cloudflare_web_analytics_beacon(token: str) -> str:
    if not TOKEN_PATTERN.fullmatch(token):
        raise ValueError("Cloudflare Web Analytics token must be 32 lowercase hex characters")
    payload = json.dumps({"token": token}, separators=(",", ": "))
    return (
        "<!-- Cloudflare Web Analytics --><script type='module' "
        f"src='{CLOUDFLARE_BEACON_SOURCE}' data-cf-beacon='{payload}'></script>"
        "<!-- End Cloudflare Web Analytics -->"
    )


def inject_cloudflare_web_analytics(html: str, token: str) -> str:
    beacon = cloudflare_web_analytics_beacon(token)
    existing_count = html.count(CLOUDFLARE_BEACON_SOURCE)
    if existing_count:
        if existing_count == 1 and beacon in html:
            return html
        raise ValueError("HTML contains a conflicting Cloudflare Web Analytics beacon")
    if html.count("</body>") != 1:
        raise ValueError("HTML must contain exactly one closing body tag")
    newline = "\r\n" if "\r\n" in html else "\n"
    return html.replace("</body>", f"{beacon}{newline}</body>", 1)
