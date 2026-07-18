"""
Fetch Google Scholar citation count via SerpAPI.
Uses the user's free-tier API key (100 searches/month).
Runs on GitHub Actions — SerpAPI uses residential proxies so it won't be blocked.
"""
import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone

# Google Scholar author ID (from the profile URL)
SCHOLAR_AUTHOR_ID = "-cNWmJMAAAAJ"
OUTPUT_FILE = "citations.json"


def main():
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        print("ERROR: SERPAPI_KEY environment variable not set", file=sys.stderr)
        sys.exit(1)

    params = urllib.parse.urlencode({
        "engine": "google_scholar_author",
        "author_id": SCHOLAR_AUTHOR_ID,
        "api_key": api_key,
        "hl": "en",
    })
    url = f"https://serpapi.com/search.json?{params}"
    print(f"Fetching Google Scholar data via SerpAPI...")

    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Fetch failed: {e}", file=sys.stderr)
        sys.exit(1)

    if "error" in data:
        print(f"SerpAPI error: {data['error']}", file=sys.stderr)
        sys.exit(1)

    # Extract citation stats from the cited_by table
    table = data.get("cited_by", {}).get("table", [])
    count = h_index = i10_index = None
    for row in table:
        if "citations" in row:
            count = row["citations"].get("all")
        elif "h_index" in row:
            h_index = row["h_index"].get("all")
        elif "i10_index" in row:
            i10_index = row["i10_index"].get("all")

    if count is None:
        print(f"Could not find citation count in response", file=sys.stderr)
        print(f"Response keys: {list(data.keys())}", file=sys.stderr)
        sys.exit(1)

    now = datetime.now(timezone.utc).isoformat()
    out = {
        "count": count,
        "h_index": h_index,
        "i10_index": i10_index,
        "updated": now,
        "source": "Google Scholar",
    }
    with open(OUTPUT_FILE, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")

    print(f"Written: {count:,} citations (h={h_index}, i10={i10_index}) -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
