"""Unit tests for the shared Cloudflare Web Analytics beacon helper."""

from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
SOURCE_TEMPLATE = TOOLS / "jun_movelist_source_template.html"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import pipeline  # noqa: E402

from tools.site_analytics import (
    CLOUDFLARE_BEACON_SOURCE,
    cloudflare_web_analytics_beacon,
    inject_cloudflare_web_analytics,
)


TOKEN = "0123456789abcdef0123456789abcdef"


class SiteAnalyticsTest(unittest.TestCase):
    def test_beacon_matches_dashboard_module_snippet(self) -> None:
        self.assertEqual(
            cloudflare_web_analytics_beacon(TOKEN),
            "<!-- Cloudflare Web Analytics --><script type='module' "
            "src='https://static.cloudflareinsights.com/beacon.min.js' "
            "data-cf-beacon='"
            '{"token": "0123456789abcdef0123456789abcdef"}'
            "'></script><!-- End Cloudflare Web Analytics -->",
        )

    def test_injection_is_before_body_close_and_idempotent(self) -> None:
        original = "<!doctype html><body><main>content</main></body></html>"
        injected = inject_cloudflare_web_analytics(original, TOKEN)

        self.assertLess(injected.index(CLOUDFLARE_BEACON_SOURCE), injected.index("</body>"))
        self.assertEqual(injected.count(CLOUDFLARE_BEACON_SOURCE), 1)
        self.assertEqual(inject_cloudflare_web_analytics(injected, TOKEN), injected)

    def test_injection_rejects_invalid_token(self) -> None:
        for token in ("", "not-hex", "A" * 32, "a" * 31, "a" * 33):
            with self.subTest(token=token), self.assertRaises(ValueError):
                inject_cloudflare_web_analytics("<body></body>", token)

    def test_injection_rejects_conflicting_beacon(self) -> None:
        existing = (
            "<body><script type='module' "
            f'src="{CLOUDFLARE_BEACON_SOURCE}" '
            "data-cf-beacon='"
            '{"token":"ffffffffffffffffffffffffffffffff"}'
            "'></script></body>"
        )

        with self.assertRaises(ValueError):
            inject_cloudflare_web_analytics(existing, TOKEN)

    def test_injection_requires_body_close(self) -> None:
        with self.assertRaises(ValueError):
            inject_cloudflare_web_analytics("<html></html>", TOKEN)


class LegacyPipelineAnalyticsTest(unittest.TestCase):
    def test_crlf_conversion_and_analytics_reruns_are_byte_stable(self) -> None:
        with SOURCE_TEMPLATE.open(encoding="utf-8", newline="") as source_file:
            source = source_file.read().replace("\r\n", "\n")
        crlf_source = source.replace("\n", "\r\n")

        with tempfile.TemporaryDirectory() as tempdir:
            target = Path(tempdir) / pipeline.CONFIG["jun"]["file"]
            with target.open("w", encoding="utf-8", newline="") as target_file:
                target_file.write(crlf_source)

            with (
                mock.patch.object(pipeline, "SITE", tempdir),
                contextlib.redirect_stdout(io.StringIO()),
            ):
                pipeline.run("jun")
                converted = target.read_bytes()
                self.assertNotIn(b"\n", converted.replace(b"\r\n", b""))

                beacon = cloudflare_web_analytics_beacon(
                    pipeline.CLOUDFLARE_WEB_ANALYTICS_TOKEN
                ).encode("utf-8") + b"\r\n"
                target.write_bytes(converted.replace(beacon, b"", 1))
                pipeline.run("jun")
                reinjected = target.read_bytes()
                self.assertEqual(reinjected, converted)
                self.assertEqual(reinjected.count(CLOUDFLARE_BEACON_SOURCE.encode()), 1)

                pipeline.run("jun")
                self.assertEqual(target.read_bytes(), reinjected)


if __name__ == "__main__":
    unittest.main()
