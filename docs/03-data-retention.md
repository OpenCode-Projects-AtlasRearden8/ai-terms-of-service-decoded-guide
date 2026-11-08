# Data Retention: How Long Your Chats Actually Sit Around

You press delete. The conversation vanishes from your screen. It is very
satisfying.

And then, quietly, one of two things happens: the company really did delete it,
or the company moved it into a "backup," "archive," "disaster recovery," or
"legal hold" bucket, where it lives for another 30 to 90 days... and
occasionally *forever*.

Retention is the part of the terms of service where "delete" does not mean
"delete," so this chapter is all about what the words actually mean.

## The three lives of a "deleted" chat

Most AI apps use some version of these three stages:

1. **Visible.** Your chat shows up in your history. You can reopen it, share
   it, or delete it yourself.
2. **Soft-deleted.** You deleted it, and it is gone from your screen, but a
   backup still exists on the company's servers. This is usually for 30 to 90
   days, and exists so they can undo deletions (for example, if your account
   was compromised), restore after a crash, or comply with law enforcement
   requests.
3. **Fully deleted.** Removed from active systems and (eventually, though not
   always quickly) purged from backups. Some companies are prompt about this;
   some keep de-identified copies around indefinitely for internal analysis.
   The privacy policy - a separate document from the terms of service - usually
   spells this out.

So "I deleted it" often means "I moved it from bucket 1 to bucket 2." That is
fine, as long as you know it. It is *not* fine when someone expects "I deleted
that chat about my landlord dispute" to mean "it no longer exists anywhere on
Earth."

## What "retention" usually buys you

Here is the friend-warmed truth: most retention is *not* sinister. It exists
because of things like:

- **Backups and outage recovery.** Databases need safety copies. Real gold
  standard: "we restore it within days" beats "we lost every chat in a flood."
- **Abuse and safety review.** If someone files a report about a conversation,
  the company may need enough history to actually review it.
- **Legal requests.** Terms and privacy policies often carve out an exception:
  whichever retention period applied, they can keep data longer if a court or
  law enforcement process requires it.
- **Security.** If an account is stolen, a small retention window lets the
  company help you undo the damage instead of just shrugging.

None of this changes the practical rule, which is:

> **Assume anything you typed can survive for at least 30-90 days after you
> delete it - and read the specific app's privacy policy for the exact window
> and any exceptions.**

## The settings that change your retention

Many apps now give you real levers here. Common ones (names vary by app):

- **Auto-delete chats after N days** (24 hours to 18 months in some apps, with
  a range of choices). Usually buried in "Data controls" or "History."
- **Disable chat history entirely.** Some apps let you turn off saved history
  so conversations disappear from your visible history much faster after the
  chat ends.
- **Temporary / incognito chats.** One-off chats that skip your saved history
  entirely. Good for sensitive questions. Not the same as guaranteed zero
  traces - read the feature's description carefully.
- **Download-before-delete.** Strong tip: before closing any AI account you
  have been using for years, export your data *first* (more detail in the
  [export rights chapter](05-export-rights.md)), then delete. Deleting first
  and exporting second never works, in the same way that shredding a document
  and then photocopying it never works.

## A simple mental model

If the words "retention" and "de-identified" start making your eyes glaze
over, hold on to this one summary:

- **What you can see:** usually deletable by you, anytime.
- **What they keep after you delete:** usually 30-90 days, with exceptions for
  law enforcement, safety reports, and their backup schedule.
- **What they keep forever:** usually de-identified snippets used for analytics
  or safety - the privacy policy will generally admit this.
- **What trained models "know":** weaning a model of a fact it learned from
  training is somewhere between hard and impossible. This is why the
  [training chapter](02-training-on-your-chats.md) comes first.

## Quick reality check

> **Friend note:** The companies are not out to get you - retention is mostly
> plumbing. But "I deleted it" is a phrase that means four different things,
> and until you know which version an app offers, you don't actually know what
> you agreed to. Thirty seconds in "Data controls" usually tells you more than
> an hour of vaguely skimming a legal PDF.

Next: the age limit almost everyone overlooks -
[**age limits**](04-age-limits.md).
