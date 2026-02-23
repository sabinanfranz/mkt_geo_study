"""
Crawl b2b.fastcampus.co.kr key pages and save structured data.

Usage:
    python scripts/crawl_b2b.py
    python scripts/crawl_b2b.py --max-pages 30

Output:
    data/crawled/{slug}.json   -- per-page structured data
    data/crawled/_summary.json -- crawl summary
    data/crawled/_report.md    -- human-readable analysis
"""

from __future__ import annotations

import argparse
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup, Comment, Tag

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

BASE_DOMAIN = "b2b.fastcampus.co.kr"
BASE_URL = f"https://{BASE_DOMAIN}"

SEED_URLS = [
    f"{BASE_URL}/",
    f"{BASE_URL}/service_custom",
    f"{BASE_URL}/refer_customer",
    f"{BASE_URL}/resource_insight_aiforwork",
    f"{BASE_URL}/resource_seminar_onlinelearning",
    f"{BASE_URL}/service_aicamp_b2bproposalwai",
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
DELAY_BETWEEN_REQUESTS = 1.5  # seconds

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "crawled"

# Tags to remove when extracting text content
REMOVE_TAGS = {"script", "style", "noscript", "svg", "iframe", "head"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def url_to_slug(url: str) -> str:
    """Convert a URL to a filesystem-safe slug for the JSON filename."""
    parsed = urlparse(url)
    path = parsed.path.strip("/")
    if not path:
        return "index"
    # Replace slashes and special chars with underscores
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
    # Relative links or same domain
    if not parsed.netloc and not parsed.scheme:
        return True
    return parsed.netloc == BASE_DOMAIN


def normalize_url(href: str, page_url: str) -> str | None:
    """Normalize a link to an absolute URL, or return None if invalid."""
    if not href:
        return None
    # Skip javascript:, mailto:, tel:, #anchors
    if href.startswith(("javascript:", "mailto:", "tel:", "#")):
        return None
    absolute = urljoin(page_url, href)
    parsed = urlparse(absolute)
    # Only http(s)
    if parsed.scheme not in ("http", "https"):
        return None
    # Remove fragment
    clean = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    # Remove trailing slash for consistency (except root)
    if clean != f"{BASE_URL}/" and clean.endswith("/"):
        clean = clean.rstrip("/")
    return clean


def extract_text_content(soup: BeautifulSoup) -> str:
    """Extract cleaned main text content from page, removing scripts/styles."""
    # Work on a copy so we don't mutate the original
    body = soup.find("body")
    if not body:
        return ""

    # Create a copy
    from copy import copy
    body_copy = copy(body)

    # Remove unwanted tags
    for tag_name in REMOVE_TAGS:
        for tag in body_copy.find_all(tag_name):
            tag.decompose()

    # Remove HTML comments
    for comment in body_copy.find_all(string=lambda text: isinstance(text, Comment)):
        comment.extract()

    # Get text
    text = body_copy.get_text(separator="\n", strip=True)
    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Page Crawler
# ---------------------------------------------------------------------------


def crawl_page(url: str, session: requests.Session) -> dict[str, Any] | None:
    """Crawl a single page and return structured data, or None on failure."""
    print(f"  Fetching: {url}")
    try:
        resp = session.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        print(f"    [ERROR] Timeout for {url}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"    [ERROR] HTTP {e.response.status_code} for {url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"    [ERROR] Request failed for {url}: {e}")
        return None

    # Ensure we're dealing with HTML
    content_type = resp.headers.get("Content-Type", "")
    if "text/html" not in content_type and "application/xhtml" not in content_type:
        print(f"    [SKIP] Non-HTML content type: {content_type}")
        return None

    soup = BeautifulSoup(resp.text, "html.parser")

    # --- Title ---
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else None

    # --- Meta description ---
    meta_desc_tag = soup.find("meta", attrs={"name": "description"})
    meta_description = meta_desc_tag.get("content", "").strip() if meta_desc_tag else None

    # --- Meta keywords ---
    meta_kw_tag = soup.find("meta", attrs={"name": "keywords"})
    meta_keywords = meta_kw_tag.get("content", "").strip() if meta_kw_tag else None

    # --- OG tags ---
    og_tags = {}
    for og in soup.find_all("meta", attrs={"property": re.compile(r"^og:")}):
        prop = og.get("property", "")
        content = og.get("content", "")
        if prop and content:
            og_tags[prop] = content

    # --- Canonical URL ---
    canonical_tag = soup.find("link", attrs={"rel": "canonical"})
    canonical = canonical_tag.get("href", "").strip() if canonical_tag else None

    # --- Headings ---
    headings = []
    for level in range(1, 7):
        tag_name = f"h{level}"
        for h in soup.find_all(tag_name):
            text = h.get_text(strip=True)
            if text:
                headings.append({"level": level, "tag": tag_name, "text": text})

    # --- JSON-LD structured data ---
    json_ld_scripts = []
    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.string or "")
            json_ld_scripts.append(data)
        except (json.JSONDecodeError, TypeError):
            pass

    # --- Schema.org microdata (itemscope) ---
    schema_microdata = []
    for el in soup.find_all(attrs={"itemscope": True}):
        item_type = el.get("itemtype", "")
        if item_type:
            schema_microdata.append(item_type)

    # --- RDFa schema.org ---
    rdfa_types = []
    for el in soup.find_all(attrs={"typeof": True}):
        rdfa_types.append(el.get("typeof", ""))

    # --- Links ---
    internal_links = []
    external_links = []
    seen_internal = set()
    seen_external = set()

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

    # --- Images ---
    images = []
    for img in soup.find_all("img"):
        src = img.get("src", "").strip()
        alt = img.get("alt", "").strip()
        if src:
            abs_src = normalize_url(src, url) or src
            images.append({"src": abs_src, "alt": alt})

    # --- Main text content ---
    text_content = extract_text_content(soup)

    # --- Nav elements (for site structure discovery) ---
    nav_links = []
    for nav in soup.find_all("nav"):
        for a in nav.find_all("a", href=True):
            href = a.get("href", "").strip()
            normalized = normalize_url(href, url)
            if normalized and is_internal_link(href):
                link_text = a.get_text(strip=True)
                nav_links.append({"url": normalized, "text": link_text})

    # Also check header for navigation
    for header in soup.find_all("header"):
        for a in header.find_all("a", href=True):
            href = a.get("href", "").strip()
            normalized = normalize_url(href, url)
            if normalized and is_internal_link(href):
                link_text = a.get_text(strip=True)
                nav_links.append({"url": normalized, "text": link_text})

    # Deduplicate nav_links
    seen_nav = set()
    unique_nav = []
    for nl in nav_links:
        if nl["url"] not in seen_nav:
            seen_nav.add(nl["url"])
            unique_nav.append(nl)
    nav_links = unique_nav

    result = {
        "url": url,
        "slug": url_to_slug(url),
        "crawled_at": datetime.now(timezone.utc).isoformat(),
        "status_code": resp.status_code,
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
        "text_content": text_content[:50000],  # Cap at 50K chars
        "text_length": len(text_content),
        "h1_count": sum(1 for h in headings if h["level"] == 1),
        "has_structured_data": len(json_ld_scripts) > 0 or len(schema_microdata) > 0,
    }

    print(f"    OK - title: {title}")
    print(f"    Headings: {len(headings)}, Internal links: {len(internal_links)}, "
          f"External links: {len(external_links)}, Images: {len(images)}")
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
    discovered = set()
    for r in results:
        # Prioritize nav links (site navigation)
        for link in r.get("nav_links", []):
            url = link["url"]
            parsed = urlparse(url)
            if parsed.netloc == BASE_DOMAIN:
                discovered.add(url)
        # Also consider all internal links
        for link in r.get("internal_links", []):
            url = link["url"]
            parsed = urlparse(url)
            if parsed.netloc == BASE_DOMAIN:
                discovered.add(url)
    return sorted(discovered)


# ---------------------------------------------------------------------------
# Report Generation
# ---------------------------------------------------------------------------


def generate_summary(results: list[dict], all_discovered: list[str]) -> dict:
    """Generate _summary.json content."""
    total_internal = sum(len(r.get("internal_links", [])) for r in results)
    total_external = sum(len(r.get("external_links", [])) for r in results)

    # Build navigation structure from nav_links
    nav_structure = {}
    for r in results:
        for nl in r.get("nav_links", []):
            nav_structure[nl["url"]] = nl.get("text", "")

    return {
        "crawl_timestamp": datetime.now(timezone.utc).isoformat(),
        "base_domain": BASE_DOMAIN,
        "page_count": len(results),
        "crawled_urls": [r["url"] for r in results],
        "total_internal_links": total_internal,
        "total_external_links": total_external,
        "discovered_urls_not_crawled": [
            u for u in all_discovered
            if u not in {r["url"] for r in results}
        ],
        "navigation_structure": nav_structure,
        "pages_with_structured_data": [
            r["url"] for r in results if r.get("has_structured_data")
        ],
        "pages_without_structured_data": [
            r["url"] for r in results if not r.get("has_structured_data")
        ],
    }


def generate_report(results: list[dict], summary: dict) -> str:
    """Generate _report.md content."""
    lines = []
    lines.append("# b2b.fastcampus.co.kr Crawl Report")
    lines.append("")
    lines.append(f"**Crawl Date:** {summary['crawl_timestamp']}")
    lines.append(f"**Pages Crawled:** {summary['page_count']}")
    lines.append(f"**Total Internal Links Found:** {summary['total_internal_links']}")
    lines.append(f"**Total External Links Found:** {summary['total_external_links']}")
    lines.append("")

    # --- Site Structure Analysis ---
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

    # --- Per-Page Analysis ---
    lines.append("## Per-Page Analysis")
    lines.append("")

    for r in results:
        lines.append(f"### {r.get('title', '(no title)')}")
        lines.append(f"**URL:** {r['url']}")
        lines.append(f"**Status:** {r['status_code']}")
        lines.append("")

        # Meta info
        meta_desc = r.get("meta_description")
        lines.append(f"- **Meta Description:** {meta_desc if meta_desc else 'MISSING'}")
        lines.append(f"- **Canonical:** {r.get('canonical', 'MISSING')}")
        lines.append(f"- **Text Length:** {r.get('text_length', 0)} chars")
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
                    lines.append(f"- JSON-LD #{i+1}: @type = {ld_type}")
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

    # --- Internal Link Map ---
    lines.append("## Internal Link Map")
    lines.append("")
    lines.append("Source Page -> Target Pages (internal)")
    lines.append("")
    for r in results:
        slug = r.get("slug", "unknown")
        int_links = r.get("internal_links", [])
        if int_links:
            lines.append(f"### {slug}")
            for link in int_links[:30]:  # Cap display at 30
                text = link.get("text", "(no anchor text)")
                lines.append(f"- [{text}]({link['url']})")
            if len(int_links) > 30:
                lines.append(f"- ... and {len(int_links) - 30} more")
            lines.append("")

    # --- Missing Elements Report ---
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

        if page_issues:
            issues_found = True
            lines.append(f"### {r['url']}")
            for issue in page_issues:
                lines.append(f"- [ ] {issue}")
            lines.append("")

    if not issues_found:
        lines.append("No issues found. All pages have title, meta description, H1, "
                      "and structured data.")
        lines.append("")

    # --- Uncrawled Discovered URLs ---
    uncrawled = summary.get("discovered_urls_not_crawled", [])
    if uncrawled:
        lines.append("## Discovered but Not Crawled")
        lines.append("")
        lines.append(f"Found {len(uncrawled)} additional internal URLs that were not crawled "
                      "(increase --max-pages to include them):")
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
        description="Crawl b2b.fastcampus.co.kr and save structured data."
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=20,
        help="Maximum number of pages to crawl (default: 20)",
    )
    args = parser.parse_args()

    max_pages = args.max_pages
    print(f"=== b2b.fastcampus.co.kr Crawler ===")
    print(f"Max pages: {max_pages}")
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers.update(HEADERS)

    results: list[dict] = []
    crawled_urls: set[str] = set()
    queue: list[str] = list(SEED_URLS)
    all_discovered: set[str] = set(SEED_URLS)

    # Phase 1: Crawl seed URLs
    print("[Phase 1] Crawling seed URLs...")
    print()

    while queue and len(results) < max_pages:
        url = queue.pop(0)
        if url in crawled_urls:
            continue

        crawled_urls.add(url)
        result = crawl_page(url, session)

        if result:
            results.append(result)
            # Save individual page JSON
            slug = result["slug"]
            out_path = OUTPUT_DIR / f"{slug}.json"
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"    Saved: {out_path.name}")

        print()
        time.sleep(DELAY_BETWEEN_REQUESTS)

    # Phase 2: Discover and crawl additional pages from navigation
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
            result = crawl_page(url, session)

            if result:
                results.append(result)
                # Save individual page JSON
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

    # Phase 3: Generate summary and report
    print("[Phase 3] Generating summary and report...")

    summary = generate_summary(results, sorted(all_discovered))

    # Save summary JSON
    summary_path = OUTPUT_DIR / "_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"  Saved: {summary_path.name}")

    # Save report Markdown
    report_md = generate_report(results, summary)
    report_path = OUTPUT_DIR / "_report.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)
    print(f"  Saved: {report_path.name}")

    # Final summary to stdout
    print()
    print("=== Crawl Complete ===")
    print(f"Pages crawled: {len(results)}")
    print(f"Total internal links: {summary['total_internal_links']}")
    print(f"Total external links: {summary['total_external_links']}")
    print(f"Pages with structured data: {len(summary['pages_with_structured_data'])}")
    print(f"Pages without structured data: {len(summary['pages_without_structured_data'])}")
    uncrawled_count = len(summary.get("discovered_urls_not_crawled", []))
    if uncrawled_count:
        print(f"Discovered but not crawled: {uncrawled_count} URLs")
    print(f"Output directory: {OUTPUT_DIR}")


if __name__ == "__main__":
    main()
