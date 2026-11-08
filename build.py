#!/usr/bin/env python3
"""Build the static HTML site for ai-terms-of-service-decoded-guide.

Reads the chapters in docs/ (in the order listed in CHAPTERS below) and
writes a dependency-free static site into site/:

  - site/index.html          landing page
  - site/<slug>.html         one page per chapter
  - site/style.css           single shared stylesheet (system fonts)

Uses only the Python standard library. Output is deterministic: running
this script twice produces byte-identical files.
"""

from __future__ import annotations

import html
import re
import shutil
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"

# (file slug, short title for nav, one-line description for the landing page)
CHAPTERS = [
    (
        "01-why-this-matters",
        "Why this matters",
        "What quietly becomes true the moment you tap Send.",
    ),
    (
        "02-training-on-your-chats",
        "Training on your chats",
        "Who learns from what you type, and how to flip the toggle.",
    ),
    (
        "03-data-retention",
        "Data retention",
        "How long your conversations actually stick around.",
    ),
    (
        "04-age-limits",
        "Age limits",
        "The rule almost every family breaks without knowing it.",
    ),
    (
        "05-export-rights",
        "Export rights",
        "Taking your research with you when you leave.",
    ),
    (
        "06-account-suspension",
        "Account suspension",
        "Why accounts get frozen, and what to do about it.",
    ),
    (
        "07-five-minute-checklist",
        "Five-minute checklist",
        "The bookmarkable cheat sheet for any new AI app's terms.",
    ),
    (
        "08-common-scenarios",
        "Real-life scenarios",
        "Eight everyday situations, decoded.",
    ),
]

SITE_TITLE = "AI Terms of Service, Decoded"
SITE_TAGLINE = "What you actually agree to when you use a popular AI app - in plain English."
OWNER = "Asdale Dynamics, LLC"
AUTHOR = "Dylan Asdale"

ICON_SVG = (
    "data:image/svg+xml,"
    "%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E"
    "%3Crect width='32' height='32' rx='7' fill='%233b4a8c'/%3E"
    "%3Ctext x='16' y='22' font-family='Georgia,serif' font-size='17'"
    " fill='%23fff' text-anchor='middle'%3EA%3C/text%3E%3C/svg%3E"
)


# --------------------------------------------------------------------------
# tiny Markdown renderer (subset: what the docs in docs/ actually use)
# --------------------------------------------------------------------------

def slugify(text: str) -> str:
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"[^\w\s-]", "", text)
    return re.sub(r"[\s]+", "-", text.strip().lower())


def render_inline(text: str) -> str:
    """Render inline markup: code, links, bold, italic."""
    # escape first, then handle markup on the escaped text
    out = html.escape(text, quote=False)

    # protect inline code spans
    code_spans: list[str] = []

    def stash_code(m: re.Match) -> str:
        code_spans.append(m.group(1))
        return f"\x00{len(code_spans) - 1}\x00"

    out = re.sub(r"`([^`]+)`", stash_code, out)

    # links: [text](target)
    def do_link(m: re.Match) -> str:
        label, target = m.group(1), m.group(2)
        if target.endswith(".md"):
            target = target[:-3] + ".html"
        return f'<a href="{target}">{label}</a>'

    out = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", do_link, out)

    # bold then italic
    out = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", out)
    out = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", out)

    # restore code spans
    def unstash(m: re.Match) -> str:
        body = html.escape(code_spans[int(m.group(1))], quote=False)
        return f"<code>{body}</code>"

    out = re.sub(r"\x00(\d+)\x00", unstash, out)
    return out


def render_markdown(source: str, page_id: str) -> str:
    """Kept for API compatibility; see :func:`render_markdown_clean`."""
    return render_markdown_clean(source)


# The naive two-pass above got tangled; use a single clean pass instead.
def render_markdown_clean(source: str) -> str:
    """Single-pass Markdown-to-HTML for the subset used by this project.

    Supported: #..#### headings (with ids), paragraphs, bullet/ordered
    lists, blockquotes, fenced code blocks, horizontal rules, inline
    code/bold/italics/links.
    """
    lines = textwrap.dedent(source).splitlines()
    out: list[str] = []
    used_slugs: set[str] = set()

    para: list[str] = []
    bq: list[str] = []
    ul: list[str] = []
    ol: list[str] = []
    fence: list[str] | None = None

    def flush_para() -> None:
        nonlocal para
        if para:
            joined = " ".join(part.strip() for part in para)
            out.append(f"<p>{render_inline(joined)}</p>")
            para = []

    def flush_bq() -> None:
        nonlocal bq
        if bq:
            joined = " ".join(part.strip() for part in bq)
            out.append(f"<blockquote><p>{render_inline(joined)}</p></blockquote>")
            bq = []

    def flush_ul() -> None:
        nonlocal ul
        if ul:
            out.append("<ul>")
            out.extend(f"<li>{render_inline(item)}</li>" for item in ul)
            out.append("</ul>")
            ul = []

    def flush_ol() -> None:
        nonlocal ol
        if ol:
            out.append("<ol>")
            out.extend(f"<li>{render_inline(item)}</li>" for item in ol)
            out.append("</ol>")
            ol = []

    def flush_all() -> None:
        flush_para()
        flush_bq()
        flush_ul()
        flush_ol()

    for line in lines:
        # fenced code block
        if line.strip().startswith("```"):
            if fence is None:
                flush_all()
                fence = []
            else:
                out.append("<pre><code>" + html.escape("\n".join(fence), quote=False) + "</code></pre>")
                fence = None
            continue
        if fence is not None:
            fence.append(line)
            continue

        stripped = line.strip()
        if not stripped:
            flush_all()
            continue

        m = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if m:
            flush_all()
            level = len(m.group(1))
            text = m.group(2)
            base = slugify(text)
            slug, n = base, 2
            while slug in used_slugs:
                slug = f"{base}-{n}"
                n += 1
            used_slugs.add(slug)
            out.append(f'<h{level} id="{slug}">{render_inline(text)}</h{level}>')
            continue

        if stripped in ("---", "***", "___"):
            flush_all()
            out.append("<hr>")
            continue

        if stripped.startswith("> "):
            flush_ul()
            flush_ol()
            flush_para()
            bq.append(stripped[2:])
            continue

        m_ol = re.match(r"^\d+\.\s+(.*)$", stripped)
        if m_ol:
            flush_para()
            flush_bq()
            flush_ul()
            ol.append(m_ol.group(1))
            continue

        if stripped.startswith("- "):
            flush_para()
            flush_bq()
            flush_ol()
            ul.append(stripped[2:])
            continue

        # plain text: part of the current paragraph, or (if we are in the
        # middle of a list) a wrapped continuation of the last list item
        if para:
            para.append(stripped)
        elif ul:
            ul[-1] += " " + stripped
        elif ol:
            ol[-1] += " " + stripped
        else:
            para.append(stripped)

    flush_all()
    if fence is not None:  # unterminated fence: dump it as code anyway
        out.append("<pre><code>" + html.escape("\n".join(fence), quote=False) + "</code></pre>")
    return "\n".join(out)


def render_markdown_entry(source: str) -> str:
    return render_markdown_clean(source)


# --------------------------------------------------------------------------
# page chrome
# --------------------------------------------------------------------------

def nav_links(current: str | None) -> str:
    items = []
    for slug, title, _ in CHAPTERS:
        if slug == current:
            items.append(f'<a href="{slug}.html" class="navlink current" aria-current="page">{title}</a>')
        else:
            items.append(f'<a href="{slug}.html" class="navlink">{title}</a>')
    return "\n          ".join(items)


def page_shell(
    *,
    title: str,
    lede: str | None = None,
    body: str,
    current: str | None,
    prev: tuple[str, str] | None = None,
    next: tuple[str, str] | None = None,
) -> str:
    nav = nav_links(current)
    lede_html = f'<p class="lede">{lede}</p>' if lede else ""
    prevnext = ""
    if prev or next:
        parts = []
        if prev:
            parts.append(
                f'<a class="pn prev" href="{prev[0]}.html">&larr; {prev[1]} <span class="pnlabel">Previous</span></a>'
            )
        else:
            parts.append('<span class="pn spacer"></span>')
        if next:
            parts.append(
                f'<a class="pn next" href="{next[0]}.html"><span class="pnlabel">Next</span> {next[1]} &rarr;</a>'
            )
        else:
            parts.append('<span class="pn spacer"></span>')
        prevnext = '<nav class="prevnext">' + "\n  ".join(parts) + "</nav>"

    return textwrap.dedent(f"""\
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="color-scheme" content="light">
    <title>{title} - {SITE_TITLE}</title>
    <meta name="description" content="{lede or SITE_TAGLINE}">
    <link rel="icon" href="{ICON_SVG}">
    <link rel="stylesheet" href="style.css">
    </head>
    <body>
    <header class="siteheader">
      <a class="sitetitle" href="index.html">{SITE_TITLE}</a>
      <nav class="sitelinks">
          {nav}
      </nav>
    </header>
    <main>
      <article>
      {lede_html}
      {body}
      </article>
      {prevnext}
    </main>
    <footer>
      <p>Written by {AUTHOR} &middot; Published by {OWNER} &middot;
      <a href="https://dylanasdale.github.io">dylanasdale.github.io</a></p>
      <p><a href="LICENSE.txt">MIT License</a> &middot; This site is static: no cookies, no analytics, no trackers.</p>
    </footer>
    </body>
    </html>
    """)


def first_heading_title(md_text: str) -> str:
    for line in md_text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return "Untitled"


def chapter_body_and_title(slug: str) -> tuple[str, str]:
    md_path = DOCS / f"{slug}.md"
    md_text = md_path.read_text(encoding="utf-8")
    body = render_markdown_entry(md_text)
    title = first_heading_title(md_text)
    return body, title


def build_index() -> str:
    items = []
    for n, (slug, _, description) in enumerate(CHAPTERS, start=1):
        body, title = chapter_body_and_title(slug)
        items.append(
            textwrap.dedent(f"""\
            <section class="card">
              <h2><a href="{slug}.html">{n}. {title}</a></h2>
              <p>{description}</p>
            </section>""")
        )
    joined = "\n".join(items)

    intro = render_markdown_clean(
        textwrap.dedent(
            """\
        Every popular AI app asks you to agree to terms of service the moment
        you sign up - and almost nobody reads them. This guide reads them for
        you, in the order that matters: what happens to your chats, how long
        they stick around, who is *allowed* to use the app, what you can take
        with you when you leave, and what happens if your account gets
        frozen. Start anywhere; the
        [five-minute checklist](07-five-minute-checklist.md) is the page most
        people bookmark.
        """
        )
    )

    return page_shell(
        title=SITE_TITLE,
        lede=SITE_TAGLINE,
        body="" + intro + "\n" + joined + "",
        current=None,
    )


STYLE_CSS = textwrap.dedent(
    """\
    /* ai-terms-of-service-decoded-guide - one stylesheet, system fonts only */
    :root {
      --ink: #1d2433;
      --muted: #5b6472;
      --paper: #fdfdfb;
      --card: #ffffff;
      --accent: #3b4a8c;
      --accent-soft: #eef0f8;
      --rule: #e3e5ea;
      --quote: #f4f2ec;
      --quote-r: #d8cfa8;
      --code: #2a3140;
    }

    * { box-sizing: border-box; }

    html { font-size: 17px; }

    body {
      margin: 0;
      background: var(--paper);
      color: var(--ink);
      font-family: system-ui, -apple-system, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      line-height: 1.65;
    }

    .siteheader {
      padding: 1.1rem 1.5rem 0.9rem;
      border-bottom: 1px solid var(--rule);
      background: var(--card);
    }

    .sitetitle {
      font-family: Georgia, "Times New Roman", serif;
      font-size: 1.35rem;
      font-weight: bold;
      color: var(--accent);
      text-decoration: none;
      letter-spacing: 0.01em;
    }

    .sitelinks {
      display: flex;
      flex-wrap: wrap;
      gap: 0.15rem 0.4rem;
      margin-top: 0.55rem;
      font-size: 0.86rem;
    }

    .navlink {
      color: var(--muted);
      text-decoration: none;
      padding: 0.18rem 0.6rem;
      border-radius: 999px;
      border: 1px solid transparent;
    }

    .navlink:hover { color: var(--accent); background: var(--accent-soft); }

    .navlink.current {
      color: var(--accent);
      background: var(--accent-soft);
      border-color: var(--rule);
      font-weight: 600;
    }

    main {
      max-width: 46rem;
      margin: 0 auto;
      padding: 1.6rem 1.25rem 2.5rem;
    }

    article {
      background: var(--card);
      border: 1px solid var(--rule);
      border-radius: 14px;
      padding: 1.7rem 1.9rem 1.15rem;
    }

    h1, h2, h3, h4 {
      font-family: Georgia, "Times New Roman", serif;
      line-height: 1.25;
      color: var(--ink);
      scroll-margin-top: 1rem;
    }

    h1 { font-size: 1.75rem; margin: 0 0 1rem; }
    h2 { font-size: 1.28rem; margin: 1.9rem 0 0.55rem; }
    h3 { font-size: 1.08rem; margin: 1.5rem 0 0.4rem; }
    h4 { font-size: 0.98rem; margin: 1.3rem 0 0.35rem; }

    p { margin: 0.7rem 0 1.1rem; }

    .lede {
      font-size: 1.06rem;
      color: var(--muted);
      margin-top: 0;
    }

    a { color: var(--accent); }
    a:hover { text-decoration-thickness: 2px; }

    ul, ol { margin: 0.3rem 0 1.1rem; padding-left: 1.35rem; }
    li { margin: 0.3rem 0; }
    li::marker { color: var(--accent); font-weight: 600; }

    blockquote {
      margin: 1.25rem 0;
      padding: 0.85rem 1.15rem;
      background: var(--quote);
      border-left: 4px solid var(--quote-r);
      border-radius: 0 10px 10px 0;
    }

    blockquote p:first-child { margin-top: 0; }
    blockquote p:last-child { margin-bottom: 0; }

    code {
      font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, "Liberation Mono", monospace;
      font-size: 0.86em;
      background: var(--accent-soft);
      border-radius: 5px;
      padding: 0.08em 0.35em;
    }

    pre {
      background: var(--code);
      color: #eef1f6;
      border-radius: 10px;
      padding: 0.9rem 1.1rem;
      overflow-x: auto;
      line-height: 1.5;
      font-size: 0.86rem;
    }

    pre code { background: none; color: inherit; padding: 0; font-size: 1em; }

    hr {
      border: 0;
      border-top: 1px solid var(--rule);
      margin: 1.6rem 0;
    }

    .card {
      background: var(--card);
      border: 1px solid var(--rule);
      border-radius: 12px;
      padding: 0.85rem 1.25rem 0.55rem;
      margin: 0.85rem 0;
    }

    .card h2 { margin: 0.2rem 0 0.3rem; font-size: 1.14rem; }
    .card h2 a { text-decoration: none; color: var(--accent); }
    .card p { margin: 0.15rem 0 0.75rem; color: var(--muted); }

    .prevnext {
      display: flex;
      justify-content: space-between;
      gap: 0.8rem;
      margin-top: 1.2rem;
      font-size: 0.92rem;
    }

    .pn {
      flex: 1;
      display: inline-block;
      padding: 0.55rem 0.9rem;
      background: var(--card);
      border: 1px solid var(--rule);
      border-radius: 10px;
      text-decoration: none;
      color: var(--ink);
    }

    .pn:hover { color: var(--accent); background: var(--accent-soft); }

    .pn.next { text-align: right; }
    .pn.next .pnlabel { display: block; color: var(--muted); font-size: 0.78rem; }
    .pn.prev .pnlabel { display: block; color: var(--muted); font-size: 0.78rem; }
    .pn.spacer { visibility: hidden; }

    footer {
      max-width: 46rem;
      margin: 0 auto;
      padding: 1rem 1.25rem 2.2rem;
      color: var(--muted);
      font-size: 0.86rem;
      border-top: 1px solid var(--rule);
    }

    @media (max-width: 640px) {
      html { font-size: 16px; }
      article { padding: 1.15rem 1.1rem 0.9rem; }
      .prevnext { flex-direction: column-reverse; }
      .pn.spacer { display: none; }
    }
    """
)


# --------------------------------------------------------------------------
# build
# --------------------------------------------------------------------------

def build() -> None:
    if SITE.exists():
        shutil.rmtree(SITE)
    SITE.mkdir(parents=True)

    (SITE / "style.css").write_text(STYLE_CSS, encoding="utf-8")

    count = len(CHAPTERS)
    for n, (slug, _, _) in enumerate(CHAPTERS):
        body, title = chapter_body_and_title(slug)
        prev_idx = n - 1 if n > 0 else None
        next_idx = n + 1 if n < count - 1 else None
        prev = (CHAPTERS[prev_idx][0], CHAPTERS[prev_idx][1]) if prev_idx is not None else None
        next = (CHAPTERS[next_idx][0], CHAPTERS[next_idx][1]) if next_idx is not None else None
        lede = hello_lede(slug, n)
        html_text = page_shell(
            title=title,
            lede=lede,
            body=body,
            current=slug,
            prev=prev,
            next=next,
        )
        (SITE / f"{slug}.html").write_text(html_text, encoding="utf-8")

    (SITE / "index.html").write_text(build_index(), encoding="utf-8")

    shutil.copyfile(ROOT / "LICENSE", SITE / "LICENSE.txt")
    print(f"Built {count} chapter pages + index into {SITE}")


def hello_lede(slug: str, n: int) -> str:
    ledes = {
        "01-why-this-matters": None,
        "07-five-minute-checklist": "Bookmark this page - it is the one worth keeping.",
    }
    return ledes.get(slug)


if __name__ == "__main__":
    build()
