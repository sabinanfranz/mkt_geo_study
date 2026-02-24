"""UI code-block readability and contrast tests."""

from __future__ import annotations

import re
from pathlib import Path


CSS_PATH = Path(__file__).resolve().parent.parent / "apps" / "web" / "css" / "style.css"
VAR_RE = re.compile(r"(--[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{3,6})\s*;")


def _read_css() -> str:
    assert CSS_PATH.exists(), f"CSS file not found: {CSS_PATH}"
    return CSS_PATH.read_text(encoding="utf-8")


def _extract_var_block(css: str, selector: str) -> dict[str, str]:
    pattern = re.compile(re.escape(selector) + r"\s*\{(?P<body>.*?)\}", re.DOTALL)
    match = pattern.search(css)
    assert match, f"Selector block not found: {selector}"
    body = match.group("body")
    vars_map = {name: value for name, value in VAR_RE.findall(body)}
    assert vars_map, f"No CSS variables found in: {selector}"
    return vars_map


def _hex_to_rgb(value: str) -> tuple[float, float, float]:
    value = value.strip().lstrip("#")
    if len(value) == 3:
        value = "".join(ch * 2 for ch in value)
    assert len(value) == 6, f"Expected 3 or 6 hex chars, got: {value}"
    r = int(value[0:2], 16) / 255.0
    g = int(value[2:4], 16) / 255.0
    b = int(value[4:6], 16) / 255.0
    return r, g, b


def _linearize(channel: float) -> float:
    return channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4


def _luminance(hex_color: str) -> float:
    r, g, b = _hex_to_rgb(hex_color)
    return 0.2126 * _linearize(r) + 0.7152 * _linearize(g) + 0.0722 * _linearize(b)


def _contrast_ratio(bg: str, fg: str) -> float:
    l1 = _luminance(bg)
    l2 = _luminance(fg)
    lighter = max(l1, l2)
    darker = min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


def test_code_color_tokens_exist_for_light_and_dark_mode():
    css = _read_css()
    root_vars = _extract_var_block(css, ":root")
    dark_vars = _extract_var_block(css, '[data-theme="dark"]')

    required = [
        "--code-inline-bg",
        "--code-inline-fg",
        "--code-pre-bg",
        "--code-pre-fg",
        "--code-block-bg",
        "--code-block-fg",
        "--code-label-bg",
        "--code-label-fg",
        "--log-block-bg",
        "--log-block-fg",
    ]

    for key in required:
        assert key in root_vars, f"Missing light token: {key}"
        assert key in dark_vars, f"Missing dark token: {key}"


def test_code_color_tokens_meet_wcag_aa():
    css = _read_css()
    root_vars = _extract_var_block(css, ":root")
    dark_vars = _extract_var_block(css, '[data-theme="dark"]')

    pairs = [
        ("--code-inline-bg", "--code-inline-fg"),
        ("--code-pre-bg", "--code-pre-fg"),
        ("--code-block-bg", "--code-block-fg"),
        ("--code-label-bg", "--code-label-fg"),
        ("--log-block-bg", "--log-block-fg"),
    ]

    for mode, vars_map in (("light", root_vars), ("dark", dark_vars)):
        for bg_key, fg_key in pairs:
            ratio = _contrast_ratio(vars_map[bg_key], vars_map[fg_key])
            assert ratio >= 4.5, (
                f"{mode} contrast too low: {bg_key} vs {fg_key} = {ratio:.2f}"
            )


def test_code_readability_selectors_cover_all_render_paths():
    css = _read_css()
    selectors = [
        ".reading-card pre code",
        ".extension-content pre code",
        ".feedback-md pre code",
        ".code-example pre code",
        ".browser-body pre",
        ".log-example pre",
        '[data-theme="dark"] .browser-body pre',
    ]
    for selector in selectors:
        assert selector in css, f"Missing selector for code readability: {selector}"
