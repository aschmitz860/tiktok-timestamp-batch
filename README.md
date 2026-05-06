# tiktok-timestamp-batch

Fork of [bellingcat/tiktok-timestamp](https://github.com/bellingcat/tiktok-timestamp) that adds a Python CLI for batch-decoding TikTok upload dates from a CSV of post URLs. Same bit-shift logic as the upstream [web tool](https://bellingcat.github.io/tiktok-timestamp/) — run locally over a whole spreadsheet at once instead of one URL at a time. No API calls, no rate limits, just pure math on the numeric video ID.

The original web tool is preserved in this fork (`index.html`) and remains usable as-is.

## Install

Requirements: **Python 3.10 or later** (the script uses PEP 604 `X | None` type syntax). Standard library only — no `pip install` step.

```sh
git clone https://github.com/aschmitz860/tiktok-timestamp-batch.git
cd tiktok-timestamp-batch
python3 tiktok_dates.py          # prints "usage: tiktok_dates.py <input.csv>" — confirms the script runs
```

If you only need the CLI and not the web tool source, you can also just download `tiktok_dates.py` on its own — it has no other file dependencies.

## Usage

```sh
python3 tiktok_dates.py input.csv > output.csv
```

**Input CSV** must have a `Post` column containing TikTok URLs of the form `https://www.tiktok.com/@user/video/<numeric-id>`. Other columns pass through unchanged.

**Example input** (`posts.csv`):

```csv
Post,Notes
https://www.tiktok.com/@example/video/7359023456789012345,first sighting
https://www.tiktok.com/@user/video/7400000000000000000,follow-up clip
```

**Example output**:

```csv
Post,Notes,Date
https://www.tiktok.com/@example/video/7359023456789012345,first sighting,Uploaded on: Sat, 18 Apr 2026 02:03:34 GMT (UTC)
https://www.tiktok.com/@user/video/7400000000000000000,follow-up clip,Uploaded on: Tue, 23 Jul 2026 19:48:16 GMT (UTC)
```

- A `Date` column is created if missing, or filled in if blank.
- Rows whose `Post` cell lacks `/video/<digits>` pass through with a blank `Date` and a warning printed to stderr.
- Output is written to stdout — redirect with `>` to save to a file.

The script handles UTF-8 (with or without BOM) and falls back to cp1252 (Excel's default) if UTF-8 decoding fails.

## What the timestamp means

The decoded value is the **upload time** of the video — the moment the creator submitted it to TikTok. It is **not**:

- the moment the video was recorded
- the moment you observed or saved the video
- the moment a copy was reposted or stitched

For chain-of-custody work, record the upload timestamp alongside your own capture time and the URL you pulled it from.

## Best practices

- **Capture archives first.** This script tells you when something was uploaded but doesn't preserve the content. Use [yt-dlp](https://github.com/yt-dlp/yt-dlp), [auto-archiver](https://github.com/bellingcat/auto-archiver), or another tool to save the video itself before it gets removed.
- **Resolve short links upstream.** `vm.tiktok.com/...` and `vt.tiktok.com/...` redirects don't contain the numeric ID; this script will skip them. Resolve to a canonical `/@user/video/<id>` URL first (e.g. `curl -sIL <short-url> | grep -i location`).
- **Verify a sample manually.** Pick a few rows and cross-check against the upstream [web tool](https://bellingcat.github.io/tiktok-timestamp/) before relying on a large batch — same logic, but a 30-second sanity check is cheap insurance.
- **Keep the input CSV intact.** Don't pipe `input.csv > input.csv` — that empties the file before the script reads it. Always write to a new path.
- **Watch the stderr stream.** Skipped rows are reported there. If you redirect only stdout, you'll see warnings inline; if you also redirect stderr, capture it to a separate log so you can review skips later.
- **Mind the time zone.** All dates are emitted in **UTC** (matching Bellingcat's format). Convert to the relevant local time only at the reporting layer, never in the source data.

## How it works

TikTok video IDs are Snowflake-style 64-bit integers: the top 32 bits are the Unix epoch seconds at upload time. Right-shift the ID by 32 bits and you have the timestamp directly — no API call required, and the value is recoverable even after the video is deleted, as long as you have the URL.

```python
unix_seconds = int(video_id) >> 32
```

This is the same operation the [upstream web tool](https://bellingcat.github.io/tiktok-timestamp/) performs in JavaScript; this fork just runs it in Python over a CSV.

## Limitations

- Short links (`vm.tiktok.com/...`, `vt.tiktok.com/...`) are not supported — they need a redirect lookup against TikTok to recover the numeric ID. Resolve those upstream first.
- The script assumes one URL per row in the `Post` column. Multi-URL cells are not parsed.
- Encoding detection is two-step (UTF-8, then cp1252). Other encodings (UTF-16, GB18030, etc.) will be silently mis-decoded by the cp1252 fallback. If you suspect non-Western input, convert to UTF-8 first with `iconv` or similar.

## Credits

All credit for the underlying decoding technique goes to [Bellingcat's tiktok-timestamp](https://github.com/bellingcat/tiktok-timestamp), which is in turn based on [Ryan Benson's research](https://dfir.blog/tinkering-with-tiktok-timestamps/). This fork just wraps the same logic in a Python CLI for batch use.

## Contributors

- [@aschmitz860](https://github.com/aschmitz860) — Python CLI and repository maintenance
- [Claude Code](https://claude.com/claude-code) (Anthropic) — paired on the upstream-fork migration, README expansion, and security review

Released under the [MIT License](LICENSE) (inherited from upstream).
