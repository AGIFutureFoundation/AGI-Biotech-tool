# Provenance Ledger

![How a result is hashed, chained and anchored](graph-provenance.png)


Every result the workspace produces is appended to a SHA-256 hash chain: each record carries the hash of
the one before it, so changing an earlier record invalidates every record after it. Verifying the chain is
one call, and exporting it gives you the whole history as a file.

## It is not a blockchain

Said plainly because the project is called biodao.blockchain and the question is fair.

The ledger is **local and single-writer**. There is no network, no consensus, no distribution, and no
mining. A hash chain gives you tamper-*evidence*: if a record is altered, verification fails and you know.
It does not give you tamper-*resistance* against whoever controls the machine — they can discard the chain
and start a new one. Anyone claiming otherwise is overselling a hash chain, which is a useful,
well-understood, thoroughly unexciting data structure.

What it is genuinely good for: proving to yourself, or to a reviewer six months later, that the figure in
the slide is the figure the tool produced, and that the chain between them has not been edited.

## What it detects, and the one thing it does not

Tested, in `tests/ledger.test.mjs`, by actually tampering:

| Tampering | Caught? |
| --- | --- |
| Editing a score in a record | yes, at that record |
| Deleting the "not kcal/mol" caveat from a record | yes — the caveat is a hashed field, not a note |
| Re-hashing an edited record to cover the edit | yes, at the *next* record, whose link now dangles |
| Reordering two records | yes |
| Splicing a record out of the middle | yes |
| Forging the header's `head` or `length` | yes |
| Renumbering a record's index | yes |
| **Removing records from the end** | **no** |

That last row is a property of hash chains, not a bug: the remaining prefix is a valid chain in its own
right. The only remedy is an external reference — a head hash written somewhere the ledger's author does not
control, at a time you can establish. `verifyExport(doc, { expectedHead })` in `js/ledger-verify.js` takes
that hash and closes the hole; called without it, every result it returns says in as many words that records
removed from the end would not show. An "ok" that quietly means "ok except for the part I cannot check" is
worse than no check at all.

## Verifying an export someone sent you

`js/ledger-verify.js` checks an exported document on its own — no workspace, no browser storage, no network:

```js
import { verifyExport, describeResult } from './js/ledger-verify.js';
const result = await verifyExport(JSON.parse(await file.text()), { expectedHead: anchoredHash });
console.log(describeResult(result));
```

It re-hashes every record, checks every link and index, and cross-checks the document's claimed head and
length against the records it actually carries — a header that disagrees with its own body is the first
thing a careless forgery gets wrong.

## What a record holds

A dock record, for example:

| Field | |
| --- | --- |
| `compound` | AGI identifier or ligand name |
| `smiles` | Canonical SMILES, when known |
| `target`, `site` | Structure name and pocket label |
| `score` | The top pose's score |
| `poses` | How many were kept |
| `method` | `Monte Carlo search, Vina-style score, local rigid-body and torsional refinement` |
| `refinedBy` | How much refinement improved the top pose |
| `provenance` | `ESTIMATE: unvalidated in-browser score, not kcal/mol` |

That last field is the point. The caveat is not in a footnote on a web page that can be redesigned away —
it is a field in the record, and it travels with the number into every export.

## Placeholders cannot launder themselves

A value the workspace does not know is recorded as unknown, and a value it estimated is recorded as an
estimate. Neither can be promoted to a measurement by passing through another step. An anchoring operation
refuses placeholder data outright rather than anchoring a number nobody measured.

This is the single rule the whole project is organised around, and the ledger is where it is enforced
mechanically rather than by good intentions.

## Using it

| | |
| --- | --- |
| **Verify** | Re-hash the chain and report whether it is intact, plus the head hash |
| **Export** | The full record list, as a file you can attach to a report |
| **By voice** | "verify the ledger" |
| **By agent** | The `ledger` tool — see [Voice and Agent Control](Voice-and-Agent-Control) |

## Verifying this page

```bash
node --test tests/ledger.test.mjs
```

Twenty-one cases. See [Testing](Testing).

Note that the ledger records a *score*, and [Docking and Scoring](Docking-and-Scoring) explains why that
score is not an affinity. A tamper-evident record of an unvalidated number is still an unvalidated number;
the ledger proves provenance, not correctness.
