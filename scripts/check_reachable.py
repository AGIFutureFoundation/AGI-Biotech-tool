#!/usr/bin/env python3
"""Report JavaScript modules that nothing can reach.

index.html loads a small number of entry scripts; everything else arrives
through ES import chains. A file outside those chains is dead weight that still
looks maintained -- this repo carried six such files, 1,726 lines, including one
that was a syntax error and so could never have loaded at all.

Three states, not two. The original pass knew only "in the app" and "dead", and
that conflated two different things:

  REACHED   imported, directly or transitively, from an index.html entry point.
  STAGED    not in the app, but imported by a test or an eval harness -- so it
            is exercised, by code that `make verify` runs, and a change that
            breaks it turns CI red.
  DEAD      nothing imports it at all. This is the case the check exists for,
            and it still exits non-zero.

Calling a staged module dead would push whoever hit the gate toward wiring an
unfinished module into the live app just to get a green tick, which is the
opposite of what a gate against dead code should encourage. Calling a dead
module staged would gut the check. So both are reported, and only one fails.

A staged module that nothing ever promotes is still rot, so they are listed
every run rather than passing silently.

Exits non-zero when anything is dead or missing, so it works as a CI gate.

    .venv/bin/python scripts/check_reachable.py
"""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
JS_DIR = os.path.join(ROOT, "js")

SCRIPT_SRC = re.compile(r"""<script[^>]*\bsrc\s*=\s*["']([^"']+)["']""", re.I)
# Covers `import x from 'y'`, `import 'y'`, `export ... from 'y'` and
# `import('y')`, which is how a module is pulled in lazily.
IMPORT = re.compile(r"""(?:\bfrom|\bimport)\s*\(?\s*["']([^"']+)["']""")


def entry_points():
    with open(os.path.join(ROOT, "index.html")) as fh:
        html = fh.read()
    return [os.path.basename(s) for s in SCRIPT_SRC.findall(html) if "js/" in s]


def harness_entry_points():
    """js/ modules imported directly by a test or eval file.

    These are entry points in the same sense index.html's scripts are: a file
    something outside js/ reaches into. Covers the static `import ... from
    '../js/x.js'` and the dynamic `await import('../js/x.js')` that the eval
    harnesses use.
    """
    found = set()
    for folder in ("tests", "evals"):
        d = os.path.join(ROOT, folder)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            if not name.endswith((".mjs", ".js")):
                continue
            with open(os.path.join(d, name)) as fh:
                src = fh.read()
            for spec in IMPORT.findall(src):
                if "/js/" not in spec and not spec.startswith("../js"):
                    continue
                base = os.path.basename(spec)
                found.add(base if base.endswith(".js") else base + ".js")
    return sorted(found)


def walk(entries):
    """Every js/ module reachable from `entries`, including the entries."""
    reached, queue = set(), list(entries)
    while queue:
        name = queue.pop()
        if name in reached:
            continue
        reached.add(name)
        queue.extend(imports_of(name))
    return reached


def imports_of(name):
    path = os.path.join(JS_DIR, name)
    if not os.path.exists(path):
        return []
    with open(path) as fh:
        src = fh.read()
    out = []
    for spec in IMPORT.findall(src):
        if not spec.startswith("."):
            continue  # a bare specifier is a CDN/bare import, not a local file
        base = os.path.basename(spec)
        out.append(base if base.endswith(".js") else base + ".js")
    return out


def main():
    entries = entry_points()
    if not entries:
        print("no <script src=js/...> entry points found in index.html")
        return 1

    reached = walk(entries)
    harness = harness_entry_points()
    staged_reached = walk(harness) - reached

    on_disk = {f for f in os.listdir(JS_DIR) if f.endswith(".js")}
    staged = sorted(staged_reached & on_disk)
    dead = sorted(on_disk - reached - staged_reached)
    missing = sorted((reached | staged_reached) - on_disk)

    print(f"entry points : {', '.join(entries)}")
    print(f"reachable    : {len(reached & on_disk)} of {len(on_disk)} modules")

    for name in missing:
        print(f"  MISSING     {name} is imported but does not exist")

    for name in staged:
        print(f"  STAGED      js/{name} (exercised by tests/evals, not yet in the app)")

    total = 0
    for name in dead:
        with open(os.path.join(JS_DIR, name)) as fh:
            lines = sum(1 for _ in fh)
        total += lines
        print(f"  DEAD        js/{name} ({lines} lines) -- nothing imports it")

    if staged:
        print(f"\n{len(staged)} staged module(s): reached by tests, not by the app.")
    if dead:
        print(f"\n{len(dead)} dead module(s), {total} lines")
    if missing:
        print(f"{len(missing)} imported module(s) absent from disk")
    if not dead and not missing and not staged:
        print("\nall modules reachable from the app")

    return 1 if (dead or missing) else 0


if __name__ == "__main__":
    sys.exit(main())
