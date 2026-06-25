#!/usr/bin/env python3
"""
update_publications.py
----------------------
Fetches Dr Aakash Bansal's publications from Google Scholar and writes
publications.json, which the website renders. Designed to run on a schedule
(see .github/workflows/update-publications.yml).

Usage:
    python update_publications.py

Behaviour / safety:
- If Scholar returns no publications (e.g. rate-limited or blocked), the script
  exits with a non-zero code WITHOUT overwriting publications.json, so the site
  keeps its last good data.
- Set SCHOLARLY_USE_PROXY=1 to route requests through free proxies (helps when
  Google blocks the runner's IP, but free proxies are slow/unreliable).
"""

import json
import os
import sys
import time
import datetime

SCHOLAR_ID = "VBRbQlYAAAAJ"  # Aakash Bansal's Google Scholar author ID
OUTPUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "publications.json")

# venue keywords that indicate a conference paper (otherwise treated as journal)
CONFERENCE_KEYWORDS = [
    "conference", "symposium", "workshop", "proceedings", "colloquium",
    "eucap", "mapcon", "iwat", "comcas", "splitech", "lacap",
    "usnc", "ursi", "ap-s", "ap/s", "radio and antenna days",
    "icsc", "icpeices", "space, aerospace", "meeting",
]


def classify(venue: str) -> str:
    v = (venue or "").lower()
    return "conference" if any(k in v for k in CONFERENCE_KEYWORDS) else "journal"


def tidy_authors(raw: str) -> str:
    # Scholar returns "A Bansal and C Panagamuwa and W Whittow"
    if not raw:
        return ""
    return ", ".join(a.strip() for a in raw.split(" and ") if a.strip())


def best_url(pub: dict) -> str:
    bib = pub.get("bib", {})
    return (
        pub.get("pub_url")
        or pub.get("eprint_url")
        or bib.get("url")
        or (f"https://scholar.google.com/citations?view_op=view_citation&hl=en&user={SCHOLAR_ID}&citation_for_view={pub.get('author_pub_id')}"
            if pub.get("author_pub_id") else "")
    )


def main() -> int:
    from scholarly import scholarly

    if os.environ.get("SCHOLARLY_USE_PROXY") == "1":
        try:
            from scholarly import ProxyGenerator
            pg = ProxyGenerator()
            if pg.FreeProxies():
                scholarly.use_proxy(pg)
                print("Using free proxies.")
        except Exception as e:  # noqa: BLE001
            print(f"Proxy setup failed, continuing without: {e}")

    print(f"Fetching author {SCHOLAR_ID} ...")
    try:
        author = scholarly.search_author_id(SCHOLAR_ID)
        author = scholarly.fill(author, sections=["basics", "indices", "publications"])
    except Exception as e:  # noqa: BLE001
        print(f"ERROR: could not fetch author profile: {e}", file=sys.stderr)
        return 1

    raw_pubs = author.get("publications", []) or []
    print(f"Found {len(raw_pubs)} publication stubs; fetching details ...")

    publications = []
    for i, stub in enumerate(raw_pubs, 1):
        bib = stub.get("bib", {})
        title = bib.get("title", "").strip()
        try:
            full = scholarly.fill(stub)
            bib = full.get("bib", bib)
            url = best_url(full)
            citations = int(full.get("num_citations", stub.get("num_citations", 0)) or 0)
        except Exception as e:  # noqa: BLE001
            print(f"  [{i}] detail fetch failed for '{title[:50]}': {e}")
            url = best_url(stub)
            citations = int(stub.get("num_citations", 0) or 0)

        venue = (
            bib.get("journal")
            or bib.get("conference")
            or bib.get("venue")
            or bib.get("citation")
            or ""
        ).strip()
        year_raw = str(bib.get("pub_year", "")).strip()
        year = int(year_raw) if year_raw.isdigit() else None

        if not title:
            continue

        publications.append({
            "title": title,
            "authors": tidy_authors(bib.get("author", "")),
            "venue": venue,
            "year": year,
            "citations": citations,
            "type": classify(venue),
            "url": url,
        })
        time.sleep(1.0)  # be polite to Scholar

    if not publications:
        print("ERROR: no publications parsed — leaving existing file untouched.", file=sys.stderr)
        return 2

    publications.sort(key=lambda p: (p["year"] or 0, p["citations"]), reverse=True)

    payload = {
        "updated": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "source": "Google Scholar",
        "profile": {
            "name": author.get("name", "Aakash Bansal"),
            "scholar_id": SCHOLAR_ID,
            "total_citations": author.get("citedby"),
            "h_index": author.get("hindex"),
            "i10_index": author.get("i10index"),
        },
        "count": len(publications),
        "publications": publications,
    }

    with open(OUTPUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"Wrote {len(publications)} publications to {OUTPUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
