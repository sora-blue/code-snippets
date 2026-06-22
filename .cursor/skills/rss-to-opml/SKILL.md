---
name: rss-to-opml
description: >-
  Convert tab-separated RSS feed lines (title + URL) into a Rolify/OPML export
  file. Skips blank lines and rows containing "not found". Use when the user
  wants RSS to OPML, rolly rss export, or batch subscription outline generation.
---

# RSS to OPML

## Script

`workflows/rss-to-opml/rssconv.py`

## Input format

Tab-separated lines: `标题<TAB>URL`

- Blank lines → skipped
- Lines containing `not found` → skipped

Example (`workflows/rss-to-opml/sample-input.txt`):

```
南华早报		https://rsshub.rssforever.com/scmp/3
韩国中央日报	not found
```

## Run

**Direct (all platforms):**

```bash
python workflows/rss-to-opml/rssconv.py --in feeds.txt --out export.opml
```

**Via unified runner:**

```bash
python workflows/run.py rss-to-opml -- --in feeds.txt --out export.opml
```

Note the `--` before workflow-specific flags when using `run.py`.

## Options

| Flag | Default | Purpose |
|------|---------|---------|
| `-l`, `--length` | `5` | Icon text length (first word prefix) |

## Output

Valid OPML 1.0 with random `#RRGGBB` color per feed. XML special characters in titles/URLs are escaped.

Pure Python — no WSL routing needed on Windows.
