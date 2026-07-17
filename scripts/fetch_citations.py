"""
Fetch Google Scholar citation count for Ji-Zhe Zhou.
Runs on GitHub Actions every 8 hours. No external dependencies.
"""
import json
import re
import sys
import urllib.request
from datetime import datetime, timezone

SCHOLAR_URL = "https://scholar.google.com/citations?hl=en&user=-cNWmJMAAAAJ"
OUTPUT_FILE = "citations.json"


def fetch_html(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_count(html: str) -> int | None:
    patterns = [
        r'"cites":\s*(\d+)',
        r'<td[^>]+class="gsc_rsb_std"[^>]*>\s*(\d[\d,]*)\s*</td>',
        r"(\d[\d,]+)\s*(?:total citations|citations)",
        r"cited\s+by\s+(\d[\d,]*)",
    ]
    for pat in patterns:
        m = re.search(pat, html, re.IGNORECASE)
        if m:
            n = int(m.group(1).replace(",", ""))
            if n > 0:
                return n
    return None


def main():
    print(f"Fetching: {SCHOLAR_URL}")
    try:
        html = fetch_html(SCHOLAR_URL)
    except Exception as e:
        print(f"Fetch failed: {e}", file=sys.stderr)
        sys.exit(1)

    count = parse_count(html)
    if count is None:
        print("Could not parse citation count from HTML.", file=sys.stderr)
        # Save a debug snippet for troubleshooting
        print("HTML snippet (first 2000 chars):", html[:2000], file=sys.stderr)
        sys.exit(1)

    now = datetime.now(timezone.utc).isoformat()
    data = {"count": count, "updated": now}
    with open(OUTPUT_FILE, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")

    print(f"Written: {count:,} citations → {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
