# Briefing agents without burning credits

Most waste in a multi-agent run is not the work; it is agents rediscovering the codebase, editing the same
file, and reporting at length. These rules cut all three. They were applied to the agents that built the
voice and hand-tracking layers in this repo.

## The brief template

```
Create ONE new file: <absolute path>
Do not read or modify any other file. Do not run the app. Do not create other files.

Context: <two sentences, the minimum to make decisions>

Exact exported API (must match, other code depends on it):
<the signatures, verbatim>

Requirements:
- <constraint that would otherwise be guessed>
- <the failure mode you already know about>
Verify: <the exact command that proves it parses or passes>

Reply with ONLY: exported names, and any assumption you made. Under 15 lines.
```

## Why each line earns its place

- **One file, named absolutely.** File ownership is what prevents the collisions that cost a rewrite. Two
  agents editing one file in this repo produced duplicated blocks that broke the module twice.
- **"Do not read any other file."** Exploration is the largest hidden cost in a subagent run. If context is
  needed, paste it; a paragraph is cheaper than a search.
- **The exact API.** Integration becomes mechanical. Without it you pay twice: once for the agent to invent
  a shape, again for you to adapt it.
- **Known failure modes up front.** Naming the trap (recognition stops silently, a background tab clamps
  timers) is far cheaper than a debugging round trip.
- **A verify command.** The agent proves its own work; you do not spend a turn discovering it does not parse.
- **A capped reply.** You need the API surface and the assumptions. Everything else is re-readable in the file.

## Running the team

- Integrate centrally. Agents write new modules; one owner wires them into shared files.
- Prefer several small agents over one large one, but only when their outputs do not touch.
- Give slow, independent work (benchmarks, dataset builds) to background agents and keep interactive work
  in the main session.
- Before spawning, check `git log`: another session may already be doing it.

## Meta-prompt used to rewrite the request

> Rewrite this request as a build spec. For each item state what it means concretely, the test that shows it
> is done, and whether it is possible as stated. Where it is not possible, say so plainly and give the
> nearest thing that is. Keep the user's priorities; drop nothing silently.

That rewrite is `docs/SPEC.md`.
