#!/usr/bin/env python3
"""Keep each blog post's "last updated" metadata honest and in sync.

For every post we write four places from ONE source of truth — the commit
date of the last *real* (non-bot) commit that touched the file:

  1. the JSON-LD ``dateModified`` field,
  2. the visible ``<span class="sig-updated">`` line in the sign-off block
     (date only — it sits right under the publication date, which is the
     pairing Google looks for),
  3. the visible ``<p class="lastmod-note">`` line after the references
     (date *and* time — for readers who want to know how fresh the page is),
  4. the ``<lastmod>`` entry in sitemap.xml.

Google will only show an updated date in search results when the structured
data agrees with a date a human can actually see on the page, so 1 and 2 must
never drift apart. That is also why the old JavaScript updater was deleted:
it overwrote ``dateModified`` at render time with the deploy timestamp, which
silently broke that agreement.

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

SITEMAP = "sitemap.xml"
SITE = "https://knightzjz.github.io/"

MONTHS_EN = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

# Both visible lines read "<label><date>". The labels are pinned down here
# rather than matched as "anything ending in a colon".
#
# An earlier version did the latter, matched the whole span body, and shipped
# the posts with the label stripped — a bare date that read like a sentence
# fragment. Pinning the labels also kills the mirror image of that bug: the
# closing note carries a time (…22:08), so a colon-chasing pattern happily
# treats the colon *inside the clock* as the label separator, splices the new
# date into the middle of the timestamp, and then passes its own sanity check
# because the re-match finds the rewritten value sitting after that colon.
LABELS = {
    "zh": {"sig": "最后更新：", "note": "最后更新时间："},
    "en": {"sig": "Last updated: ", "note": "Last updated: "},
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


def fmt_visible_long(when: datetime, lang: str) -> str:
    """Date plus time, for the closing note after the references."""
    clock = f"{when.hour:02d}:{when.minute:02d}"
    if lang == "zh":
        return f"{when.year} 年 {when.month} 月 {when.day} 日 {clock}"
    return f"{MONTHS_EN[when.month - 1]} {when.day}, {when.year}, {clock}"


def fmt_iso(when: datetime) -> str:
    return when.strftime("%Y-%m-%dT%H:%M:%S") + "+08:00"


def rewrite_post(path: str, lang: str, when: datetime, dry: bool) -> bool:
    full = os.path.join(REPO, path)
    with open(full, encoding="utf-8") as fh:
        src = fh.read()

    iso = fmt_iso(when)
    visible = fmt_visible(when, lang)
    visible_long = fmt_visible_long(when, lang)

    sig_re = labelled('<span class="sig-updated">', LABELS[lang]["sig"], "</span>")
    note_re = labelled('<p class="lastmod-note">', LABELS[lang]["note"], "</p>")

    # 1. JSON-LD dateModified — the field is written without spaces after the
    #    colon in these files, but match both spellings to stay robust.
    new_src, n_ld = re.subn(
        r'("dateModified"\s*:\s*")[^"]*(")',
        lambda m: m.group(1) + iso + m.group(2),
        src,
        count=1,
    )
    # 2. Visible "last updated" line — replace the date only, keep the label.
    m_vis = sig_re.search(new_src)
    n_vis = 0
    if m_vis is not None:
        new_src = new_src[: m_vis.start(2)] + visible + new_src[m_vis.end(2) :]
        n_vis = 1

    # 3. article:modified_time meta tag.
    new_src, n_meta = re.subn(
        r'(<meta property="article:modified_time" content=")[^"]*(")',
        lambda m: m.group(1) + iso + m.group(2),
        new_src,
        count=1,
    )

    # 4. Closing note after the references — date and time, label kept intact.
    m_note = note_re.search(new_src)
    n_note = 0
    if m_note is not None:
        new_src = (
            new_src[: m_note.start(2)] + visible_long + new_src[m_note.end(2) :]
        )
        n_note = 1

    missing = [
        name
        for name, count in
        (
            ("dateModified", n_ld),
            ("sig-updated", n_vis),
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
    check = sig_re.search(new_src)
    if check is None or check.group(2) != visible:
        print(f"  !! {path}: visible line would read wrong — left untouched")
        return False

    check_long = note_re.search(new_src)
    if check_long is None or check_long.group(2) != visible_long:
        print(f"  !! {path}: closing note would read wrong — left untouched")
        return False

    if new_src == src:
        print(f"  == {path}: already up to date ({iso})")
        return False

    print(f"  -> {path}: {iso} | {visible} | {visible_long}")
    if not dry:
        with open(full, "w", encoding="utf-8") as fh:
            fh.write(new_src)
    return True


def rewrite_sitemap(dates: dict[str, datetime], dry: bool) -> bool:
    full = os.path.join(REPO, SITEMAP)
    with open(full, encoding="utf-8") as fh:
        src = fh.read()

    new_src = src
    for path, when in dates.items():
        url = SITE + path
        new_src = re.sub(
            r"(<loc>" + re.escape(url) + r"</loc>\s*<lastmod>)[^<]*(</lastmod>)",
            lambda m: m.group(1) + fmt_iso(when) + m.group(2),
            new_src,
            count=1,
        )

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
    dates: dict[str, datetime] = {}

    for path, lang in POSTS:
        when = last_real_commit(path)
        if when is None:
            print(f"  ?? {path}: no git history, skipped")
            continue
        dates[path] = when
        if rewrite_post(path, lang, when, dry):
            changed = True

    changed = rewrite_sitemap(dates, dry) or changed

    print("\n" + ("Changes pending." if changed else "Nothing to update."))
    return 0


if __name__ == "__main__":
    sys.exit(main())
