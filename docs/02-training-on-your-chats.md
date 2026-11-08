# Training on Your Chats: Who Learns From What You Type

This is the big one. Of everything in an AI app's terms of service, this is the
clause that makes people the most uncomfortable - and the one that is easiest
to actually do something about.

## The plain-English version

When you type a message into a consumer AI app, the company keeps a copy. That
is how the app remembers your conversation, shows it in your history, and lets
you pick up where you left off.

The important question is: **what are they allowed to do with that copy?**

There are basically two buckets:

1. **"To provide the service."** Storing your chat so you can read it later,
   keeping the app working, fixing bugs, protecting against abuse. This is
   normal, expected, and almost universal.
2. **"To improve our services" or "to train our models."** Taking your actual
   words (sometimes with your identifying details removed, sometimes not) and
   feeding them into the systems that teach future versions of the model how to
   behave. This is the bucket people care about.

The second bucket is the one to watch, because once your writing goes into
training data, it can influence how the model responds to *other people* - and
you generally cannot un-train a model.

## How most consumer AI apps handle it

Most of the big consumer AI chatbots follow roughly this shape (details change,
so check the live terms for any app you rely on):

- **There is a toggle.** Somewhere in settings there is usually an option with
  a name like "improve the model for everyone," "help improve [the app]," or
  "data controls." When it is on, your new conversations may be used for
  training. When it is off, they generally are not.
- **The default matters more than the toggle.** Some apps default the toggle
  to *on*. Others default it to *off* unless you pay from a business account
  (business and enterprise tiers almost always promise **not** to train on
  your data - that is frequently a selling point of the paid commercial plans).
- **Old chats are usually grandfathered differently.** Turning the toggle off
  today often stops *future* conversations from being used, but conversations
  under the old setting may already have been used or retained. When in doubt,
  look for the app's own explanation of what happens to existing data.
- **Temporary chats exist.** Many apps now offer a "temporary" or "incognito"
  chat mode that bypasses your saved history entirely. It is a nice tool for
  sensitive one-off questions, but it is not a magic shield, and views about
  what is actually retained vary by app - read that app's description of the
  feature.
- **Deleting is its own thing.** Deleting a conversation from your history is
  not the same as it never being collected, and retention rules (see the
  [next chapter](03-data-retention.md)) decide how long the copy lives.

## Three fallback rules that always apply

Regardless of which app you use, these three rules hold almost everywhere:

1. **Don't type secrets you wouldn't say at the DMV.** Passwords, national
   ID numbers, patient health details, credit card numbers of your clients -
   keep them out of consumer AI chats entirely. Type it into a chatbot, and you
   should assume it *could* end up in a human reviewer's screen someday, even
   if the odds are small.
2. **Business plan ≠ safety by vibes.** If your job requires confidentiality,
   use a plan that is specifically sold as confidential. "The free one but
   with waves of optimism" is not a compliance strategy.
3. **Trust is cheaper than audits.** For personal stuff - recipe ideas, your
   book chapter, a chess opening brainstorm - the risk is usually low and the
   training toggle is the levels of "nice if off." For anything you would be
   embarrassed to see quoted in a court filing, use the strictest mode
   available or don't use a consumer chatbot at that moment.

## Where to actually find this setting

Look in your app's settings for one of these common labels:

- "Data controls"
- "Help improve the model"
- "Improve the model for everyone"
- "Training"
- "Personalization and learning"
- "Activity" or "Chat history and training"

If you cannot find any such section in ten seconds of tapping around the
settings page, that is itself a signal - some apps make it easy and some bury
it, but *none* are obligated to make it fun to find.

## Quick reality check

> **Friend note:** I am not saying AI companies are snooping. Most major apps
> do remove identifying details before training, and most of your conversations
> will never be read by a human. The point of this chapter is not "fear." It is
> "calibration": know which bucket your words land in, decide how much you
> care, and flip the toggle once so the default stops being someone else's
> decision.

Next up: how long your chats actually stick around after you delete them -
[**data retention**](03-data-retention.md).
