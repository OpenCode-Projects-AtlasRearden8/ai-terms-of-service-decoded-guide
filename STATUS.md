# STATUS.md

**Project:** AI Terms of Service, Decoded
**Owner:** Asdale Dynamics, LLC
**Author:** Dylan Asdale
**Status:** Complete and verified - 231/231 test checks passing.
**Last verified:** 2026-11-08

## What was built

A plain-English beginner guide to the fine print in popular AI apps' terms of
service, delivered as both **Markdown docs** and a **generated static HTML
site** (system fonts only, zero JavaScript, zero cookies, zero analytics -
works offline).

**Chapters (docs/, mirrored 1:1 into site/):**

1. Why AI terms of service actually matter
2. Training on your chats (who learns from what you type, and the toggles)
3. Data retention (the three lives of a "deleted" chat)
4. Age limits (the rule most families break without knowing it)
5. Export rights (taking your data with you when you leave)
6. Account suspension (why accounts freeze, appeal paths, arbitration notes)
7. **The five-minute checklist** - the bookmarkable six-question skim guide
   for any new AI app's terms, plus a print-and-pin mini version
8. Eight real-life scenarios (work use, book writing, shared links, kids,
   "delete everything," building on free APIs, data requests)

**File map:**

| Path | What it is |
| --- | --- |
| `docs/*.md` | The guide (source of truth) |
| `build.py` | Stdlib-only Markdown-to-HTML site generator |
| `site/` | Generated static site (open `site/index.html`) |
| `tests/test.py` | Verification suite (231 checks) |
| `LICENSE` | MIT, `Copyright (c) 2026 Asdale Dynamics, LLC` |
| `README.md` | Overview, run instructions, credits |

## How to run it

```bash
# Regenerate the site from docs/  (Python 3.9+, no dependencies)
python3 build.py

# Run the verification suite
python3 tests/test.py

# Read it
open site/index.html        # macOS
xdg-open site/index.html    # Linux
```

No installation, no network, no tracking - the site is fully static and
self-contained (one stylesheet, a data-URI favicon, nothing remote).

## Verification results

`python3 tests/test.py` - **passed: 231, failed: 0**

Coverage highlights:

- Every chapter file listed in `build.py` exists; no orphan docs files.
- Build exits 0 and is **deterministic**: two builds are byte-identical.
- All internal links resolve (files + heading anchors); heading ids unique.
- No `<script>`/`<iframe>`/`<form>` tags anywhere; no analytics/tracker
  strings; remote URLs appear only as plain navigational `<a>` links.
- No leftover unrendered Markdown (`**`, `](`) in generated HTML.
- `LICENSE` carries the exact line `Copyright (c) 2026 Asdale Dynamics, LLC`
  on its own line; README and every site footer credit Asdale Dynamics, LLC.
- No credential-shaped strings or personal emails in any committed file.

## Known gaps / notes

- **Not legal advice, by design.** The guide describes common patterns in
  consumer AI terms, hedged deliberately ("most apps", "often 30-90 days")
  rather than quoting specific companies' current clause wording, which
  changes often. A "what each specific company says" chapter would need
  regular re-verification to stay honest.
- **Markdown renderer is a deliberate subset** (headings, paragraphs,
  lists, quotes, fenced code, hr, inline code/bold/italic/links). Tables,
  images, and nested lists are not supported; none are used in the docs.
- **Site is not published anywhere** per instructions - no remote, no push,
  nothing deployed. It is a local folder you open in a browser.
- **Fenced code block styling** is dark; the one code sample (the checklist
  mini-version) reads fine on it, verified by render.
- **Companion guides referenced but separate projects:** the API-keys guide
  and the personal AI policy guide are mentioned as siblings, not included.

## Housekeeping

- Git initialized in this folder; committed as the existing identity with a
  plain commit message and no Co-authored-by trailers; never pushed.
