#!/usr/bin/env python3
"""Keep each blog post's "last updated" metadata honest and in sync.

Blog posts (``POSTS``) get three places written from ONE source of truth —
the commit date of the last *real* (non-bot) commit that touched the file:

  1. the JSON-LD ``dateModified`` field,
  2. the visible ``<p class="lastmod-note">`` line after the references — the
     only updated date a reader sees, and therefore the only one that can
     corroborate the structured data,
  3. the ``<lastmod>`` entry in sitemap.xml.

There used to be a second visible date in the sign-off block, right under the
publication date. It was removed on purpose: two visible "last updated" lines
read like a rendering glitch, and the publication date already carries the
time. One date, in one place, matching the JSON-LD exactly.

Google only shows an updated date when the structured data agrees with a date
a human can actually see, so 1 and 2 must never drift apart. That is also why
the old JavaScript updater was deleted: it overwrote ``dateModified`` at
render time with the deploy timestamp, which silently broke that agreement.

Landing pages (``PAGES`` — the home page and the blog index) get machine
readable metadata only: their JSON-LD ``dateModified`` and their sitemap
``<lastmod>``. They deliberately carry NO visible updated date. Google never
renders a date for a non-article page, so a visible line would have nothing
to corroborate and would only clutter the layout; sitemap ``<lastmod>`` is a
crawl-scheduling hint and does not require a human-visible counterpart.

The rewrite uses ``count=1``, so on the blog index the ``dateModified``
belonging to the Blog entity must stay the FIRST one in the file — ahead of
anything inside the ``blogPost`` array. That is why those entries carry
``datePublished`` only.

Idempotent by construction: bot commits carry ``[skip ci]`` and are skipped
when looking for the last real commit, so re-running produces the same date
and therefore no diff. No diff means no commit, which is what stops the
GitHub Action from re-triggering itself forever.

Usage:
    python scripts/update_modified_dates.py            # rewrite files
    DRY_RUN=1 python scripts/update_modified_dates.py  # report only
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BEIJING = timezone(timedelta(hours=8))

# Commit subjects containing this marker are bot commits and are ignored when
# looking for the last real content change.
SKIP_MARKER = "[skip ci]"

# (path, language of the visible date line)
POSTS = [
    ("blog/unified-fid.html", "zh"),
    ("blog/unified-fid-en.html", "en"),
]

# (path, URL path as it appears in sitemap.xml) for pages that only carry
# machine-readable freshness. The URL is spelled out because it is not always
# the file path: the home page lives in index.html but is listed as "/".
PAGES = [
    ("index.html", ""),
    ("blog/index.html", "blog/"),
]

SITEMAP = "sitemap.xml"
SITE = "https://knightzjz.github.io/"

MONTHS_EN = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

# The closing note reads "<label><date>". The label is pinned down here
# rather than matched as "anything ending in a colon".
#
# An earlier version did the latter, matched the whole element body, and
# shipped the posts with the label stripped — a bare date that read like a
# sentence fragment. Pinning the label also kills the mirror image of that
# bug: when the note still carried a time (…22:08), a colon-chasing pattern
# happily treated the colon *inside the clock* as the label separator, spliced
# the new date into the middle of the timestamp, and then passed its own
# sanity check because the re-match found the rewritten value sitting after
# that colon. The time is gone now, but the whitelist stays.
LABELS = {
    "zh": "最后更新：",
    "en": "Last updated: ",
}


def labelled(open_tag: str, label: str, close_tag: str) -> re.Pattern:
    """Match <open_tag><label><the part we rewrite><close_tag>.

    Group 2 is the payload and the only thing callers should replace; the
    label lives in group 1 and is never touched.
    """
    return re.compile(
        r"(" + re.escape(open_tag) + re.escape(label) + r")([^<]*)("
        + re.escape(close_tag) + r")"
    )


def git(*args: str) -> str:
    out = subprocess.run(
        ["git", "-C", REPO, *args],
        capture_output=True, text=True, check=True,
    )
    return out.stdout


def last_real_commit(path: str) -> datetime | None:
    """Commit date of the newest commit touching `path`, skipping bot commits."""
    log = git("log", "--format=%cI%x1f%s", "--", path).strip()
    if not log:
        return None
    fallback = None
    for entry in log.split("\n"):
        iso, _, subject = entry.partition("\x1f")
        when = datetime.fromisoformat(iso.strip()).astimezone(BEIJING)
        if fallback is None:
            fallback = when
        if SKIP_MARKER not in subject:
            return when
    # Every commit we know about is a bot commit — better than nothing.
    return fallback


def fmt_visible(when: datetime, lang: str) -> str:
    if lang == "zh":
        return f"{when.year} 年 {when.month} 月 {when.day} 日"
    return f"{MONTHS_EN[when.month - 1]} {when.day}, {when.year}"




def fmt_iso(when: datetime) -> str:
    return when.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"


def rewrite_post(path: str, lang: str, when: datetime, dry: bool) -> bool:
    full = os.path.join(REPO, path)
    with open(full, encoding="utf-8") as fh:
        src = fh.read()

    iso = fmt_iso(when)
    visible = fmt_visible(when, lang)

    note_re = labelled('<p class="lastmod-note">', LABELS[lang], "</p>")

    # 1. JSON-LD dateModified — the field is written without spaces after the
    #    colon in these files, but match both spellings to stay robust.
    new_src, n_ld = re.subn(
        r'("dateModified"\s*:\s*")[^"]*(")',
        lambda m: m.group(1) + iso + m.group(2),
        src,
        count=1,
    )

    # 2. article:modified_time meta tag.
    new_src, n_meta = re.subn(
        r'(<meta property="article:modified_time" content=")[^"]*(")',
        lambda m: m.group(1) + iso + m.group(2),
        new_src,
        count=1,
    )

    # 3. Closing note after the references — the only visible updated date on
    #    the page. Replace the date only, keep the label.
    m_note = note_re.search(new_src)
    n_note = 0
    if m_note is not None:
        new_src = (
            new_src[: m_note.start(2)] + visible + new_src[m_note.end(2) :]
        )
        n_note = 1

    missing = [
        name
        for name, count in
        (
            ("dateModified", n_ld),
            ("modified_time", n_meta),
            ("lastmod-note", n_note),
        )
        if count == 0
    ]
    if missing:
        print(f"  !! {path}: could not find {', '.join(missing)} — left untouched")
        return False

    # Belt and braces: refuse to write if the label somehow got eaten, or if
    # the visible date no longer matches the ISO value we are shipping.
    check = note_re.search(new_src)
    if check is None or check.group(2) != visible:
        print(f"  !! {path}: closing note would read wrong — left untouched")
        return False

    if new_src == src:
        print(f"  == {path}: already up to date ({iso})")
        return False

    print(f"  -> {path}: {iso} | {visible}")
    if not dry:
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(new_src)
    return True


def rewrite_page(path: str, when: datetime, dry: bool) -> bool:
    """Refresh the machine-readable date on a non-article page.

    No visible line is written — see the module docstring for why.
    """
    full = os.path.join(REPO, path)
    with open(full, encoding="utf-8") as fh:
        src = fh.read()

    iso = fmt_iso(when)
    new_src, n_ld = re.subn(
        r'("dateModified"\s*:\s*")[^"]*(")',
        lambda m: m.group(1) + iso + m.group(2),
        src,
        count=1,
    )
    if n_ld == 0:
        # Not every landing page ships structured data. The sitemap entry is
        # the part that matters, so this is a note rather than a failure.
        print(f"  -- {path}: no JSON-LD dateModified (sitemap lastmod only)")
        return False

    if new_src == src:
        print(f"  == {path}: already up to date ({iso})")
        return False

    print(f"  -> {path}: {iso}")
    if not dry:
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(new_src)
    return True


def rewrite_sitemap(
    dates: dict[str, datetime], dry: bool, problems: list[str]
) -> bool:
    full = os.path.join(REPO, SITEMAP)
    with open(full, encoding="utf-8") as fh:
        src = fh.read()

    new_src = src
    for path, when in dates.items():
        url = SITE + path
        new_src, n = re.subn(
            r"(<loc>" + re.escape(url) + r"</loc>\s*<lastmod>)[^<]*(</lastmod>)",
            lambda m: m.group(1) + fmt_iso(when) + m.group(2),
            new_src,
            count=1,
        )
        if n == 0:
            # A stale URL here would otherwise rot silently: the entry just
            # stops being maintained while still looking maintained.
            problems.append(f"{SITEMAP}: no <lastmod> found for {url}")

    if new_src == src:
        print(f"  == {SITEMAP}: already up to date")
        return False

    print(f"  -> {SITEMAP}: refreshed lastmod")
    if not dry:
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(new_src)
    return True


def main() -> int:
    dry = os.environ.get("DRY_RUN") == "1"
    if dry:
        print("DRY RUN — no files will be written\n")

    changed = False
    problems: list[str] = []
    dates: dict[str, datetime] = {}

    for path, lang in POSTS:
        when = last_real_commit(path)
        if when is None:
            problems.append(f"{path}: no git history")
            continue
        dates[path] = when
        if rewrite_post(path, lang, when, dry):
            changed = True

    for path, url_path in PAGES:
        when = last_real_commit(path)
        if when is None:
            problems.append(f"{path}: no git history")
            continue
        dates[url_path] = when
        if rewrite_page(path, when, dry):
            changed = True

    if rewrite_sitemap(dates, dry, problems):
        changed = True

    print("\n" + ("Changes pending." if changed else "Nothing to update."))
    if problems:
        print("Problems:")
        for item in problems:
            print(f"  - {item}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
