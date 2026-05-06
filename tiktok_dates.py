#!/usr/bin/env python3
"""Fill the `Date` column of a TikTok-post CSV with upload timestamps.

Mirrors the bit-shift logic from https://bellingcat.github.io/tiktok-timestamp/
(no network calls — pure local computation).
"""
import csv
import re
import sys
from datetime import datetime, timezone
from email.utils import format_datetime

VIDEO_ID_RE = re.compile(r"/video/(\d+)")


def format_bellingcat(unix_seconds: int) -> str:
    dt = datetime.fromtimestamp(unix_seconds, tz=timezone.utc)
    return f"Uploaded on: {format_datetime(dt, usegmt=True)} (UTC)"


def decode(post_url: str) -> str | None:
    m = VIDEO_ID_RE.search(post_url)
    if not m:
        return None
    # TikTok IDs are Snowflake-style: top 32 bits = unix epoch seconds.
    unix_seconds = int(m.group(1)) >> 32
    return format_bellingcat(unix_seconds)


def open_csv(path: str):
    """Open utf-8-sig first; fall back to cp1252 (Excel default, decodes any bytes)."""
    try:
        f = open(path, newline="", encoding="utf-8-sig")
        f.read()
        f.seek(0)
        return f
    except UnicodeDecodeError:
        f.close()
        return open(path, newline="", encoding="cp1252")


def main(path: str) -> None:
    with open_csv(path) as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if not fieldnames or "Post" not in fieldnames:
            sys.exit(f"error: input CSV must have a 'Post' column; got {fieldnames}")
        if "Date" not in fieldnames:
            fieldnames = list(fieldnames) + ["Date"]
        writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            url = (row.get("Post") or "").strip()
            date = decode(url)
            if date is None:
                if url:
                    print(f"skip (no /video/<id>): {url}", file=sys.stderr)
            else:
                row["Date"] = date
            writer.writerow(row)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("usage: tiktok_dates.py <input.csv>")
    main(sys.argv[1])
