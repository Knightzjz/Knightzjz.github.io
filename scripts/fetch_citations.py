"""
Fetch citation count via Semantic Scholar API (free, no auth, no IP blocking).
Replaces Google Scholar scraping which gets CAPTCHA-blocked on GitHub Actions.
"""
import json
import sys
import urllib.request
from datetime import datetime, timezone

# Semantic Scholar author ID (from the profile URL)
AUTHOR_ID = "2238645"
API_URL = f"https://api.semanticscholar.org/graph/v1/author/{AUTHOR_ID}?fields=citationCount"
OUTPUT_FILE = "citations.json"


def main():
    print(f"Fetching: {API_URL}")
    req = urllib.request.Request(API_URL, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Fetch failed: {e}", file=sys.stderr)
        sys.exit(1)

    count = data.get("citationCount")
    if count is None or count < 0:
        print(f"Invalid citationCount in response: {data}", file=sys.stderr)
        sys.exit(1)

    now = datetime.now(timezone.utc).isoformat()
    out = {"count": count, "updated": now, "source": "Semantic Scholar"}
    with open(OUTPUT_FILE, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")

    print(f"Written: {count:,} citations -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
