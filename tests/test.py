#!/usr/bin/env python3
"""Verification suite for ai-terms-of-service-decoded-guide.

Standard library only. Run from anywhere:

    python3 tests/test.py

Checks:
  1. every chapter file listed in build.py exists
  2. the site builds, and building twice produces identical files
     (deterministic output)
  3. every internal link in the generated HTML resolves to an existing
     file and, where used, an existing heading anchor
  4. no tracking: no scripts, no remote resources, no known analytics
     strings; the only remote references are plain navigational links
  5. headings have unique ids within each page
  6. LICENSE contains the exact required copyright line; README credits
     Asdale Dynamics, LLC
  7. no secrets or personal data patterns in committed text files
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import sys
import tempfile
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SITE = ROOT / "site"

FAILED: list[str] = []
PASSED: list[str] = []


def check(name: str, ok: bool, detail: str = "") -> None:
    if ok:
        PASSED.append(name)
        print(f"  PASS  {name}")
    else:
        FAILED.append(name)
        print(f"  FAIL  {name}" + (f" - {detail}" if detail else ""))


def section(title: str) -> None:
    print(f"\n{title}")


# --------------------------------------------------------------------------


def get_chapter_slugs() -> list[str]:
    src = (ROOT / "build.py").read_text(encoding="utf-8")
    return re.findall(r'^\s*"\s*(\d{2}-[a-z0-9-]+)",\s*$', src, re.M)


# --------------------------------------------------------------------------


class ResourceParser(HTMLParser):
    """Collects href/src values and tag kinds from generated pages."""

    def __init__(self) -> None:
        super().__init__()
        self.resources: list[tuple[str, str, str]] = []  # (tag, attr, value)
        self.has_script = False
        self.headings: list[str] = []
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs) -> None:  # type: ignore[no-untyped-def]
        a = dict(attrs)
        if tag in {"script", "iframe", "object", "embed", "form"}:
            self.has_script = True  # any monitored resource tag = bad
        for attr in ("href", "src"):
            if attr in a and a[attr] is not None:
                self.resources.append((tag, attr, a[attr]))
        if tag in ("h1", "h2", "h3", "h4") and "id" in a:
            self.ids.append(a["id"])


def parse_site() -> dict[Path, ResourceParser]:
    pages: dict[Path, ResourceParser] = {}
    for html_path in sorted(SITE.glob("*.html")):
        parser = ResourceParser()
        parser.feed(html_path.read_text(encoding="utf-8"))
        pages[html_path] = parser
    return pages


# --------------------------------------------------------------------------
# tests
# --------------------------------------------------------------------------


def test_chapters_exist() -> None:
    section("1. Chapter files exist")
    slugs = get_chapter_slugs()
    check("build.py lists chapters", len(slugs) >= 7, f"found {len(slugs)}")
    md_files = {p.stem for p in DOCS.glob("*.md")}
    for slug in slugs:
        check(f"docs/{slug}.md exists", (DOCS / f"{slug}.md").is_file())
    orphans = md_files - set(slugs)
    check("no orphan docs/*.md (every chapter is on the site)",
          not orphans, f"orphans: {sorted(orphans)}")


def test_build_deterministic(tmp: Path) -> None:
    section("2. Build runs and is deterministic")

    def snapshot() -> dict[str, str]:
        return {
            p.relative_to(SITE).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in sorted(SITE.rglob("*"))
            if p.is_file()
        }

    result = subprocess.run(
        [sys.executable, str(ROOT / "build.py")],
        cwd=ROOT, capture_output=True, text=True,
    )
    check("build.py exits 0", result.returncode == 0, result.stderr[-400:])
    first = snapshot()

    out_dir = tmp / "rebuild"
    out_dir.mkdir()
    result2 = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0, sys.argv[1]); import build; "
         "build.SITE = __import__('pathlib').Path(sys.argv[2]); build.build()",
         str(ROOT), str(out_dir)],
        cwd=ROOT, capture_output=True, text=True,
    )
    check("rebuild-to-alt-dir exits 0", result2.returncode == 0, result2.stderr[-400:])
    second = {
        p.relative_to(out_dir).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(out_dir.rglob("*"))
        if p.is_file()
    }
    check("two runs byte-identical", first == second,
          f"first keys {sorted(first)} vs {sorted(second)}")
    check("site has index.html", (SITE / "index.html").is_file())
    check("site has style.css", (SITE / "style.css").is_file())
    check("site has LICENSE.txt", (SITE / "LICENSE.txt").is_file())
    license_ok = "Copyright (c) 2026 Asdale Dynamics, LLC" in (SITE / "LICENSE.txt").read_text(encoding="utf-8")
    check("site/LICENSE.txt carries the LLC copyright", license_ok)


def test_internal_links(pages: dict[Path, ResourceParser]) -> None:
    section("3. Internal links resolve")
    headings_by_page: dict[Path, set[str]] = {}
    for page, parser in pages.items():
        headings_by_page[page] = set(parser.ids)
        dupes = [i for i in parser.ids if parser.ids.count(i) > 1]
        check(f"{page.name}: unique heading ids", not dupes, f"dupes {dupes}")

    # style.css referenced
    for page in pages:
        targets = [v for t, a, v in pages[page].resources
                   if t == "link" and a == "href"]
        check(f"{page.name}: stylesheet is local style.css",
              "style.css" in map(str, targets))

    ok = True
    problems: list[str] = []
    for page, parser in pages.items():
        for tag, attr, value in parser.resources:
            if tag not in ("a", "link", "img", "iframe", "script"):
                continue
            url = value
            if url.startswith(("mailto:", "data:", "tel:")):
                continue
            if url.startswith(("http://", "https://", "//")):
                # remote references are only allowed as navigational <a>
                if tag != "a":
                    ok = False
                    problems.append(f"{page.name}: remote {tag} {url}")
                continue
            if url.startswith("#"):
                frag = url[1:]
                if frag and frag not in headings_by_page[page]:
                    ok = False
                    problems.append(f"{page.name}: broken anchor {url}")
                continue
            target_path, _, frag = url.partition("#")
            resolved = (SITE / target_path).resolve()
            if not resolved.is_file():
                ok = False
                problems.append(f"{page.name}: missing file {url}")
                continue
            if frag:
                frag_parser = ResourceParser()
                frag_parser.feed(resolved.read_text(encoding="utf-8"))
                if frag not in frag_parser.ids:
                    ok = False
                    problems.append(f"{page.name}: missing anchor #{frag} in {target_path}")
        extra = {
            v for t, a, v in parser.resources if t == "img" or t == "iframe"
        }
        if extra:
            ok = False
            problems.append(f"{page.name}: unexpected img/iframe {extra}")
    check("all internal links resolve", ok, "; ".join(problems[:6]))


def test_no_tracking(pages: dict[Path, ResourceParser]) -> None:
    section("4. No tracking / no scripts / no remote resources")
    for page, parser in pages.items():
        check(f"{page.name}: no script/iframe/object/form tags", not parser.has_script)
        text = page.read_text(encoding="utf-8")
        for needle in (
            "google-analytics", "googletagmanager", "gtag(", "analytics.",
            "plausible", "fathom", "matomo", "hotjar", "cloudflareinsights",
            "twitter.com/widgets", "facebook.net", "doubleclick",
        ):
            check(f"{page.name}: no '{needle}'", needle.lower() not in text.lower())
        # remote resources: only <a> tags may point off-site
        remote_bad = [
            (t, v) for t, a, v in parser.resources
            if v.startswith(("http://", "https://", "//")) and t != "a"
        ]
        check(f"{page.name}: remote refs limited to plain links", not remote_bad)


def test_licenses() -> None:
    section("5. License and credits")
    exact = "Copyright (c) 2026 Asdale Dynamics, LLC"
    lic = (ROOT / "LICENSE").read_text(encoding="utf-8")
    check("LICENSE exists and is MIT", lic.startswith("MIT License"))
    check("LICENSE copyright line exact", exact in lic.replace("\n", " "), lic.splitlines()[2] if len(lic.splitlines()) > 2 else lic)
    # the line should be intact on one line
    check("LICENSE copyright line on its own line",
          exact in lic.splitlines())
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    check("README credits Asdale Dynamics, LLC", "Asdale Dynamics, LLC" in readme)
    check("README mentions MIT license", "MIT" in readme)
    check("README written-by line", "Dylan Asdale" in readme)


def test_no_secrets() -> None:
    section("6. No secrets or personal data in text files")
    patterns = [
        (r"sk-[A-Za-z0-9]{16,}", "OpenAI-style key"),
        (r"AKIA[0-9A-Z]{16}", "AWS access key id"),
        (r"BEGIN [A-Z ]*PRIVATE KEY", "private key block"),
        (r"(?i)bearer\s+[A-Za-z0-9._-]{20,}", "bearer token"),
        (r"(?i)(password|passwd|api[_-]?key)\s*[:=]\s*['\"][^'\"]{8,}", "hardcoded credential"),
        (r"[A-Za-z0-9._%+-]+@(?:(?!gmail\.com|example\.com|example\.org)[A-Za-z0-9.-]+)\.[A-Za-z]{2,}", "raw personal email"),
    ]
    targets = [p for p in ROOT.rglob("*")
               if p.is_file()
               and p.suffix in {".md", ".py", ".html", ".css", ".txt"}
               and "site" not in p.relative_to(ROOT).parts[:1]
               and p.name not in {"LICENSE"}]
    ok = True
    hits: list[str] = []
    for p in targets:
        text = p.read_text(encoding="utf-8", errors="ignore")
        for pattern, label in patterns:
            for m in re.finditer(pattern, text):
                ok = False
                hits.append(f"{p.relative_to(ROOT)}: {label}")
    check("no credential-looking strings", ok, "; ".join(hits[:5]))


def test_contents_sane(pages: dict[Path, ResourceParser]) -> None:
    section("7. Content sanity")
    for page, parser in pages.items():
        text = page.read_text(encoding="utf-8")
        check(f"{page.name}: has <title>", "<title>" in text and "</title>" in text)
        check(f"{page.name}: has lang", "<html lang=\"en\">" in text)
        check(f"{page.name}: has viewport meta", 'name="viewport"' in text)
        check(f"{page.name}: has <main>", "<main>" in text)
        check(f"{page.name}:LLC credit in footer", "Asdale Dynamics, LLC" in text)
        check(f"{page.name}: no leftover unrendered markdown", "**" not in text and "](" not in text)

    idx = (SITE / "index.html").read_text(encoding="utf-8")
    check("index links every chapter",
          all(f'{slug}.html' in idx for slug in get_chapter_slugs()))
    # the bookmark checklist page exists and mentions the six sections
    cl = (SITE / "07-five-minute-checklist.html").read_text(encoding="utf-8")
    for topic in ("Training on your chats", "Data retention", "Age limits",
                  "Export rights", "Account suspension", "Change-of-terms notice"):
        check(f"checklist covers '{topic}'", topic in cl)


def main() -> int:
    print("ai-terms-of-service-decoded-guide - verification suite")
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        test_chapters_exist()
        test_build_deterministic(tmp)
        pages = parse_site()
        check("site has index.html parsed", bool(pages))
        test_internal_links(pages)
        test_no_tracking(pages)
        test_licenses()
        test_no_secrets()
        test_contents_sane(pages)

    print("\n" + "=" * 60)
    print(f"passed: {len(PASSED)}   failed: {len(FAILED)}")
    if FAILED:
        print("failed checks:")
        for name in FAILED:
            print(f"  - {name}")
        return 1
    print("ALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
