#!/usr/bin/env python3
"""
GEO Readiness Scorecard Analyzer

Reads crawled JSON data from data/crawled/ and produces a GEO readiness
scorecard scoring each page on 5 dimensions (Answerability, Proof, Fan-out,
Crawlability, Trust) with 0-5 points each, for a total of 25.

Usage:
    python scripts/analyze_geo_readiness.py
    python scripts/analyze_geo_readiness.py --input-dir data/crawled
    python scripts/analyze_geo_readiness.py --output data/crawled/_geo_scorecard.json
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------------------------
# Helpers to safely extract fields (handles both old and new JSON formats)
# ---------------------------------------------------------------------------

def _get(page: dict, key: str, default=None):
    """Return page[key] if present and not None, else default."""
    val = page.get(key)
    return val if val is not None else default


def _text_between_h1_and_first_h2(page: dict) -> str:
    """
    Fallback for answer_first_block: extract text between H1 and first H2
    from the raw text_content using heading texts as anchors.
    """
    headings = _get(page, "headings", [])
    text = _get(page, "text_content", "")
    if not text or not headings:
        return ""

    h1_texts = [h["text"] for h in headings if h.get("tag") == "h1" and h.get("text")]
    h2_texts = [h["text"] for h in headings if h.get("tag") == "h2" and h.get("text")]

    if not h1_texts:
        return ""

    h1_text = h1_texts[0]
    h1_pos = text.find(h1_text)
    if h1_pos == -1:
        return ""

    start = h1_pos + len(h1_text)

    if h2_texts:
        h2_pos = text.find(h2_texts[0], start)
        if h2_pos != -1:
            return text[start:h2_pos].strip()

    # No H2 found -- take a generous block after H1
    return text[start:start + 500].strip()


def _compute_img_alt_ratio(page: dict) -> float:
    """Compute image alt coverage ratio, handling both formats."""
    iac = _get(page, "img_alt_coverage")
    if isinstance(iac, dict) and iac.get("total", 0) > 0:
        return iac.get("ratio", 0.0)

    # Old format: compute from images list
    images = _get(page, "images", [])
    if not images:
        return 0.0
    with_alt = sum(1 for img in images if img.get("alt", "").strip())
    return with_alt / len(images)


# ---------------------------------------------------------------------------
# Scoring functions
# ---------------------------------------------------------------------------

def score_answerability(page: dict) -> tuple[int, list[str]]:
    score = 0
    details = []

    h1_count = _get(page, "h1_count", 0)
    if h1_count >= 1:
        score += 1
        details.append("H1 exists")

    title = _get(page, "title", "")
    if title and title.strip():
        score += 1
        details.append("title exists")

    # Answer-first block
    afb = _get(page, "answer_first_block", "")
    if not afb:
        afb = _text_between_h1_and_first_h2(page)

    if afb and len(afb) >= 100:
        score += 1
        details.append(f"answer block >= 100 chars ({len(afb)} chars)")

    if afb and len(afb) >= 200:
        score += 1
        details.append(f"answer block >= 200 chars")

    meta_desc = _get(page, "meta_description", "")
    if meta_desc and len(meta_desc) >= 50:
        score += 1
        details.append("meta_description >= 50 chars")

    return score, details


def score_proof(page: dict) -> tuple[int, list[str]]:
    score = 0
    details = []

    ext_links = _get(page, "external_links", [])
    n_ext = len(ext_links)

    if n_ext >= 1:
        score += 1
        details.append(f"{n_ext} external link(s)")
    if n_ext >= 3:
        score += 1
        details.append(f">= 3 external links")
    if n_ext >= 5:
        score += 1
        details.append(f">= 5 external links")

    text = _get(page, "text_content", "")

    # Statistics patterns: number + unit
    stat_pattern = re.compile(
        r'\d+[\.,]?\d*\s*(%|명|건|시간|만|억|개|회|건|년|월|달|배|위|조원|백만|천)'
    )
    if stat_pattern.search(text):
        score += 1
        details.append("contains statistics (number+unit)")

    # Citation patterns
    citation_pattern = re.compile(
        r'출처|근거|연구|조사|보고서|survey|report|according|연구결과|통계|데이터에\s*따르면',
        re.IGNORECASE,
    )
    if citation_pattern.search(text):
        score += 1
        details.append("contains citation keywords")

    return score, details


def score_fanout(page: dict) -> tuple[int, list[str]]:
    score = 0
    details = []

    subheading_count = _get(page, "subheading_count")
    if subheading_count is None:
        # Old format: count h2/h3/h4 from headings list
        headings = _get(page, "headings", [])
        subheading_count = sum(1 for h in headings if h.get("level", 0) >= 2)

    if subheading_count >= 2:
        score += 1
        details.append(f"{subheading_count} subheading(s)")
    if subheading_count >= 5:
        score += 1
        details.append(f">= 5 subheadings")

    faq_count = _get(page, "faq_count", 0)
    text = _get(page, "text_content", "")
    faq_pattern = re.compile(r'FAQ|자주\s*묻는\s*질문|Q\s*[.:]|Q\d|질문과\s*답변', re.IGNORECASE)
    if faq_count >= 1 or faq_pattern.search(text):
        score += 1
        details.append("FAQ content detected")

    int_links = _get(page, "internal_links", [])
    n_int = len(int_links)

    if n_int >= 3:
        score += 1
        details.append(f"{n_int} internal link(s)")
    if n_int >= 5:
        score += 1
        details.append(f">= 5 internal links")

    return score, details


def score_crawlability(page: dict) -> tuple[int, list[str]]:
    score = 0
    details = []

    title = _get(page, "title", "")
    if title and title.strip():
        score += 1
        details.append("title")

    meta_desc = _get(page, "meta_description", "")
    if meta_desc and meta_desc.strip():
        score += 1
        details.append("meta_desc")

    canonical = _get(page, "canonical", "")
    if canonical and canonical.strip():
        score += 1
        details.append("canonical")

    has_sd = _get(page, "has_structured_data", False)
    json_ld = _get(page, "json_ld", [])
    schema_md = _get(page, "schema_microdata", [])
    if has_sd or json_ld or schema_md:
        score += 1
        details.append("structured_data")

    og = _get(page, "og_tags", {})
    if og.get("og:title") and og.get("og:description"):
        score += 1
        details.append("og:title + og:description")

    return score, details


def score_trust(page: dict) -> tuple[int, list[str]]:
    score = 0
    details = []

    rendered = _get(page, "rendered_with", "requests")
    text_len = _get(page, "text_length", 0)
    if rendered != "selenium" or text_len > 500:
        score += 1
        details.append("SSR page" if rendered != "selenium" else "text > 500 despite CSR")

    text = _get(page, "text_content", "")

    date_pattern = re.compile(
        r'202[0-9]|발행일|작성일|업데이트|updated|published|발행\s+\d{4}',
        re.IGNORECASE,
    )
    if date_pattern.search(text):
        score += 1
        details.append("has date reference")

    author_pattern = re.compile(
        r'작성자|저자|편집|감수|editor|author|기자|집필',
        re.IGNORECASE,
    )
    if author_pattern.search(text):
        score += 1
        details.append("has author/editor reference")

    canonical = _get(page, "canonical", "")
    meta_robots = _get(page, "meta_robots", "")
    if canonical and "noindex" not in (meta_robots or "").lower():
        score += 1
        details.append("canonical without noindex")

    alt_ratio = _compute_img_alt_ratio(page)
    if alt_ratio > 0.5:
        score += 1
        details.append(f"img alt ratio {alt_ratio:.0%}")

    return score, details


# ---------------------------------------------------------------------------
# Main analysis
# ---------------------------------------------------------------------------

def analyze_page(page: dict) -> dict:
    """Score a single page and return its result record."""
    ans_score, ans_details = score_answerability(page)
    prf_score, prf_details = score_proof(page)
    fan_score, fan_details = score_fanout(page)
    crw_score, crw_details = score_crawlability(page)
    trs_score, trs_details = score_trust(page)

    total = ans_score + prf_score + fan_score + crw_score + trs_score

    return {
        "url": page.get("url", ""),
        "slug": page.get("slug", ""),
        "scores": {
            "answerability": ans_score,
            "proof": prf_score,
            "fan_out": fan_score,
            "crawlability": crw_score,
            "trust": trs_score,
            "total": total,
        },
        "details": {
            "answerability": ans_details,
            "proof": prf_details,
            "fan_out": fan_details,
            "crawlability": crw_details,
            "trust": trs_details,
        },
        "rendered_with": _get(page, "rendered_with", "requests"),
        "text_length": _get(page, "text_length", 0),
    }


def compute_summary(results: list[dict]) -> dict:
    """Compute aggregate summary across all scored pages."""
    n = len(results)
    if n == 0:
        return {"by_dimension": {}, "top_issues": []}

    dims = ["answerability", "proof", "fan_out", "crawlability", "trust"]
    by_dim = {}
    for dim in dims:
        vals = [r["scores"][dim] for r in results]
        by_dim[dim] = {
            "avg": round(sum(vals) / n, 1),
            "min": min(vals),
            "max": max(vals),
        }

    # Detect top issues
    issues = []

    # Answerability: pages lacking answer-first block (score < 3 means no answer block)
    no_answer = sum(1 for r in results if r["scores"]["answerability"] < 3)
    if no_answer > 0:
        issues.append(f"{no_answer}/{n} pages lack Answer-first block (answerability < 3)")

    # Proof: pages with < 3 external links
    weak_proof = sum(1 for r in results if r["scores"]["proof"] < 2)
    if weak_proof > 0:
        issues.append(f"{weak_proof}/{n} pages have weak Proof (score < 2)")

    # Fan-out: low subheading/FAQ
    low_fanout = sum(1 for r in results if r["scores"]["fan_out"] < 2)
    if low_fanout > 0:
        issues.append(f"{low_fanout}/{n} pages have low Fan-out (score < 2)")

    # Crawlability: missing basic SEO
    low_crawl = sum(1 for r in results if r["scores"]["crawlability"] < 3)
    if low_crawl > 0:
        issues.append(f"{low_crawl}/{n} pages have low Crawlability (score < 3)")

    # CSR pages
    csr_pages = sum(1 for r in results if r["rendered_with"] == "selenium")
    if csr_pages > 0:
        issues.append(f"{csr_pages}/{n} pages are CSR-rendered (selenium)")

    # Trust: low trust
    low_trust = sum(1 for r in results if r["scores"]["trust"] < 2)
    if low_trust > 0:
        issues.append(f"{low_trust}/{n} pages have low Trust (score < 2)")

    # Pages with very low total
    critical = sum(1 for r in results if r["scores"]["total"] <= 8)
    if critical > 0:
        issues.append(f"{critical}/{n} pages score <= 8/25 (critical)")

    return {
        "by_dimension": by_dim,
        "top_issues": issues,
    }


def print_report(results: list[dict], summary: dict) -> None:
    """Print a human-readable console report."""
    n = len(results)
    if n == 0:
        print("No pages to analyze.")
        return

    avg = sum(r["scores"]["total"] for r in results) / n

    print()
    print("=== GEO Readiness Scorecard ===")
    print(f"Pages analyzed: {n}")
    print(f"Average score:  {avg:.1f} / 25")
    print()

    header = f"  {'Page':<45} {'Answer':>6} {'Proof':>5} {'Fan-out':>7} {'Crawl':>5} {'Trust':>5} {'TOTAL':>5}"
    print(header)
    print("  " + "-" * (len(header) - 2))

    for r in results:
        slug = "/" + r["slug"] if r["slug"] else r["url"]
        if len(slug) > 43:
            slug = slug[:40] + "..."

        s = r["scores"]
        flag = ""
        if r["rendered_with"] == "selenium":
            flag = "  [CSR]"
        elif s["total"] <= 8:
            flag = "  [!]"

        print(
            f"  {slug:<45} {s['answerability']:>6} {s['proof']:>5} "
            f"{s['fan_out']:>7} {s['crawlability']:>5} {s['trust']:>5} "
            f"{s['total']:>5}{flag}"
        )

    print()
    if summary["top_issues"]:
        print("Top Issues:")
        for i, issue in enumerate(summary["top_issues"], 1):
            print(f"  {i}. {issue}")
        print()

    # Dimension averages
    print("Dimension Averages:")
    for dim, stats in summary["by_dimension"].items():
        bar_len = int(stats["avg"] * 4)  # up to 20 chars for score 5
        bar = "#" * bar_len + "." * (20 - bar_len)
        print(f"  {dim:<15} {stats['avg']:>4.1f}  [{bar}]  (min={stats['min']}, max={stats['max']})")
    print()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Analyze crawled pages for GEO readiness"
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=PROJECT_ROOT / "data" / "crawled",
        help="Directory containing crawled JSON files (default: data/crawled/)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output JSON path (default: <input-dir>/_geo_scorecard.json)",
    )
    args = parser.parse_args()

    input_dir = args.input_dir.resolve()
    output_path = (args.output or (input_dir / "_geo_scorecard.json")).resolve()

    if not input_dir.is_dir():
        print(f"ERROR: Input directory not found: {input_dir}", file=sys.stderr)
        sys.exit(1)

    # Collect JSON files, skip those starting with _
    json_files = sorted(
        f for f in input_dir.glob("*.json")
        if not f.name.startswith("_")
    )

    if not json_files:
        print(f"ERROR: No JSON files found in {input_dir}", file=sys.stderr)
        sys.exit(1)

    print(f"Found {len(json_files)} page file(s) in {input_dir}")

    # Load and score each page
    results = []
    for jf in json_files:
        try:
            with open(jf, "r", encoding="utf-8") as fh:
                page = json.load(fh)
        except (json.JSONDecodeError, OSError) as exc:
            print(f"  WARNING: Skipping {jf.name}: {exc}", file=sys.stderr)
            continue

        result = analyze_page(page)
        results.append(result)

    if not results:
        print("ERROR: No valid pages could be analyzed.", file=sys.stderr)
        sys.exit(1)

    # Sort by total score ascending (worst first = highest priority)
    results.sort(key=lambda r: r["scores"]["total"])

    # Assign priority rank
    for rank, r in enumerate(results, 1):
        r["priority_rank"] = rank

    # Compute summary
    summary = compute_summary(results)
    avg_score = round(sum(r["scores"]["total"] for r in results) / len(results), 1)

    # Build output JSON
    output_data = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_pages": len(results),
        "average_score": avg_score,
        "pages": results,
        "summary": summary,
    }

    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        json.dump(output_data, fh, ensure_ascii=False, indent=2)

    print(f"Scorecard written to: {output_path}")

    # Print console report
    print_report(results, summary)


if __name__ == "__main__":
    main()
