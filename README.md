# tiktok-timestamp-batch

Fork of [bellingcat/tiktok-timestamp](https://github.com/bellingcat/tiktok-timestamp) that adds a Python CLI for batch-decoding TikTok upload dates from a CSV of post URLs. Same bit-shift logic as the upstream [web tool](https://bellingcat.github.io/tiktok-timestamp/) — run locally over a whole spreadsheet at once instead of one URL at a time. No API calls, no rate limits, just pure math on the numeric video ID.

The original web tool is preserved in this fork (`index.html`) and remains usable as-is.

## Usage

```sh
python3 tiktok_dates.py input.csv > output.csv
```

- **Input:** a CSV with a `Post` column containing TikTok URLs of the form `https://www.tiktok.com/@user/video/<id>`. A `Date` column will be filled in (created if missing); other columns pass through unchanged.
- **Output:** the same CSV on stdout with `Date` populated like `Uploaded on: Sat, 18 Apr 2026 02:03:34 GMT (UTC)` (matches Bellingcat's format).
- **Skipped rows:** any row whose `Post` cell lacks `/video/<digits>` is passed through with a blank `Date` and a warning to stderr.

Stdlib only — no dependencies. Handles UTF-8 and cp1252 (Excel default) input.

## Limitations

Short links (`vm.tiktok.com/...`, `vt.tiktok.com/...`) are not supported — they need a redirect lookup against TikTok to recover the numeric ID. Resolve those upstream first.

## Credits

All credit for the underlying decoding technique goes to [Bellingcat's tiktok-timestamp](https://github.com/bellingcat/tiktok-timestamp), which is in turn based on [Ryan Benson's research](https://dfir.blog/tinkering-with-tiktok-timestamps/). This fork just wraps the same logic in a Python CLI for batch use.
