# Voice and Agent Control

Hands in a headset are busy holding a molecule. Voice is the second input, and the same tool registry that
serves voice serves an external agent over MCP.

## The nineteen intents

`parseCommand(text, vocabulary)` in `js/voice.js` is a pure function: transcript in, intent and slots out.
No microphone, no network, no model. That is why it is the most thoroughly tested part of the interface.

| Intent | Says something like |
| --- | --- |
| `load_target` | "load SOD1", "show me LRRK2", "open parkin" |
| `load_pdb` | "load 2YXJ", "structure two y x j" |
| `search` | "search for amyotrophic lateral sclerosis" |
| `dock` | "dock it", "run docking" |
| `find_pockets` | "find pockets", "where are the pockets" |
| `screen` | "screen the library", "screen twelve compounds" |
| `start_md` / `stop_md` | "start dynamics", "stop the simulation" |
| `colour_by` | "colour by confidence", "colour by missense", "colour by hydrophobicity" |
| `representation` | "show cartoon", "show spacefill", "show ball and stick", "show surface" |
| `next_compound` / `prev_compound` | "next", "previous compound" |
| `evidence` | "gather evidence", "what do we know about this" |
| `explain` | "explain this", "read me the score" |
| `measure` | "measure the distance" |
| `reset_view` | "reset view", "recentre" |
| `undo` | "undo that" |
| `help` | "what can I say" |
| `unknown` | anything else |

### What speech recognisers actually send

A recogniser does not hand you the gene symbol you said. It hands you English.

- **"load LRRK2" arrives as "load lark two."** A trailing number-word is converted back to a digit before
  matching, so the symbol resolves. This was a real bug, found by a test, not by use.
- **Spelled letters arrive as words.** "two y x j" becomes `2YXJ`, because a recogniser writes spoken
  letters as `bee`, `see`, `jay`, `queue`, `zed`.
- **A four-character code is read as a structure, not a gene.** PDB identifiers and gene symbols overlap in
  shape and are disambiguated by length and composition.
- **Fuzzy matching is bounded.** A Levenshtein distance within a threshold matches; beyond it the intent is
  `unknown` and nothing runs.

### Silence is safe

Silence, filler words, and unrelated conversation all return `unknown`, which offers help and **executes
nothing**. An always-listening microphone in a lab must not act on an overheard sentence. This is tested
explicitly, not left to chance.

## The twenty-two agent tools

`buildTools(app)` in `js/agent.js` returns the registry. The same objects back the voice layer, the in-app
agent console, and the MCP server, so a capability cannot exist for one caller and not another.

| Tool | |
| --- | --- |
| `load_target` | A curated target by gene symbol, or any gene by name, via AlphaFold |
| `load_structure` | An experimental structure from the PDB by its four-character identifier |
| `find_pockets` | Detect and rank binding pockets by volume and enclosure |
| `load_compound` | Place a molecule by SMILES, compound identifier, or library name |
| `extract_ligand` | Lift a ligand out of the loaded crystal structure so it can be re-docked |
| `dock` *(slow)* | Dock the current ligand into the active site |
| `screen_library` *(slow)* | Dock every compound in the library and rank them |
| `simulate` | Start or stop interactive dynamics in the viewport |
| `run_backend_md` *(slow)* | All-atom OpenMM dynamics on the local server |
| `gather_evidence` *(slow)* | Domains, pathways, expression and variants from the public databases |
| `similar_folds` *(slow)* | Search the current fold against AlphaFold DB and the PDB |
| `known_drugs` | Clinical drugs and candidates for the loaded target, with mechanism |
| `set_view` | Change representation, colouring, or camera framing |
| `analyse_pose` | Classify every contact the bound ligand makes, residue by residue |
| `selectivity` *(slow)* | Dock against related targets and compare |
| `compound_series` | Group the library into structural series by fingerprint similarity |
| `measure` | Distance between two atoms, or an angle across three |
| `describe_scene` | One short paragraph on what is loaded and the latest result |
| `library_search` | Search by text, SMARTS substructure, or property range |
| `next_compound` / `prev_compound` | Step through the library |
| `ledger` | Verify or export the provenance hash chain |

Six tools are marked `slow`, and they are the six that actually cost compute. A caller that wants to warn a
user before a long operation has the flag to check.

## The seam that breaks silently

A person says "colour by confidence." The renderer has never heard of confidence; it knows `plddt`. A
person says "show cartoon"; the renderer wants `cartoon+pocket`. Those translations live in enum maps in
`js/agent.js`, and they are the failure mode nobody notices — a working voice command, a tool that returns
success, and a viewport that does not change.

So the translation is asserted directly in `tests/agent.test.mjs`: the word a person says, through the
parser, through the tool, to the string the renderer actually receives.

## Driving it from outside

`server/mcp_server.py` speaks MCP over stdio and forwards to the browser over `/api/command`, which is a
server-sent-events channel. An external agent therefore gets the same twenty-two tools with the same
schemas. The published schema carries exactly `name`, `description` and `parameters` — never the
implementation function.

An unknown tool name is refused. A tool that throws has the failure recorded in history and re-thrown
rather than swallowed, and every start and result event carries the calling source, so you can tell a voice
command from an agent call after the fact.

## Verifying this page

```bash
node --test tests/voice.test.mjs tests/agent.test.mjs
```

Thirty-two cases. Every published example parses to the intent it is published under, which means the help
text on this page cannot go stale without a test failing.
