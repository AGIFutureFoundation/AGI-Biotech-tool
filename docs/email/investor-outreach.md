# Investor outreach email — template

Two files, same words:

- `investor-outreach.md` (this one) — paste into any mail client as plain text.
- `investor-outreach.html` — branded, table-based HTML for clients that render it.

Send the plain text version unless you have a reason not to. A plain, specific
email from a founder reads better to most investors than a designed one, and it
cannot render badly.

## Before you send

**The `{{...}}` fields are the only things to change.** Everything else is
checked against the repository and should not be edited casually — the figures
in this email are the ones the tests enforce, and the honesty is the pitch.

| Field | What goes in it |
| --- | --- |
| `{{FIRST_NAME}}` | Their first name. If you don't know it, don't send it. |
| `{{WHY_THEM}}` | One concrete sentence: a portfolio company, a thesis they published, a person who introduced you. Delete the email if you cannot write this honestly. |
| `{{DECK_LINK}}` | The deck artifact, **after** sharing it. It is private by default and the recipient will get a 404 until you share it from the page's Share menu. |
| `{{CALENDAR_OR_ASK}}` | How to book time, or the specific ask. |

**The deck and overview artifacts are private.** Share them explicitly before
putting their links in an email, or use the GitHub links alone — those are
public and need no action.

## Subject lines

Pick one. The first is the honest one and the one that matches the letter.

- `Drug discovery software that publishes its own failure rate`
- `biodao.blockchain — a molecular workspace an AI agent can operate`
- `{{WHY_THEM_SHORT}} — AGI Future Foundation`

## The email

---

Subject: **Drug discovery software that publishes its own failure rate**

Hi {{FIRST_NAME}},

{{WHY_THEM}}

I run AGI Future Foundation. We build a molecular research workspace a scientist
can operate by hand in a headset, and another AI agent can operate over a
protocol — with every result signed and traceable back to the thing that
produced it.

I'll lead with our weakest number, because it's the reason to talk to us rather
than a reason not to.

Our docking benchmark scores **2–6 of 11 cases** within the standard accuracy
threshold, across ten runs. Worse: nine of those eleven cases vary between runs
by more than the margin that decides pass from fail. So the instrument cannot
currently validate its own improvements, and we say so on the front page of the
documentation rather than quoting the best run.

That is the product. Computational drug discovery is full of numbers nobody can
reproduce, and the first thing a serious buyer does is run their own controls.
We built the controls in: every figure we publish is printed next to the command
that reproduces it, and a test re-measures them against the codebase, so a claim
and reality cannot drift apart without the build going red. It has caught us
twice — including a paper we had quoted with one preposition wrong.

What exists today, all of it checkable:

- A molecular workspace — structures, pockets, docking, dynamics, interaction
  analysis — in a browser or a headset, with no account and no API key.
- 22 typed tools an AI agent can call, plus payment challenges and signed
  result fingerprints, so an agent can run and pay for a workflow.
- Eleven live public data sources, every cited identifier re-verified against
  them — 1,264 checks, zero failures.
- A container you can run inside your own network.

You can run it yourself in about two minutes without installing anything —
it works in the browser with no server:

    git clone https://github.com/AGIFutureFoundation/AGI-Biotech-tool
    cd AGI-Biotech-tool && python3 -m http.server 8080

The code, the tests and the full diligence Q&A — 28 questions answered without
hedging — are at
https://github.com/AGIFutureFoundation/AGI-Biotech-tool

{{DECK_LINK}}

If this is interesting, {{CALENDAR_OR_ASK}}. If it isn't, telling me which part
didn't hold up would be genuinely useful.

Best,
{{YOUR_NAME}}
AGI Future Foundation
x@agifuturefoundation.org

---

## What this email deliberately does not say

Each of these was considered and left out on purpose. Putting one back weakens
the email, because the pitch is that we do not do this:

- **No market size.** We have not sourced a defensible figure for the segment we
  occupy, and the pharma-R&D totals quoted in decks are not a market we address.
- **No efficacy claim.** No compound here has been synthesised, assayed or given
  to anything living.
- **No "AI-powered".** Everything is; it says nothing.
- **No best-case metric.** The 2–6 figure is the measured range, not the good run.
- **No urgency theatre.** No closing date, no "limited allocation".
