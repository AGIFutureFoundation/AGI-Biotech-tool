#!/usr/bin/env python3
"""Publish docs/wiki/ to the repository's GitHub wiki.

The instructions in docs/wiki/README.md were a block of shell to paste by hand,
which is how a wiki drifts from the repository that is supposed to be its
source: the copy that gets pushed is whatever happened to be in the clipboard.
This does the same thing as a command, runs the page checks first, and refuses
to publish pages that fail them.

    .venv/bin/python scripts/publish_wiki.py            # check, then publish
    .venv/bin/python scripts/publish_wiki.py --dry-run  # check and show the plan

One thing it cannot do for you. GitHub will not accept a push to
<repo>.wiki.git until the wiki has at least one page, and there is no REST or
GraphQL endpoint that creates one -- the bootstrap is a browser-only action.
When that is the situation, this says so and prints the exact page to open,
rather than failing with git's "Repository not found", which reads like a
permissions problem and is not one.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WIKI_SRC = os.path.join(ROOT, "docs", "wiki")
MEDIA_SRC = os.path.join(ROOT, "docs", "media")
# Instructions for maintainers, not a wiki page.
NOT_A_PAGE = {"README.md"}

# A wiki page referencing an image it does not ship renders a broken-image icon,
# which is worse than no figure. Images a page embeds are copied in beside it.
#
# PNG and JPEG only, deliberately. GitHub serves a wiki's .svg as text/plain, so
# an <img> pointing at one shows nothing -- the charts here are rasterised from
# their SVG sources for that reason, and shipping the .svg as well would invite
# someone to reference it and get a blank.
MEDIA_EXT = (".png", ".jpg", ".jpeg", ".gif")


def run(cmd, cwd=None, check=True):
    return subprocess.run(cmd, cwd=cwd, check=check, capture_output=True, text=True)


def remote_wiki_url():
    """The wiki URL derived from origin, so a fork publishes to its own wiki."""
    origin = run(["git", "remote", "get-url", "origin"], cwd=ROOT).stdout.strip()
    origin = re.sub(r"\.git$", "", origin)
    if origin.startswith("git@"):                       # git@github.com:owner/repo
        origin = "https://" + origin[4:].replace(":", "/", 1)
    return origin + ".wiki.git", origin


def media_referenced(pages):
    """Image files the pages actually reference, so nothing unused ships."""
    want = set()
    for page in pages:
        src = open(os.path.join(WIKI_SRC, page)).read()
        for m in re.finditer(r"!\[[^\]]*\]\(([^)]+)\)", src):
            target = m.group(1).strip()
            if target.startswith(("http:", "https:", "/")):
                continue                      # hosted elsewhere, not ours to ship
            want.add(os.path.basename(target))
    return sorted(want)


def check_pages():
    """The page rules are mechanical; run them rather than trusting the author."""
    test = os.path.join(ROOT, "tests", "wiki.test.mjs")
    if not os.path.exists(test):
        print("  ! tests/wiki.test.mjs is missing; publishing unchecked pages")
        return
    r = run(["node", "--test", test], cwd=ROOT, check=False)
    if r.returncode != 0:
        sys.exit("wiki page checks failed; not publishing.\n\n" + r.stdout[-3000:])
    print("  page checks pass")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="check and report, publish nothing")
    ap.add_argument("--message", default="Sync wiki from docs/wiki")
    a = ap.parse_args()

    pages = sorted(f for f in os.listdir(WIKI_SRC)
                   if f.endswith(".md") and f not in NOT_A_PAGE)
    if not pages:
        sys.exit(f"no pages in {WIKI_SRC}")

    media = media_referenced(pages)
    missing_media = [m for m in media
                     if not os.path.exists(os.path.join(MEDIA_SRC, m))]
    if missing_media:
        sys.exit("pages reference images that are not in docs/media: "
                 + ", ".join(missing_media))
    bad_ext = [m for m in media if not m.lower().endswith(MEDIA_EXT)]
    if bad_ext:
        sys.exit("GitHub wikis do not render these inline; rasterise them first: "
                 + ", ".join(bad_ext))

    wiki_url, repo_url = remote_wiki_url()
    print(f"source : docs/wiki ({len(pages)} pages, {len(media)} images)")
    print(f"target : {wiki_url}")
    check_pages()

    if a.dry_run:
        for p in pages:
            print(f"    {p[:-3].replace('-', ' ')}  <- docs/wiki/{p}")
        for m in media:
            size = os.path.getsize(os.path.join(MEDIA_SRC, m))
            print(f"    [image] {m}  ({size // 1024} KB)")
        return 0

    tmp = tempfile.mkdtemp(prefix="wiki-")
    try:
        clone = run(["git", "clone", "--quiet", wiki_url, tmp], check=False)
        if clone.returncode != 0:
            err = (clone.stderr or "").lower()
            if "not found" in err or "could not read" in err:
                print(f"""
The wiki has no pages yet, so GitHub will not accept a push to it.

This is not a permissions problem and there is no API for it: the first page
has to be created once in the browser, after which this command owns the wiki.

  1. open {repo_url}/wiki
  2. click "Create the first page", put anything in it, save
  3. run this command again -- it overwrites that page with docs/wiki/Home.md
""".rstrip())
                return 2
            sys.exit("could not clone the wiki:\n" + clone.stderr)

        for f in os.listdir(tmp):
            if f != ".git":
                os.remove(os.path.join(tmp, f))
        for p in pages:
            shutil.copyfile(os.path.join(WIKI_SRC, p), os.path.join(tmp, p))
        for m in media:
            shutil.copyfile(os.path.join(MEDIA_SRC, m), os.path.join(tmp, m))

        run(["git", "add", "-A"], cwd=tmp)
        status = run(["git", "status", "--porcelain"], cwd=tmp).stdout.strip()
        if not status:
            print("  wiki already matches docs/wiki; nothing to push")
            return 0

        run(["git", "commit", "-q", "-m", a.message], cwd=tmp)
        push = run(["git", "push", "--quiet"], cwd=tmp, check=False)
        if push.returncode != 0:
            sys.exit("push failed:\n" + push.stderr)
        print(f"  published {len(pages)} pages and {len(media)} images -> {repo_url}/wiki")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
