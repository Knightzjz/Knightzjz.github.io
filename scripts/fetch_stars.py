"""
Fetch GitHub star counts for all repos linked on the homepage.
Uses the built-in GITHUB_TOKEN in GitHub Actions (5000 req/hour).
No SerpAPI or external proxy needed — GitHub API is free and public.
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

REPOS = [
    "venus-guangjian/SICA_OpenMMSec",
    "scu-zjz/RITA",
    "SunnyHaze/IML-ViT",
    "scu-zjz/ForensicHub",
    "scu-zjz/SparseViT",
    "scu-zjz/IMDLBenCo",
    "Knightzjz/NCL-IML",
]
OUTPUT_FILE = "stars.json"


def fetch_stars(repo, token):
    url = f"https://api.github.com/repos/{repo}"
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("stargazers_count")
    except Exception as e:
        print(f"  WARN: {repo} — {e}", file=sys.stderr)
        return None


def main():
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN", "")

    print("Fetching GitHub star counts...")
    repos = {}
    for repo in REPOS:
        count = fetch_stars(repo, token)
        if count is not None:
            repos[repo] = count
            print(f"  {repo}: {count} stars")
        else:
            print(f"  {repo}: FAILED (skipped)")

    if not repos:
        print("ERROR: No repos fetched successfully", file=sys.stderr)
        sys.exit(1)

    now = datetime.now(timezone.utc).isoformat()
    out = {"repos": repos, "updated": now}
    with open(OUTPUT_FILE, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")

    print(f"\nWritten {len(repos)}/{len(REPOS)} repos -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
