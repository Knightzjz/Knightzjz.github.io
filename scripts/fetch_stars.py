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
from pathlib import Path

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

    # Load old data — used both for unchanged-check (skip unnecessary commits)
    # and as fallback for repos that fail on this run (prevents data loss).
    output_path = Path(OUTPUT_FILE)
    old_data = {}
    if output_path.exists():
        try:
            old_data = json.loads(output_path.read_text("utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    old_repos = old_data.get("repos", {}) if isinstance(old_data, dict) else {}

    print("Fetching GitHub star counts...")
    repos = {}
    failed = []
    for repo in REPOS:
        count = fetch_stars(repo, token)
        if count is not None:
            repos[repo] = count
            print(f"  {repo}: {count} stars")
        elif repo in old_repos:
            # Preserve historical value instead of dropping the repo from output
            repos[repo] = old_repos[repo]
            failed.append(repo)
            print(f"  {repo}: FAILED — kept previous value ({old_repos[repo]})")
        else:
            failed.append(repo)
            print(f"  {repo}: FAILED — no previous value available")

    if not repos:
        print("ERROR: No repos fetched and no prior data to fall back on", file=sys.stderr)
        sys.exit(1)

    if failed:
        print(f"Warning: {len(failed)} repo(s) failed this run: {failed}", file=sys.stderr)

    # Skip writing if star counts are unchanged (avoids ~3 bot commits/day
    # that would otherwise happen purely from the updated timestamp).
    if old_repos == repos and isinstance(old_data, dict):
        print(f"Unchanged: {len(repos)} repos — skipping write")
        return

    now = datetime.now(timezone.utc).isoformat()
    out = {"repos": repos, "updated": now}
    with open(OUTPUT_FILE, "w") as f:
        json.dump(out, f, indent=2)
        f.write("\n")

    print(f"\nWritten {len(repos)}/{len(REPOS)} repos -> {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
