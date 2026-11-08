# AI Terms of Service, Decoded

*A plain-English guide to what you actually agree to when you use popular AI
apps - written by Dylan Asdale and published by Asdale Dynamics, LLC.*

You use AI apps every week. You probably agree to their terms of service every
month without noticing. This project reads those terms **with you**, in the
order that matters, and leaves out the lawyer furniture:

- **Training on your chats** - when a company may learn from what you type,
  and how to flip the toggle.
- **Data retention** - how long "deleted" chats actually survive.
- **Age limits** - the rule almost every family breaks without knowing it.
- **Export rights** - how to take your conversations with you when you leave.
- **Account suspension** - why accounts get frozen and what to do about it.
- **The five-minute checklist** - a bookmarkable cheat sheet for skimming any
  new AI app's terms yourself.
- **Eight real-life scenarios** - using AI for work, books, kids, shared
  links, and "someone asked for a copy of everything."

Written like a friend would: plain English, short sentences, never
condescending, with honest "friend note" asides marking what is certain,
what varies by app, and what needs a real lawyer.

## Read it here

Two ways to read the guide:

1. **Static site (nicest):** open `site/index.html` in any browser.
2. **Plain Markdown:** read the chapters in `docs/` in numeric order,
   starting with `docs/01-why-this-matters.md`.

Both contain exactly the same words - the site is generated from the
Markdown, not written separately, so they never drift apart.

## Run it / build it

Nothing needs installing. This is a static site with zero dependencies,
zero cookies, zero analytics, and zero scripts - it works offline from a USB
stick.

```bash
# regenerate site/ from docs/ (requires Python 3.9+)
python3 build.py

# run the verification suite (stdlib only)
python3 tests/test.py
```

The build is deterministic: running it twice produces identical files.

## Project layout

```
docs/           the guide, one Markdown file per chapter
site/           generated static HTML (open site/index.html)
build.py        stdlib Markdown-to-HTML site generator
tests/test.py   verification: build determinism, links, no tracking, license
```

## Not legal advice

This is an education project, not legal advice. AI companies update their
terms regularly; the patterns described here are stable, but the exact
wording and numbers vary by app and over time. When something matters,
check the current terms.

## Companion guides

- **API Keys, Plain English** - what a key is, why it is a secret, and how
  not to leak one to a chatbot.
- **Your Personal AI Policy** - write your own short rules once, so
  day-to-day AI decisions make themselves.

## Credits

Written by Dylan Asdale (*The Massive AI Manual*,
[dylanasdale.github.io](https://dylanasdale.github.io)).
Copyright (c) 2026 Asdale Dynamics, LLC, licensed under the MIT License
(see `LICENSE`).
