#!/usr/bin/env python3
"""Report JavaScript modules that nothing in the app can reach.

index.html loads a small number of entry scripts; everything else arrives
through ES import chains. A file outside those chains is dead weight that still
looks maintained -- this repo carried six such files, 1,726 lines, including one
that was a syntax error and so could never have loaded at all.

Exits non-zero when anything is unreachable, so it works as a CI gate.

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

    reached, queue = set(), list(entries)
    while queue:
        name = queue.pop()
        if name in reached:
            continue
        reached.add(name)
        queue.extend(imports_of(name))

    on_disk = {f for f in os.listdir(JS_DIR) if f.endswith(".js")}
    unreachable = sorted(on_disk - reached)
    missing = sorted(reached - on_disk)

    print(f"entry points : {', '.join(entries)}")
    print(f"reachable    : {len(reached & on_disk)} of {len(on_disk)} modules")

    for name in missing:
        print(f"  MISSING     {name} is imported but does not exist")

    total = 0
    for name in unreachable:
        with open(os.path.join(JS_DIR, name)) as fh:
            lines = sum(1 for _ in fh)
        total += lines
        print(f"  UNREACHABLE js/{name} ({lines} lines)")

    if unreachable:
        print(f"\n{len(unreachable)} unreachable module(s), {total} lines")
    if missing:
        print(f"{len(missing)} imported module(s) absent from disk")
    if not unreachable and not missing:
        print("\nall modules reachable")

    return 1 if (unreachable or missing) else 0


if __name__ == "__main__":
    sys.exit(main())
