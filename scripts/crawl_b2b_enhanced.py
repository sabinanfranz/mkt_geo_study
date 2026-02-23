"""
Enhanced crawl of b2b.fastcampus.co.kr with robots.txt/sitemap parsing,
Selenium fallback for JS-rendered pages, and extended data collection.

Extends scripts/crawl_b2b.py with:
  - Pre-crawl robots.txt and sitemap.xml collection
  - 16 seed URLs (original 6 + 10 strategy/high-score additions)
  - Selenium headless fallback for JS-rendered pages
  - Additional per-page fields (meta_robots, answer_first_block, img_alt_coverage, etc.)

Usage:
    python scripts/crawl_b2b_enhanced.py
    python scripts/crawl_b2b_enhanced.py --max-pages 25
    python scripts/crawl_b2b_enhanced.py --no-selenium

Output:
    data/crawled/{slug}.json            -- per-page structured data (overwrites originals)
    data/crawled/_robots_analysis.json  -- robots.txt analysis
    data/crawled/_sitemap_urls.json     -- sitemap URL listing
    data/crawled/_enhanced_summary.json -- crawl summary with GEO scores
    data/crawled/_enhanced_report.md    -- human-readable analysis report
"""

from __future__ import annotations

import argparse
import json
import re
import time
import xml.etree.ElementTree as ET
from copy import copy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Comment, Tag

# Chrome binary path for Selenium
CHROME_BINARY_PATH = "C:/Program Files/Google/Chrome/Application/chrome.exe"

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_DOMAIN = "b2b.fastcampus.co.kr"
BASE_URL = f"https://{BASE_DOMAIN}"

SEED_URLS = [
    # Existing 6
    f"{BASE_URL}/",
    f"{BASE_URL}/service_custom",
    f"{BASE_URL}/refer_customer",
    f"{BASE_URL}/resource_insight_aiforwork",
    f"{BASE_URL}/resource_seminar_onlinelearning",
    f"{BASE_URL}/service_aicamp_b2bproposalwai",
    # New 5 (strategy-critical, must-crawl)
    f"{BASE_URL}/service_online",
    f"{BASE_URL}/service_online_enterprise",
    f"{BASE_URL}/resource_report",
    f"{BASE_URL}/resource_seminar",
    f"{BASE_URL}/resource_bizletter",
    # New 5 (high-score pages from strategy doc)
    f"{BASE_URL}/refer_customer_coretalentaiedu",
    f"{BASE_URL}/refer_customer_automatewn8n",
    f"{BASE_URL}/resource_insight_25trend",
    f"{BASE_URL}/resource_insight_recipe",
    f"{BASE_URL}/service_aicamp",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}

REQUEST_TIMEOUT = 15  # seconds
SELENIUM_TIMEOUT = 20  # seconds
SELENIUM_WAIT = 3  # seconds to wait after page load for JS rendering
DELAY_BETWEEN_REQUESTS = 1.5  # seconds

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "crawled"

# Tags to remove when extracting text content
REMOVE_TAGS = {"script", "style", "noscript", "svg", "iframe", "head"}

# AI/search bot user-agents to look for in robots.txt
AI_BOT_AGENTS = [
    "OAI-SearchBot",
    "GPTBot",
    "ChatGPT-User",
    "Googlebot",
    "Google-Extended",
    "Bingbot",
    "Anthropic-ai",
    "ClaudeBot",
    "PerplexityBot",
    "Bytespider",
    "CCBot",
]

# FAQ-like patterns for detection
FAQ_PATTERNS = [
    re.compile(r"자주\s*묻는\s*질문", re.IGNORECASE),
    re.compile(r"FAQ", re.IGNORECASE),
    re.compile(r"Q\s*[&.]\s*A", re.IGNORECASE),
    re.compile(r"Q\.\s", re.IGNORECASE),
    re.compile(r"Q\d+[\.\s]", re.IGNORECASE),
    re.compile(r"질문\s*\d+", re.IGNORECASE),
]

# ---------------------------------------------------------------------------
# Selenium support (optional)
# ---------------------------------------------------------------------------

SELENIUM_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.chrome.service import Service

    SELENIUM_AVAILABLE = True
except ImportError:
    pass


def get_selenium_driver():
    """Create a headless Chrome Selenium driver."""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"user-agent={HEADERS['User-Agent']}")
    # Set Chrome binary location
    if Path(CHROME_BINARY_PATH).exists():
        options.binary_location = CHROME_BINARY_PATH
    driver = webdriver.Chrome(options=options)
    driver.set_page_load_timeout(SELENIUM_TIMEOUT)
    return driver


def fetch_with_selenium(url: str, driver) -> str | None:
    """Fetch a page using Selenium and return the rendered page source."""
    try:
        driver.get(url)
        # Wait for JS rendering
        time.sleep(SELENIUM_WAIT)
        return driver.page_source
    except Exception as e:
        print(f"    [SELENIUM ERROR] {e}")
        return None


# ---------------------------------------------------------------------------
# Helpers (same as original)
# ---------------------------------------------------------------------------


def url_to_slug(url: str) -> str:
    """Convert a URL to a filesystem-safe slug for the JSON filename."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return "index"
    slug = re.sub(r"[^a-zA-Z0-9_-]", "_", path)
    return slug


def is_internal_link(href: str) -> bool:
    """Check if a link is internal to b2b.fastcampus.co.kr."""
    if not href:
        return False
    parsed = urlparse(href)
    if parsed.scheme and parsed.scheme not in ("http", "https"):
        return False
    if parsed.netloc and parsed.netloc != BASE_DOMAIN:
        return False
    if not parsed.netloc and not parsed.scheme:
        return True
    return parsed.netloc == BASE_DOMAIN


def normalize_url(href: str, page_url: str) -> str | None:
    """Normalize a link to an absolute URL, or return None if invalid."""
    if not href:
        return None
    if href.startswith(("javascript:", "mailto:", "tel:", "#")):
        return None
    absolute = urljoin(page_url, href)
    parsed = urlparse(absolute)
    if parsed.scheme not in ("http", "https"):
        return None
    clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    if clean != f"{BASE_URL}/" and clean.endswith("/"):
        clean = clean.rstrip("/")
    return clean


def extract_text_content(soup: BeautifulSoup) -> str:
    """Extract cleaned main text content from page, removing scripts/styles."""
    body = soup.find("body")
    if not body:
        return ""

    body_copy = copy(body)

    for tag_name in REMOVE_TAGS:
        for tag in body_copy.find_all(tag_name):
            tag.decompose()

    for comment in body_copy.find_all(
        string=lambda text: isinstance(text, Comment)
    ):
        comment.extract()

    text = body_copy.get_text(separator="\n", strip=True)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Robots.txt and Sitemap parsers
# ---------------------------------------------------------------------------


def fetch_robots_txt(session: requests.Session) -> dict[str, Any]:
    """Fetch and parse robots.txt, returning structured analysis."""
    robots_url = f"{BASE_URL}/robots.txt"
    print(f"  Fetching robots.txt: {robots_url}")

    analysis = {
        "url": robots_url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "status": None,
        "raw_content": None,
        "user_agent_blocks": {},
        "sitemaps": [],
        "ai_bot_summary": {},
    }

    try:
        resp = session.get(robots_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        analysis["status"] = resp.status_code

        if resp.status_code == 404:
            print("    [INFO] robots.txt not found (404). Continuing.")
            analysis["raw_content"] = None
            return analysis

        resp.raise_for_status()
        raw = resp.text
        analysis["raw_content"] = raw

        # Parse robots.txt
        current_agents: list[str] = []
        blocks: dict[str, list[dict]] = {}

        for line in raw.splitlines():
            line = line.strip()
            # Remove comments
            if "#" in line:
                line = line[: line.index("#")].strip()
            if not line:
                continue

            if line.lower().startswith("user-agent:"):
                agent = line.split(":", 1)[1].strip()
                if agent not in blocks:
                    blocks[agent] = []
                # If previous line was also user-agent, group them
                current_agents.append(agent)
            elif line.lower().startswith("disallow:"):
                path = line.split(":", 1)[1].strip()
                for agent in current_agents:
                    blocks.setdefault(agent, []).append(
                        {"directive": "Disallow", "path": path}
                    )
            elif line.lower().startswith("allow:"):
                path = line.split(":", 1)[1].strip()
                for agent in current_agents:
                    blocks.setdefault(agent, []).append(
                        {"directive": "Allow", "path": path}
                    )
            elif line.lower().startswith("sitemap:"):
                sitemap_url = line.split(":", 1)[1].strip()
                # Re-join if the split ate the http: prefix
                if not sitemap_url.startswith("http"):
                    sitemap_url = "https:" + sitemap_url
                analysis["sitemaps"].append(sitemap_url)
                current_agents = []
            elif line.lower().startswith("crawl-delay:"):
                delay_val = line.split(":", 1)[1].strip()
                for agent in current_agents:
                    blocks.setdefault(agent, []).append(
                        {"directive": "Crawl-delay", "value": delay_val}
                    )
            else:
                # Reset agent grouping on unrecognized directive
                current_agents = []

        analysis["user_agent_blocks"] = blocks

        # Summarize AI bot access
        for bot in AI_BOT_AGENTS:
            bot_lower = bot.lower()
            bot_rules = None
            # Check exact match first, then wildcard
            for agent_name, rules in blocks.items():
                if agent_name.lower() == bot_lower:
                    bot_rules = rules
                    break
            if bot_rules is None and "*" in blocks:
                bot_rules = blocks["*"]

            if bot_rules is not None:
                disallowed = [
                    r["path"]
                    for r in bot_rules
                    if r.get("directive") == "Disallow" and r.get("path")
                ]
                allowed = [
                    r["path"]
                    for r in bot_rules
                    if r.get("directive") == "Allow" and r.get("path")
                ]
                if disallowed == ["/"]:
                    status = "BLOCKED"
                elif disallowed:
                    status = "PARTIALLY_BLOCKED"
                else:
                    status = "ALLOWED"
                analysis["ai_bot_summary"][bot] = {
                    "status": status,
                    "disallow": disallowed,
                    "allow": allowed,
                    "source_agent": (
                        bot
                        if any(
                            a.lower() == bot_lower for a in blocks
                        )
                        else "*"
                    ),
                }
            else:
                analysis["ai_bot_summary"][bot] = {
                    "status": "NO_RULES",
                    "disallow": [],
                    "allow": [],
                    "source_agent": None,
                }

        print(f"    Found {len(blocks)} user-agent block(s), {len(analysis['sitemaps'])} sitemap(s)")

    except requests.exceptions.RequestException as e:
        print(f"    [ERROR] Failed to fetch robots.txt: {e}")
        analysis["status"] = "error"
        analysis["error"] = str(e)

    return analysis


def fetch_sitemap(
    session: requests.Session, sitemap_url: str | None = None
) -> list[str]:
    """Fetch sitemap.xml (and sub-sitemaps) and return all page URLs."""
    if sitemap_url is None:
        sitemap_url = f"{BASE_URL}/sitemap.xml"

    print(f"  Fetching sitemap: {sitemap_url}")
    all_urls: list[str] = []

    try:
        resp = session.get(sitemap_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if resp.status_code == 404:
            print("    [INFO] Sitemap not found (404). Continuing.")
            return all_urls
        resp.raise_for_status()

        # Parse XML
        try:
            root = ET.fromstring(resp.content)
        except ET.ParseError as e:
            print(f"    [WARN] Sitemap XML parse error: {e}")
            return all_urls

        # Namespace handling: sitemaps typically use
        # xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        ns_match = re.match(r"\{(.+?)\}", root.tag)
        ns = {"sm": ns_match.group(1)} if ns_match else {}

        # Check if this is a sitemap index (contains <sitemap> elements)
        sitemap_refs = root.findall(".//sm:sitemap/sm:loc", ns) if ns else root.findall(
            ".//sitemap/loc"
        )
        if sitemap_refs:
            print(f"    Found sitemap index with {len(sitemap_refs)} sub-sitemaps")
            for loc_el in sitemap_refs:
                sub_url = loc_el.text.strip() if loc_el.text else None
                if sub_url:
                    time.sleep(0.5)
                    sub_urls = fetch_sitemap(session, sub_url)
                    all_urls.extend(sub_urls)
        else:
            # Regular sitemap: extract <url><loc> entries
            url_locs = root.findall(".//sm:url/sm:loc", ns) if ns else root.findall(
                ".//url/loc"
            )
            for loc_el in url_locs:
                page_url = loc_el.text.strip() if loc_el.text else None
                if page_url:
                    all_urls.append(page_url)
            print(f"    Found {len(url_locs)} URL(s) in sitemap")

    except requests.exceptions.RequestException as e:
        print(f"    [ERROR] Failed to fetch sitemap: {e}")

    return all_urls


# ---------------------------------------------------------------------------
# Enhanced data extraction helpers
# ---------------------------------------------------------------------------


def extract_meta_robots(soup: BeautifulSoup) -> str | None:
    """Extract <meta name='robots' content='...'> value."""
    tag = soup.find("meta", attrs={"name": re.compile(r"^robots$", re.IGNORECASE)})
    if tag:
        return tag.get("content", "").strip() or None
    return None


def extract_hreflang_tags(soup: BeautifulSoup) -> list[dict]:
    """Extract hreflang link tags."""
    tags = []
    for link in soup.find_all("link", attrs={"rel": "alternate", "hreflang": True}):
        lang = link.get("hreflang", "").strip()
        href = link.get("href", "").strip()
        if lang and href:
            tags.append({"lang": lang, "url": href})
    return tags


def extract_answer_first_block(soup: BeautifulSoup) -> str | None:
    """
    Extract the text content between the first H1 and the next heading
    (H2/H3) -- up to 500 characters max.
    This represents the 'Answer-first' zone for GEO strategy.
    """
    h1 = soup.find("h1")
    if not h1:
        return None

    collected_text: list[str] = []
    total_len = 0

    # Walk siblings after the H1
    sibling = h1.find_next_sibling()
    while sibling:
        if isinstance(sibling, Tag):
            tag_name = sibling.name.lower() if sibling.name else ""
            # Stop at next heading
            if tag_name in ("h1", "h2", "h3"):
                break
            text = sibling.get_text(strip=True)
            if text:
                collected_text.append(text)
                total_len += len(text)
                if total_len >= 500:
                    break
        sibling = sibling.find_next_sibling()

    if not collected_text:
        # Try walking all next elements (not just siblings), e.g. nested structures
        for el in h1.find_all_next():
            if isinstance(el, Tag):
                tag_name = el.name.lower() if el.name else ""
                if tag_name in ("h1", "h2", "h3"):
                    break
                # Only capture block-level / meaningful text containers
                if tag_name in (
                    "p",
                    "div",
                    "span",
                    "li",
                    "blockquote",
                    "section",
                    "article",
                ):
                    text = el.get_text(strip=True)
                    if text and text not in " ".join(collected_text):
                        collected_text.append(text)
                        total_len += len(text)
                        if total_len >= 500:
                            break

    if not collected_text:
        return None

    block = " ".join(collected_text)
    # Trim to 500 chars max
    if len(block) > 500:
        block = block[:500]

    return block


def compute_img_alt_coverage(images: list[dict]) -> dict:
    """Compute image alt text coverage statistics."""
    total = len(images)
    if total == 0:
        return {"total": 0, "with_alt": 0, "ratio": 0.0}
    with_alt = sum(1 for img in images if img.get("alt", "").strip())
    return {
        "total": total,
        "with_alt": with_alt,
        "ratio": round(with_alt / total, 3),
    }


def count_words(text: str) -> int:
    """Approximate word count for Korean + English mixed text.
    For Korean, count characters / 3.5 as rough word equivalent,
    plus actual English/number word tokens.
    """
    if not text:
        return 0
    # Split on whitespace
    tokens = text.split()
    # A very rough approximation: each whitespace-delimited token is ~1 word
    # For Korean text without spaces between every word, this still works
    # reasonably because Korean uses spaces between phrases.
    return len(tokens)


def count_faq_patterns(text: str, soup: BeautifulSoup) -> int:
    """Count FAQ-like patterns in the page text and structure."""
    count = 0
    for pattern in FAQ_PATTERNS:
        count += len(pattern.findall(text))

    # Also check for FAQ-structured elements (dl/dt/dd, accordion patterns)
    for dt in soup.find_all("dt"):
        count += 1
    # Check for elements with FAQ-related class names
    for el in soup.find_all(attrs={"class": re.compile(r"faq|accordion|qa", re.IGNORECASE)}):
        count += 1

    return count


def count_subheadings(headings: list[dict]) -> int:
    """Count H2, H3, and H4 headings."""
    return sum(1 for h in headings if h["level"] in (2, 3, 4))


# ---------------------------------------------------------------------------
# Page Crawler (enhanced)
# ---------------------------------------------------------------------------


def crawl_page(
    url: str,
    session: requests.Session,
    selenium_driver=None,
    use_selenium: bool = True,
) -> dict[str, Any] | None:
    """Crawl a single page and return structured data, or None on failure.

    First tries with requests. If the page appears JS-rendered (no title and
    text_length < 300), retries with Selenium if available.
    """
    print(f"  Fetching: {url}")
    rendered_with = "requests"
    js_rendered = False
    resp_headers_dict: dict[str, str | None] = {
        "Last-Modified": None,
        "Cache-Control": None,
        "Content-Type": None,
        "X-Frame-Options": None,
    }
    x_robots_tag: str | None = None
    status_code: int | None = None

    # --- Attempt with requests first ---
    html_text: str | None = None
    try:
        resp = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        status_code = resp.status_code

        content_type = resp.headers.get("Content-Type", "")
        if "text/html" not in content_type and "application/xhtml" not in content_type:
            print(f"    [SKIP] Non-HTML content type: {content_type}")
            return None

        html_text = resp.text
        resp_headers_dict = {
            "Last-Modified": resp.headers.get("Last-Modified"),
            "Cache-Control": resp.headers.get("Cache-Control"),
            "Content-Type": resp.headers.get("Content-Type"),
            "X-Frame-Options": resp.headers.get("X-Frame-Options"),
        }
        x_robots_tag = resp.headers.get("X-Robots-Tag")

    except requests.exceptions.Timeout:
        print(f"    [ERROR] Timeout for {url}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"    [ERROR] HTTP {e.response.status_code} for {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"    [ERROR] Request failed for {url}: {e}")
        return None

    # --- Check if Selenium fallback is needed ---
    soup = BeautifulSoup(html_text, "html.parser")
    title_tag = soup.find("title")
    title_text = title_tag.get_text(strip=True) if title_tag else None
    h1_tags = soup.find_all("h1")
    preliminary_text = extract_text_content(soup)
    preliminary_len = len(preliminary_text)

    # Trigger Selenium if: no title OR no H1, OR text_length < 500
    needs_selenium = (not title_text) or (len(h1_tags) == 0) or (preliminary_len < 500)

    if needs_selenium and use_selenium and selenium_driver is not None:
        print("    [INFO] Page appears JS-rendered. Retrying with Selenium...")
        selenium_html = fetch_with_selenium(url, selenium_driver)
        if selenium_html:
            html_text = selenium_html
            soup = BeautifulSoup(html_text, "html.parser")
            rendered_with = "selenium"
            js_rendered = True
            print("    [INFO] Using Selenium-rendered content.")
        else:
            rendered_with = "requests_only"
            js_rendered = False
            print("    [WARN] Selenium fallback failed. Using requests content.")
    elif needs_selenium and use_selenium and selenium_driver is None:
        rendered_with = "requests_only"
        js_rendered = False
        print("    [INFO] Selenium not available, using requests-only data.")

    # --- Parse page content ---

    # Title
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else None

    # Meta description
    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = (
        meta_desc_tag.get("content", "").strip() if meta_desc_tag else None
    )

    # Meta keywords
    meta_kw_tag = soup.find("meta", attrs={"name": "keywords"})
    meta_keywords = meta_kw_tag.get("content", "").strip() if meta_kw_tag else None

    # Meta robots
    meta_robots = extract_meta_robots(soup)

    # OG tags
    og_tags = {}
    for og in soup.find_all("meta", attrs={"property": re.compile(r"^og:")}):
        prop = og.get("property", "")
        content = og.get("content", "")
        if prop and content:
            og_tags[prop] = content

    # Canonical URL
    canonical_tag = soup.find("link", attrs={"rel": "canonical"})
    canonical = canonical_tag.get("href", "").strip() if canonical_tag else None

    # Hreflang tags
    hreflang_tags = extract_hreflang_tags(soup)

    # Headings
    headings = []
    for level in range(1, 7):
        tag_name = f"h{level}"
        for h in soup.find_all(tag_name):
            text = h.get_text(strip=True)
            if text:
                headings.append({"level": level, "tag": tag_name, "text": text})

    # JSON-LD structured data
    json_ld_scripts = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "")
            json_ld_scripts.append(data)
        except (json.JSONDecodeError, TypeError):
            pass

    # Schema.org microdata (itemscope)
    schema_microdata = []
    for el in soup.find_all(attrs={"itemscope": True}):
        item_type = el.get("itemtype", "")
        if item_type:
            schema_microdata.append(item_type)

    # RDFa schema.org
    rdfa_types = []
    for el in soup.find_all(attrs={"typeof": True}):
        rdfa_types.append(el.get("typeof", ""))

    # Links
    internal_links = []
    external_links = []
    seen_internal: set[str] = set()
    seen_external: set[str] = set()

    for a in soup.find_all("a", href=True):
        href = a.get("href", "").strip()
        normalized = normalize_url(href, url)
        if not normalized:
            continue

        link_text = a.get_text(strip=True)
        link_info = {"url": normalized, "text": link_text}

        if is_internal_link(href):
            if normalized not in seen_internal:
                seen_internal.add(normalized)
                internal_links.append(link_info)
        else:
            if normalized not in seen_external:
                seen_external.add(normalized)
                external_links.append(link_info)

    # Images
    images = []
    for img in soup.find_all("img"):
        src = img.get("src", "").strip()
        alt = img.get("alt", "").strip()
        if src:
            abs_src = normalize_url(src, url) or src
            images.append({"src": abs_src, "alt": alt})

    # Main text content
    text_content = extract_text_content(soup)

    # Nav elements
    nav_links = []
    for nav in soup.find_all("nav"):
        for a in nav.find_all("a", href=True):
            href = a.get("href", "").strip()
            normalized = normalize_url(href, url)
            if normalized and is_internal_link(href):
                link_text = a.get_text(strip=True)
                nav_links.append({"url": normalized, "text": link_text})

    for header in soup.find_all("header"):
        for a in header.find_all("a", href=True):
            href = a.get("href", "").strip()
            normalized = normalize_url(href, url)
            if normalized and is_internal_link(href):
                link_text = a.get_text(strip=True)
                nav_links.append({"url": normalized, "text": link_text})

    # Deduplicate nav_links
    seen_nav: set[str] = set()
    unique_nav = []
    for nl in nav_links:
        if nl["url"] not in seen_nav:
            seen_nav.add(nl["url"])
            unique_nav.append(nl)
    nav_links = unique_nav

    # --- Enhanced fields ---
    answer_first_block = extract_answer_first_block(soup)
    img_alt_coverage = compute_img_alt_coverage(images)
    word_count = count_words(text_content)
    faq_count = count_faq_patterns(text_content, soup)
    subheading_count = count_subheadings(headings)

    result = {
        # Original fields
        "url": url,
        "slug": url_to_slug(url),
        "crawled_at": datetime.now(timezone.utc).isoformat(),
        "status_code": status_code,
        "title": title,
        "meta_description": meta_description,
        "meta_keywords": meta_keywords,
        "canonical": canonical,
        "og_tags": og_tags,
        "headings": headings,
        "json_ld": json_ld_scripts,
        "schema_microdata": schema_microdata,
        "rdfa_types": rdfa_types,
        "internal_links": internal_links,
        "external_links": external_links,
        "nav_links": nav_links,
        "images": images,
        "text_content": text_content[:50000],
        "text_length": len(text_content),
        "h1_count": sum(1 for h in headings if h["level"] == 1),
        "has_structured_data": len(json_ld_scripts) > 0 or len(schema_microdata) > 0,
        # Enhanced fields
        "rendered_with": rendered_with,
        "js_rendered": js_rendered,
        "meta_robots": meta_robots,
        "x_robots_tag": x_robots_tag,
        "response_headers": resp_headers_dict,
        "hreflang": hreflang_tags,
        "answer_first_block": answer_first_block,
        "img_alt_coverage": img_alt_coverage,
        "word_count": word_count,
        "faq_count": faq_count,
        "subheading_count": subheading_count,
    }

    print(f"    OK - title: {title}")
    print(
        f"    Headings: {len(headings)}, Internal links: {len(internal_links)}, "
        f"External links: {len(external_links)}, Images: {len(images)}"
    )
    print(f"    Rendered with: {rendered_with}, Word count: {word_count}")
    if answer_first_block:
        preview = answer_first_block[:80] + "..." if len(answer_first_block) > 80 else answer_first_block
        print(f"    Answer-first block: {preview}")
    if json_ld_scripts:
        print(f"    JSON-LD blocks: {len(json_ld_scripts)}")
    if schema_microdata:
        print(f"    Schema microdata types: {schema_microdata}")

    return result


# ---------------------------------------------------------------------------
# Discovery: find additional pages from navigation
# ---------------------------------------------------------------------------


def discover_urls_from_results(results: list[dict]) -> list[str]:
    """Extract internal URLs from all crawled pages for further crawling."""
    discovered: set[str] = set()
    for r in results:
        for link in r.get("nav_links", []):
            url = link["url"]
            parsed = urlparse(url)
            if parsed.netloc == BASE_DOMAIN:
                discovered.add(url)
        for link in r.get("internal_links", []):
            url = link["url"]
            parsed = urlparse(url)
            if parsed.netloc == BASE_DOMAIN:
                discovered.add(url)
    return sorted(discovered)


# ---------------------------------------------------------------------------
# Report Generation (enhanced)
# ---------------------------------------------------------------------------


def generate_enhanced_summary(
    results: list[dict],
    all_discovered: list[str],
    robots_analysis: dict,
    sitemap_urls: list[str],
) -> dict:
    """Generate _enhanced_summary.json content."""
    total_internal = sum(len(r.get("internal_links", [])) for r in results)
    total_external = sum(len(r.get("external_links", [])) for r in results)

    nav_structure = {}
    for r in results:
        for nl in r.get("nav_links", []):
            nav_structure[nl["url"]] = nl.get("text", "")

    # Per-page GEO scores
    page_scores = []
    for r in results:
        score = 0
        issues = []

        # Title
        if r.get("title"):
            score += 10
        else:
            issues.append("Missing title")

        # Meta description
        if r.get("meta_description"):
            score += 10
        else:
            issues.append("Missing meta description")

        # H1
        if r.get("h1_count") == 1:
            score += 10
        elif r.get("h1_count", 0) > 1:
            score += 5
            issues.append(f"Multiple H1 ({r['h1_count']})")
        else:
            issues.append("Missing H1")

        # Structured data
        if r.get("has_structured_data"):
            score += 15
        else:
            issues.append("No structured data")

        # Canonical
        if r.get("canonical"):
            score += 5
        else:
            issues.append("Missing canonical")

        # OG tags
        if r.get("og_tags"):
            score += 5
        else:
            issues.append("Missing OG tags")

        # Answer-first block
        if r.get("answer_first_block"):
            score += 15
        else:
            issues.append("No answer-first block after H1")

        # Word count (prefer substantial content)
        wc = r.get("word_count", 0)
        if wc >= 500:
            score += 10
        elif wc >= 200:
            score += 5
        else:
            issues.append(f"Low word count ({wc})")

        # Image alt coverage
        alt_cov = r.get("img_alt_coverage", {})
        if alt_cov.get("total", 0) > 0:
            ratio = alt_cov.get("ratio", 0)
            if ratio >= 0.8:
                score += 10
            elif ratio >= 0.5:
                score += 5
            else:
                issues.append(f"Low image alt coverage ({ratio:.0%})")
        else:
            score += 5  # No images = neutral

        # Subheadings (content structure)
        if r.get("subheading_count", 0) >= 3:
            score += 5
        elif r.get("subheading_count", 0) >= 1:
            score += 3
        else:
            issues.append("Few/no subheadings")

        # FAQ presence
        if r.get("faq_count", 0) > 0:
            score += 5
        else:
            issues.append("No FAQ content detected")

        page_scores.append(
            {
                "url": r["url"],
                "slug": r["slug"],
                "score": score,
                "max_score": 100,
                "grade": (
                    "A" if score >= 80 else
                    "B" if score >= 60 else
                    "C" if score >= 40 else
                    "D" if score >= 20 else
                    "F"
                ),
                "issues": issues,
            }
        )

    # Selenium rendering summary
    selenium_pages = [r["url"] for r in results if r.get("rendered_with") == "selenium"]
    requests_pages = [r["url"] for r in results if r.get("rendered_with") == "requests"]
    pages_needing_selenium = [
        r["url"] for r in results
        if r.get("rendered_with") in ("selenium", "requests_only")
    ]
    pages_selenium_failed = [
        r["url"] for r in results
        if r.get("rendered_with") == "requests_only"
    ]

    return {
        "crawl_timestamp": datetime.now(timezone.utc).isoformat(),
        "base_domain": BASE_DOMAIN,
        "page_count": len(results),
        "crawled_urls": [r["url"] for r in results],
        "total_internal_links": total_internal,
        "total_external_links": total_external,
        "discovered_urls_not_crawled": [
            u for u in all_discovered if u not in {r["url"] for r in results}
        ],
        "navigation_structure": nav_structure,
        "pages_with_structured_data": [
            r["url"] for r in results if r.get("has_structured_data")
        ],
        "pages_without_structured_data": [
            r["url"] for r in results if not r.get("has_structured_data")
        ],
        "robots_txt": {
            "raw": robots_analysis.get("raw_content"),
            "parsed_rules": robots_analysis.get("user_agent_blocks", {}),
            "ai_bot_summary": robots_analysis.get("ai_bot_summary", {}),
            "sitemaps_found": robots_analysis.get("sitemaps", []),
            "status": robots_analysis.get("status"),
        },
        "sitemap_urls": sitemap_urls if isinstance(sitemap_urls, list) else [],
        "sitemap_url_count": len(sitemap_urls),
        "sitemap_urls_in_crawl": [
            u for u in sitemap_urls if u in {r["url"] for r in results}
        ],
        "sitemap_urls_not_crawled": [
            u for u in sitemap_urls if u not in {r["url"] for r in results}
        ],
        "pages_needing_selenium": pages_needing_selenium,
        "pages_selenium_failed": pages_selenium_failed,
        "rendering_summary": {
            "selenium_rendered": selenium_pages,
            "requests_only": requests_pages,
        },
        "page_geo_scores": page_scores,
        "average_geo_score": (
            round(sum(ps["score"] for ps in page_scores) / len(page_scores), 1)
            if page_scores
            else 0
        ),
    }


def generate_enhanced_report(
    results: list[dict],
    summary: dict,
    robots_analysis: dict,
    sitemap_urls: list[str],
) -> str:
    """Generate _enhanced_report.md content."""
    lines: list[str] = []
    lines.append("# b2b.fastcampus.co.kr Enhanced Crawl Report (GEO Analysis)")
    lines.append("")
    lines.append(f"**Crawl Date:** {summary['crawl_timestamp']}")
    lines.append(f"**Pages Crawled:** {summary['page_count']}")
    lines.append(f"**Total Internal Links Found:** {summary['total_internal_links']}")
    lines.append(f"**Total External Links Found:** {summary['total_external_links']}")
    lines.append(f"**Average GEO Score:** {summary.get('average_geo_score', 0)}/100")
    lines.append("")

    # =========================================================
    # Robots.txt Analysis
    # =========================================================
    lines.append("## Robots.txt Analysis")
    lines.append("")

    r_status = robots_analysis.get("status")
    if r_status == 404:
        lines.append("**robots.txt not found (404).** No crawl restrictions detected.")
    elif r_status == "error":
        lines.append(f"**Error fetching robots.txt:** {robots_analysis.get('error', 'unknown')}")
    else:
        lines.append(f"**Status:** {r_status}")
        lines.append("")

        ai_summary = robots_analysis.get("ai_bot_summary", {})
        if ai_summary:
            lines.append("### AI/Search Bot Access")
            lines.append("")
            lines.append("| Bot | Status | Disallow Paths | Source |")
            lines.append("|-----|--------|---------------|--------|")
            for bot, info in ai_summary.items():
                status = info.get("status", "?")
                disallow = ", ".join(info.get("disallow", [])) or "(none)"
                source = info.get("source_agent", "?")
                lines.append(f"| {bot} | {status} | {disallow} | {source} |")
            lines.append("")

        blocks = robots_analysis.get("user_agent_blocks", {})
        if blocks:
            lines.append("### All User-Agent Blocks")
            lines.append("")
            for agent, rules in blocks.items():
                lines.append(f"**{agent}:**")
                for rule in rules:
                    directive = rule.get("directive", "")
                    path = rule.get("path", rule.get("value", ""))
                    lines.append(f"- {directive}: {path}")
                lines.append("")

        sitemaps_in_robots = robots_analysis.get("sitemaps", [])
        if sitemaps_in_robots:
            lines.append("### Sitemaps Referenced in robots.txt")
            lines.append("")
            for sm in sitemaps_in_robots:
                lines.append(f"- {sm}")
            lines.append("")

    lines.append("---")
    lines.append("")

    # =========================================================
    # Sitemap Coverage
    # =========================================================
    lines.append("## Sitemap Coverage")
    lines.append("")

    if sitemap_urls:
        lines.append(f"**Total URLs in sitemap:** {len(sitemap_urls)}")
        crawled_set = {r["url"] for r in results}
        in_crawl = [u for u in sitemap_urls if u in crawled_set]
        not_crawled = [u for u in sitemap_urls if u not in crawled_set]
        lines.append(f"**Crawled from sitemap:** {len(in_crawl)}")
        lines.append(f"**Not crawled from sitemap:** {len(not_crawled)}")
        lines.append("")
        if not_crawled:
            lines.append("### Sitemap URLs Not Crawled")
            lines.append("")
            for u in not_crawled[:50]:
                lines.append(f"- {u}")
            if len(not_crawled) > 50:
                lines.append(f"- ... and {len(not_crawled) - 50} more")
            lines.append("")
    else:
        lines.append("No sitemap found or sitemap was empty.")
        lines.append("")

    lines.append("---")
    lines.append("")

    # =========================================================
    # JS Rendering Status
    # =========================================================
    lines.append("## JS Rendering Status")
    lines.append("")

    sel_needed = summary.get("pages_needing_selenium", [])
    sel_failed = summary.get("pages_selenium_failed", [])
    rendering = summary.get("rendering_summary", {})
    selenium_pages = rendering.get("selenium_rendered", [])
    requests_pages = rendering.get("requests_only", [])

    if sel_needed:
        lines.append(
            f"**{len(sel_needed)} page(s)** required Selenium fallback:"
        )
        lines.append("")
        for u in sel_needed:
            lines.append(f"- {u}")
        lines.append("")
    else:
        lines.append("All pages were successfully rendered with requests (no Selenium needed).")
        lines.append("")

    if sel_failed:
        lines.append(f"**{len(sel_failed)} page(s)** where Selenium failed:")
        lines.append("")
        for u in sel_failed:
            lines.append(f"- {u}")
        lines.append("")

    if selenium_pages:
        lines.append(f"**{len(selenium_pages)} page(s)** successfully rendered with Selenium.")
        lines.append("")

    lines.append(f"**{len(requests_pages)} page(s)** rendered with requests only.")
    lines.append("")
    lines.append("---")
    lines.append("")

    # =========================================================
    # Answer-first Audit
    # =========================================================
    lines.append("## Answer-first Audit")
    lines.append("")
    lines.append(
        "The 'Answer-first' block is the text immediately following the first H1 heading, "
        "before the next H2/H3. This is critical for GEO strategy -- AI systems often "
        "extract this zone as the primary answer."
    )
    lines.append("")

    has_answer = [r for r in results if r.get("answer_first_block")]
    no_answer = [r for r in results if not r.get("answer_first_block")]

    lines.append(f"**Pages WITH answer-first block:** {len(has_answer)}")
    lines.append(f"**Pages WITHOUT answer-first block:** {len(no_answer)}")
    lines.append("")

    if has_answer:
        lines.append("### Pages with Answer-first Content")
        lines.append("")
        for r in has_answer:
            block = r["answer_first_block"]
            preview = block[:150] + "..." if len(block) > 150 else block
            lines.append(f"**{r.get('title', r['url'])}**")
            lines.append(f"> {preview}")
            lines.append("")

    if no_answer:
        lines.append("### Pages Missing Answer-first Content (ACTION NEEDED)")
        lines.append("")
        for r in no_answer:
            lines.append(f"- [ ] {r['url']} -- {r.get('title', '(no title)')}")
        lines.append("")

    lines.append("---")
    lines.append("")

    # =========================================================
    # GEO Score Summary
    # =========================================================
    lines.append("## GEO Score Summary")
    lines.append("")

    page_scores = summary.get("page_geo_scores", [])
    if page_scores:
        # Sort by score descending
        sorted_scores = sorted(page_scores, key=lambda x: x["score"], reverse=True)
        lines.append("| Page | Score | Grade | Key Issues |")
        lines.append("|------|-------|-------|------------|")
        for ps in sorted_scores:
            slug = ps.get("slug", "?")
            score = ps["score"]
            grade = ps["grade"]
            issues = "; ".join(ps.get("issues", [])[:3])
            if len(ps.get("issues", [])) > 3:
                issues += f" (+{len(ps['issues']) - 3} more)"
            lines.append(f"| {slug} | {score}/100 | {grade} | {issues} |")
        lines.append("")
    lines.append("---")
    lines.append("")

    # =========================================================
    # Site Structure Analysis
    # =========================================================
    lines.append("## Site Structure Analysis")
    lines.append("")
    lines.append("### Navigation Links Discovered")
    lines.append("")
    nav = summary.get("navigation_structure", {})
    if nav:
        for url, text in sorted(nav.items()):
            label = text if text else "(no text)"
            lines.append(f"- [{label}]({url})")
    else:
        lines.append("No navigation links discovered.")
    lines.append("")

    # =========================================================
    # Per-Page Analysis
    # =========================================================
    lines.append("## Per-Page Analysis")
    lines.append("")

    for r in results:
        lines.append(f"### {r.get('title', '(no title)')}")
        lines.append(f"**URL:** {r['url']}")
        lines.append(f"**Status:** {r['status_code']}")
        lines.append(f"**Rendered with:** {r.get('rendered_with', 'requests')}")
        lines.append("")

        # Meta info
        meta_desc = r.get("meta_description")
        lines.append(
            f"- **Meta Description:** {meta_desc if meta_desc else 'MISSING'}"
        )
        lines.append(f"- **Canonical:** {r.get('canonical', 'MISSING')}")
        lines.append(f"- **Meta Robots:** {r.get('meta_robots', 'none')}")
        lines.append(f"- **X-Robots-Tag:** {r.get('x_robots_tag', 'none')}")
        lines.append(f"- **Text Length:** {r.get('text_length', 0)} chars")
        lines.append(f"- **Word Count:** {r.get('word_count', 0)}")
        lines.append(f"- **Subheadings (H2-H4):** {r.get('subheading_count', 0)}")
        lines.append(f"- **FAQ patterns detected:** {r.get('faq_count', 0)}")
        lines.append("")

        # Image alt coverage
        alt_cov = r.get("img_alt_coverage", {})
        if alt_cov.get("total", 0) > 0:
            lines.append(
                f"- **Image Alt Coverage:** {alt_cov['with_alt']}/{alt_cov['total']} "
                f"({alt_cov['ratio']:.0%})"
            )
        else:
            lines.append("- **Image Alt Coverage:** No images found")
        lines.append("")

        # Hreflang tags
        hreflang = r.get("hreflang", [])
        if hreflang:
            lines.append("**Hreflang Tags:**")
            for hl in hreflang:
                lines.append(f"- {hl['lang']}: {hl['url']}")
            lines.append("")

        # Response headers
        rh = r.get("response_headers", {})
        if any(v for v in rh.values() if v):
            lines.append("**Response Headers:**")
            for k, v in rh.items():
                if v:
                    lines.append(f"- {k}: {v}")
            lines.append("")

        # OG tags
        og = r.get("og_tags", {})
        if og:
            lines.append("**Open Graph Tags:**")
            for k, v in og.items():
                lines.append(f"- {k}: {v}")
            lines.append("")

        # Heading structure
        headings = r.get("headings", [])
        if headings:
            lines.append("**Heading Structure:**")
            lines.append("```")
            for h in headings:
                indent = "  " * (h["level"] - 1)
                lines.append(f"{indent}{h['tag'].upper()}: {h['text']}")
            lines.append("```")
        else:
            lines.append("**Heading Structure:** NONE")
        lines.append("")

        # Structured data
        json_ld = r.get("json_ld", [])
        microdata = r.get("schema_microdata", [])
        if json_ld or microdata:
            lines.append("**Structured Data:**")
            if json_ld:
                for i, ld in enumerate(json_ld):
                    ld_type = ld.get("@type", "unknown")
                    lines.append(f"- JSON-LD #{i + 1}: @type = {ld_type}")
            if microdata:
                for m in microdata:
                    lines.append(f"- Microdata: {m}")
        else:
            lines.append("**Structured Data:** NONE")
        lines.append("")

        # Link counts
        int_count = len(r.get("internal_links", []))
        ext_count = len(r.get("external_links", []))
        img_count = len(r.get("images", []))
        lines.append(f"- Internal links: {int_count}")
        lines.append(f"- External links: {ext_count}")
        lines.append(f"- Images: {img_count}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # =========================================================
    # Internal Link Map
    # =========================================================
    lines.append("## Internal Link Map")
    lines.append("")
    lines.append("Source Page -> Target Pages (internal)")
    lines.append("")
    for r in results:
        slug = r.get("slug", "unknown")
        int_links = r.get("internal_links", [])
        if int_links:
            lines.append(f"### {slug}")
            for link in int_links[:30]:
                text = link.get("text", "(no anchor text)")
                lines.append(f"- [{text}]({link['url']})")
            if len(int_links) > 30:
                lines.append(f"- ... and {len(int_links) - 30} more")
            lines.append("")

    # =========================================================
    # Missing Elements Report (Enhanced)
    # =========================================================
    lines.append("## Missing Elements Report")
    lines.append("")
    lines.append("Pages with potential issues:")
    lines.append("")

    issues_found = False
    for r in results:
        page_issues = []
        if not r.get("title"):
            page_issues.append("No <title> tag")
        if not r.get("meta_description"):
            page_issues.append("No meta description")
        if r.get("h1_count", 0) == 0:
            page_issues.append("No H1 tag")
        if r.get("h1_count", 0) > 1:
            page_issues.append(f"Multiple H1 tags ({r['h1_count']})")
        if not r.get("has_structured_data"):
            page_issues.append("No structured data (JSON-LD or microdata)")
        if not r.get("canonical"):
            page_issues.append("No canonical URL")
        if not r.get("og_tags"):
            page_issues.append("No Open Graph tags")
        if not r.get("answer_first_block"):
            page_issues.append("No answer-first block after H1")
        alt_cov = r.get("img_alt_coverage", {})
        if alt_cov.get("total", 0) > 0 and alt_cov.get("ratio", 0) < 0.5:
            page_issues.append(
                f"Low image alt coverage ({alt_cov['ratio']:.0%})"
            )
        if r.get("word_count", 0) < 200:
            page_issues.append(f"Low word count ({r.get('word_count', 0)})")
        if r.get("subheading_count", 0) == 0:
            page_issues.append("No subheadings (H2-H4)")
        if r.get("meta_robots") and "noindex" in r.get("meta_robots", "").lower():
            page_issues.append(f"meta robots noindex: {r['meta_robots']}")
        if r.get("x_robots_tag") and "noindex" in r.get("x_robots_tag", "").lower():
            page_issues.append(f"X-Robots-Tag noindex: {r['x_robots_tag']}")

        if page_issues:
            issues_found = True
            lines.append(f"### {r['url']}")
            for issue in page_issues:
                lines.append(f"- [ ] {issue}")
            lines.append("")

    if not issues_found:
        lines.append(
            "No issues found. All pages have title, meta description, H1, "
            "structured data, and answer-first content."
        )
        lines.append("")

    # =========================================================
    # Uncrawled Discovered URLs
    # =========================================================
    uncrawled = summary.get("discovered_urls_not_crawled", [])
    if uncrawled:
        lines.append("## Discovered but Not Crawled")
        lines.append("")
        lines.append(
            f"Found {len(uncrawled)} additional internal URLs that were not crawled "
            "(increase --max-pages to include them):"
        )
        lines.append("")
        for u in uncrawled[:50]:
            lines.append(f"- {u}")
        if len(uncrawled) > 50:
            lines.append(f"- ... and {len(uncrawled) - 50} more")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Enhanced crawl of b2b.fastcampus.co.kr with Selenium fallback and GEO analysis."
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=25,
        help="Maximum number of pages to crawl (default: 25)",
    )
    parser.add_argument(
        "--no-selenium",
        action="store_true",
        help="Skip Selenium JS rendering even if available",
    )
    args = parser.parse_args()

    max_pages = args.max_pages
    use_selenium = not args.no_selenium

    print("=== b2b.fastcampus.co.kr Enhanced Crawler (GEO) ===")
    print(f"Max pages: {max_pages}")
    print(f"Selenium: {'enabled' if use_selenium else 'disabled'}")
    print(f"Selenium available: {SELENIUM_AVAILABLE}")
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update(HEADERS)

    # --- Pre-crawl: robots.txt ---
    print("[Pre-crawl] Analyzing robots.txt...")
    robots_analysis = fetch_robots_txt(session)

    robots_path = OUTPUT_DIR / "_robots_analysis.json"
    with open(robots_path, "w", encoding="utf-8") as f:
        json.dump(robots_analysis, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {robots_path.name}")
    print()

    # --- Pre-crawl: sitemap.xml ---
    print("[Pre-crawl] Fetching sitemap...")
    # Collect sitemap URLs from robots.txt references + default
    sitemap_sources = list(robots_analysis.get("sitemaps", []))
    if f"{BASE_URL}/sitemap.xml" not in sitemap_sources:
        sitemap_sources.insert(0, f"{BASE_URL}/sitemap.xml")

    all_sitemap_urls: list[str] = []
    seen_sitemap: set[str] = set()
    for sm_url in sitemap_sources:
        urls = fetch_sitemap(session, sm_url)
        for u in urls:
            if u not in seen_sitemap:
                seen_sitemap.add(u)
                all_sitemap_urls.append(u)

    sitemap_path = OUTPUT_DIR / "_sitemap_urls.json"
    with open(sitemap_path, "w", encoding="utf-8") as f:
        json.dump(
            {
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "sources": sitemap_sources,
                "total_urls": len(all_sitemap_urls),
                "urls": all_sitemap_urls,
            },
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"  Saved: {sitemap_path.name} ({len(all_sitemap_urls)} URLs)")
    print()

    # --- Setup Selenium driver (if needed) ---
    selenium_driver = None
    if use_selenium and SELENIUM_AVAILABLE:
        try:
            selenium_driver = get_selenium_driver()
            print("[Selenium] ChromeDriver initialized successfully.")
        except Exception as e:
            print(f"[Selenium] WARNING: Failed to initialize ChromeDriver: {e}")
            print("[Selenium] Falling back to requests-only mode.")
            selenium_driver = None
    elif use_selenium and not SELENIUM_AVAILABLE:
        print(
            "[Selenium] WARNING: selenium package not installed. "
            "Install with: pip install selenium"
        )
        print("[Selenium] Falling back to requests-only mode.")
    print()

    # --- Phase 1: Crawl seed URLs ---
    results: list[dict] = []
    crawled_urls: set[str] = set()
    queue: list[str] = list(SEED_URLS)
    all_discovered: set[str] = set(SEED_URLS)

    print("[Phase 1] Crawling seed URLs...")
    print()

    while queue and len(results) < max_pages:
        url = queue.pop(0)
        if url in crawled_urls:
            continue

        crawled_urls.add(url)
        result = crawl_page(
            url, session, selenium_driver=selenium_driver, use_selenium=use_selenium
        )

        if result:
            results.append(result)
            slug = result["slug"]
            out_path = OUTPUT_DIR / f"{slug}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"    Saved: {out_path.name}")

        print()
        time.sleep(DELAY_BETWEEN_REQUESTS)

    # --- Phase 2: Discover and crawl additional pages ---
    print("[Phase 2] Discovering additional pages from navigation...")
    discovered = discover_urls_from_results(results)
    new_urls = [u for u in discovered if u not in crawled_urls]
    all_discovered.update(discovered)

    if new_urls:
        print(f"  Found {len(new_urls)} new internal URLs from navigation/links.")
        print()

        for url in new_urls:
            if len(results) >= max_pages:
                print(f"  Reached max-pages limit ({max_pages}). Stopping.")
                break
            if url in crawled_urls:
                continue

            crawled_urls.add(url)
            result = crawl_page(
                url,
                session,
                selenium_driver=selenium_driver,
                use_selenium=use_selenium,
            )

            if result:
                results.append(result)
                slug = result["slug"]
                out_path = OUTPUT_DIR / f"{slug}.json"
                with open(out_path, "w", encoding="utf-8") as f:
                    json.dump(result, f, ensure_ascii=False, indent=2)
                print(f"    Saved: {out_path.name}")

                # Discover more URLs from this page
                new_discovered = discover_urls_from_results([result])
                for nd in new_discovered:
                    if nd not in all_discovered:
                        all_discovered.add(nd)
                        if nd not in crawled_urls:
                            new_urls.append(nd)

            print()
            time.sleep(DELAY_BETWEEN_REQUESTS)
    else:
        print("  No additional pages discovered.")
    print()

    # --- Phase 3: Generate enhanced summary and report ---
    print("[Phase 3] Generating enhanced summary and report...")

    summary = generate_enhanced_summary(
        results, sorted(all_discovered), robots_analysis, all_sitemap_urls
    )

    summary_path = OUTPUT_DIR / "_enhanced_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {summary_path.name}")

    report_md = generate_enhanced_report(
        results, summary, robots_analysis, all_sitemap_urls
    )
    report_path = OUTPUT_DIR / "_enhanced_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"  Saved: {report_path.name}")

    # --- Cleanup Selenium ---
    if selenium_driver is not None:
        try:
            selenium_driver.quit()
            print("[Selenium] Driver closed.")
        except Exception:
            pass

    # --- Final summary ---
    print()
    print("=== Enhanced Crawl Complete ===")
    print(f"Pages crawled: {len(results)}")
    print(f"Total internal links: {summary['total_internal_links']}")
    print(f"Total external links: {summary['total_external_links']}")
    print(f"Pages with structured data: {len(summary['pages_with_structured_data'])}")
    print(
        f"Pages without structured data: {len(summary['pages_without_structured_data'])}"
    )
    print(f"Average GEO Score: {summary.get('average_geo_score', 0)}/100")

    sel_needed = summary.get("pages_needing_selenium", [])
    sel_failed = summary.get("pages_selenium_failed", [])
    print(f"Pages needing Selenium: {len(sel_needed)}")
    print(f"Pages where Selenium failed: {len(sel_failed)}")

    sitemap_count = summary.get("sitemap_url_count", 0)
    if sitemap_count:
        print(f"Sitemap URLs found: {sitemap_count}")

    uncrawled_count = len(summary.get("discovered_urls_not_crawled", []))
    if uncrawled_count:
        print(f"Discovered but not crawled: {uncrawled_count} URLs")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
