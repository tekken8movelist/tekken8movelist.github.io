"""Derive a character-coloured surface that white text can actually sit on.

Every character page paints white text on its own accent: the section headings
(`h2`) and the title band. The 41 accents were chosen to read as accents on a
dark page, so they are pale by design -- white on them ranges from 3.2:1 down
to 1.2:1, i.e. from "hard" to "invisible" (Panda's #e6e9ee).

Rather than repaint 41 palettes, deepen the accent towards its own ink until
white clears WCAG AA, and use that as the surface colour. Each character keeps
as much of its own colour as contrast allows -- a deep purple gives most of it
back, a near-white gives up nearly all of it.

Both page families call this, so the guarantee holds for all 41 pages and can
be asserted at build time instead of hoped for in CSS.
"""

from __future__ import annotations

# WCAG 2 contrast for normal text. The headings are 13px bold, which is below
# the 18.66px the spec lets off at 3:1, so the full 4.5 applies.
AA_NORMAL_TEXT = 4.5
WHITE = "#ffffff"


def _channels(color: str) -> tuple[int, int, int]:
    value = color.lstrip("#")
    if len(value) == 3:
        value = "".join(channel * 2 for channel in value)
    if len(value) != 6:
        raise ValueError(f"not a hex colour: {color}")
    return tuple(int(value[i : i + 2], 16) for i in (0, 2, 4))


def relative_luminance(color: str) -> float:
    def linear(channel: int) -> float:
        srgb = channel / 255
        return srgb / 12.92 if srgb <= 0.03928 else ((srgb + 0.055) / 1.055) ** 2.4

    red, green, blue = (linear(channel) for channel in _channels(color))
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def contrast_ratio(one: str, other: str) -> float:
    first, second = relative_luminance(one), relative_luminance(other)
    lighter, darker = max(first, second), min(first, second)
    return (lighter + 0.05) / (darker + 0.05)


def mix(color: str, toward: str, fraction: float) -> str:
    """`fraction` of `color`, the rest `toward` -- sRGB, like CSS color-mix."""
    left, right = _channels(color), _channels(toward)
    blended = (
        round(left[i] * fraction + right[i] * (1 - fraction)) for i in range(3)
    )
    return "#" + "".join(f"{channel:02x}" for channel in blended)


def band_color(accent: str, ink: str, minimum: float = AA_NORMAL_TEXT) -> str:
    """The most accent-preserving mix of `accent` into `ink` white can sit on.

    Searched in 1% steps from all-accent downwards, so a character whose accent
    is already dark enough keeps it unchanged.
    """
    if contrast_ratio(WHITE, ink) < minimum:
        raise ValueError(
            f"ink {ink} is itself too light for white text "
            f"({contrast_ratio(WHITE, ink):.2f}:1); no mix can reach {minimum}:1"
        )
    for step in range(100, -1, -1):
        candidate = mix(accent, ink, step / 100)
        if contrast_ratio(WHITE, candidate) >= minimum:
            return candidate
    return ink  # unreachable: the guard above proves step 0 qualifies
