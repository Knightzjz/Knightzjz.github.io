"""
Fetch the real Google Scholar citation count.

Primary source: SerpAPI (google_scholar_author engine) — uses residential
proxies, so it works from GitHub Actions IPs that Scholar itself blocks.

Fallback: a direct GET of the public Scholar profile page (works from
residential / local IPs; usually blocked from GitHub Actions IPs, but lets
the script also succeed when run locally by hand).

On total failure the previous citations.json is preserved and the step exits
0 with a ::warning:: annotation (no red X), so the site keeps the last-known
value instead of erroring every run.
"""
import json
import os
import re
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

# Google Scholar author ID (from the profile URL)
SCHOLAR_AUTHOR_ID = "-cNWmJMAAAAJ"
OUTPUT_FILE = "citations.json"
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36")


def _get(url, timeout=20):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode("utf-8", "replace")


def fetch_via_serpapi():
    """Return (count, h_index, i10_index) or raise RuntimeError with the reason."""
    api_key = os.environ.get("SERPAPI_KEY")
    if not api_key:
        raise RuntimeError("SERPAPI_KEY env var not set")
    params = urllib.parse.urlencode({
        "engine": "google_scholar_author",
        "author_id": SCHOLAR_AUTHOR_ID,
        "api_key": api_key,
        "hl": "en",
    })
    data = json.loads(_get(f"https://serpapi.com/search.json?{params}"))
    if "error" in data:
        raise RuntimeError(f"SerpAPI error: {data['error']}")
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
        raise RuntimeError(
            f"citation count not in SerpAPI response (keys={list(data.keys())})")
    return count, h_index, i10_index


def fetch_via_direct():
    """Scrape the public Scholar profile page. Return (count, h, i10) or raise."""
    url = f"https://scholar.google.com/citations?user={SCHOLAR_AUTHOR_ID}&hl=en"
    html = _get(url)
    vals = [int(v) for v in re.findall(r'gsc_rsb_std">(\d+)', html)]
    # Page order: citations_all, citations_since, h_all, h_since, i10_all, i10_since
    if len(vals) < 5:
        raise RuntimeError(
            f"could not parse Scholar page (got {len(vals)} numbers; "
            "likely blocked/captcha from this IP)")
    return vals[0], vals[2], vals[4]


def main():
    # Missing key = config error (not a transient API issue). Fail loudly so it
    # is noticed — GitHub emails on scheduled-workflow failure. A transient
    # SerpAPI/captcha error below is handled softly instead (keep old + warn).
    if not os.environ.get("SERPAPI_KEY"):
        print("ERROR: SERPAPI_KEY secret is not set for this repo. Add it under "
              "Settings -> Secrets and variables -> Actions -> New repository secret.",
              file=sys.stderr)
        sys.exit(1)

    result = None
    errors = []
    for name, fn in (("SerpAPI", fetch_via_serpapi), ("direct", fetch_via_direct)):
        try:
            result = fn()
            print(f"{name}: OK -> {result[0]:,} citations "
                  f"(h={result[1]}, i10={result[2]})")
            break
        except Exception as e:
            print(f"{name}: {e}", file=sys.stderr)
            errors.append(f"{name}: {e}")

    if result is None:
        # Preserve last-known data; surface as a warning, not a hard failure.
        print("::warning::All Scholar sources failed; keeping previous "
              "citations.json. " + " | ".join(errors))
        sys.exit(0)

    count, h_index, i10_index = result

    # Skip writing if values are unchanged (avoids unnecessary bot commits)
    if Path(OUTPUT_FILE).exists():
        try:
            old = json.loads(Path(OUTPUT_FILE).read_text("utf-8"))
            if (old.get("count") == count
                    and old.get("h_index") == h_index
                    and old.get("i10_index") == i10_index):
                print(f"Unchanged: {count:,} citations — skipping write")
                return
        except Exception:
            pass  # If old file is corrupt, proceed to write

    out = {
        "count": count,
        "h_index": h_index,
        "i10_index": i10_index,
        "updated": datetime.now(timezone.utc).isoformat(),
        "source": "Google Scholar",
    }
    with open(OUTPUT_FILE, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")
    print(f"Written: {count:,} citations (h={h_index}, i10={i10_index}) -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
