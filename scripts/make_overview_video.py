#!/usr/bin/env python3
"""Render a long-form overview from the documentation this repository already has.

The two-minute film is a pitch: ten slides, hand-authored, built to be watched
by someone deciding whether to care. This is the other thing — a walkthrough for
someone who has already decided and now wants the detail, chaptered the way the
documentation is chaptered.

WHY IT IS GENERATED RATHER THAN WRITTEN. A hand-authored twenty-minute script
would be a third copy of the same claims, drifting away from the wiki and the
whitepaper the way every other copy in this repository has drifted. This reads
the documents themselves, so the film cannot say something the documentation
does not. When a page is corrected the next render is corrected with it.

WHAT IT REFUSES TO DO. It will not pad. A slide needs a heading and a passage
long enough to be worth reading; sections that are a link, a table or three
words are skipped rather than stretched, and `--report` prints how much real
material exists before anything is rendered. If that comes to twelve minutes,
twelve minutes is the honest length — a twenty-minute film made of eight
minutes of content is worse than the eight.

    python scripts/make_overview_video.py --report          # what exists, renders nothing
    python scripts/make_overview_video.py --out docs/overview.mp4
    python scripts/make_overview_video.py --limit 3 --stills /tmp/preview   # cheap look

Rendering is the heavy half. Check `uptime` first and coordinate with other
sessions on this machine before starting a full run.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import ImageDraw  # noqa: E402

from make_pitch_video import (  # noqa: E402
    ACCENT, DIM, FAINT, H, INK, W,
    body, brand, eyebrow, font, gradient_bg, headline, plate, wrap,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The chapters, in the order a reader should meet them: what it is, then how it
# is driven, then the evidence, then the parts that are not finished. Known
# Limits is late on purpose — it lands harder after the claims it qualifies.
CHAPTERS = [
    ("What this is", ["docs/wiki/Home.md", "docs/wiki/Getting-Started.md"]),
    ("Driving it", ["docs/wiki/Voice-and-Agent-Control.md", "docs/wiki/XR-and-Hand-Tracking.md"]),
    ("The science", ["docs/wiki/Docking-and-Scoring.md", "docs/wiki/Data-Sources.md"]),
    ("Agents and provenance", ["docs/wiki/Agent-Protocols.md", "docs/wiki/Provenance-Ledger.md"]),
    ("How it is checked", ["docs/wiki/Testing.md", "docs/WHITE_PAPER.md"]),
    ("The questions buyers ask", ["docs/QA.md"]),
    ("Where it falls short", ["docs/wiki/Known-Limits.md"]),
]

# A passage shorter than this is a stub, a cross-reference or a caption, and a
# slide made of it is padding. Measured against the pages: the shortest passage
# worth a slide runs about this long.
MIN_CHARS = 180
MAX_CHARS = 560


def clean(md):
    """Markdown to something a slide can show, without changing what it says."""
    md = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", md)            # images
    md = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", md)        # links keep their text
    md = re.sub(r"`([^`]+)`", r"\1", md)                    # code spans
    md = re.sub(r"\*\*([^*]+)\*\*", r"\1", md)              # bold
    md = re.sub(r"(?<!\w)\*([^*]+)\*(?!\w)", r"\1", md)     # italic
    md = re.sub(r"<[^>]+>", "", md)                         # inline html
    md = md.replace("&mdash;", "—").replace("&amp;", "&").replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", md).strip()


def passages(path):
    """(heading, passage) per '##' section, skipping what cannot carry a slide.

    Only prose counts. A section whose body is a table, a code block or a list
    of links has nothing a viewer can read at 1080p in twelve seconds, and
    turning it into a slide would be the padding this script exists to avoid.
    """
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return []
    text = open(full, encoding="utf-8").read()

    out = []
    # Two OR three hashes. The first version split on "## " alone, which quietly
    # dropped 22 of QA.md's 27 entries -- that document asks its questions as
    # "### ", so the richest source of buyer-facing material contributed five
    # slides instead of twenty-seven and the shortfall looked like missing
    # content rather than a missing character.
    for block in re.split(r"\n(?=#{2,3} )", text):
        m = re.match(r"##+\s*(.+)", block)
        if not m:
            continue
        heading = clean(m.group(1))
        rest = block[m.end():]

        rest = re.sub(r"```.*?```", "", rest, flags=re.S)       # code fences
        rest = re.sub(r"^\s*\|.*$", "", rest, flags=re.M)       # table rows
        rest = re.sub(r"^\s*>.*$", "", rest, flags=re.M)        # block quotes

        for para in re.split(r"\n\s*\n", rest):
            p = clean(para)
            if len(p) < MIN_CHARS or p.startswith(("-", "*", "1.")):
                continue
            # Truncate on a sentence boundary, never mid-claim: a passage cut
            # after "the benchmark is not" would invert its own meaning.
            if len(p) > MAX_CHARS:
                cut = p.rfind(". ", 0, MAX_CHARS)
                if cut < MIN_CHARS:
                    continue
                p = p[:cut + 1]
            out.append((heading, p))
            break                                               # one slide per section
    return out


def build_deck():
    deck = []
    for chapter, paths in CHAPTERS:
        items = [(src, h, p) for src in paths for (h, p) in passages(src)]
        if not items:
            continue
        deck.append(("chapter", chapter, f"{len(items)} sections", None))
        for src, heading, passage in items:
            deck.append(("slide", chapter, heading, (passage, os.path.basename(src))))
    return deck


def slide_chapter(title, sub):
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    eyebrow(d, "Chapter")
    headline(d, title, y=400, size=110)
    d.text((160, 560), sub, font=font("mono", 30), fill=FAINT)
    brand(d)
    return img


def slide_section(chapter, heading, passage, source):
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    eyebrow(d, chapter)
    y = headline(d, heading, size=64, width=1500)

    # Size the plate to the text. A fixed 340px box left a third of itself empty
    # under a short passage and would have clipped a long one.
    lines = wrap(d, passage, font("body", 32), 1500)
    plate_h = max(150, 80 + len(lines) * 46)
    plate(d, [160, y + 60, 1760, y + 60 + plate_h])
    body(d, passage, y + 100, size=32, width=1500, color=INK)

    # Top right, not bottom left: at the bottom it sat on top of the brand mark.
    sf = font("mono", 22)
    d.text((1760 - sf.getbbox(source)[2], 124), source, font=sf, fill=FAINT)
    brand(d)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "overview.mp4"))
    ap.add_argument("--seconds-per-slide", type=float, default=12.0)
    ap.add_argument("--chapter-seconds", type=float, default=4.0)
    ap.add_argument("--report", action="store_true", help="what exists; render nothing")
    ap.add_argument("--limit", type=int, default=0, help="first N frames only")
    ap.add_argument("--stills", help="write PNGs here instead of a film")
    a = ap.parse_args()

    deck = build_deck()
    sections = [x for x in deck if x[0] == "slide"]
    chapters = [x for x in deck if x[0] == "chapter"]
    total = len(sections) * a.seconds_per_slide + len(chapters) * a.chapter_seconds

    print(f"{len(sections)} sections across {len(chapters)} chapters")
    for name, _ in CHAPTERS:
        n = sum(1 for x in sections if x[1] == name)
        if n:
            print(f"  {name:28} {n:3} sections")
    print(f"\nat {a.seconds_per_slide:.0f}s per section: {total / 60:.1f} minutes")
    if a.report:
        print("\n--report: nothing rendered.")
        return 0

    frames = deck[: a.limit] if a.limit else deck
    out_dir = a.stills or tempfile.mkdtemp(prefix="overview-")
    os.makedirs(out_dir, exist_ok=True)

    paths = []
    for i, item in enumerate(frames):
        kind = item[0]
        img = (slide_chapter(item[2], item[3] if len(item) > 3 and item[3] else "")
               if kind == "chapter"
               else slide_section(item[1], item[2], item[3][0], item[3][1]))
        png = os.path.join(out_dir, f"{i:03d}.png")
        img.save(png)
        paths.append((png, a.chapter_seconds if kind == "chapter" else a.seconds_per_slide))
        print(f"  {i + 1}/{len(frames)} {kind}", end="\r", flush=True)
    print()

    if a.stills:
        print(f"wrote {len(paths)} stills to {out_dir}")
        return 0

    if not shutil.which("ffmpeg"):
        print("ffmpeg is not on PATH; the stills are in", out_dir)
        return 1

    concat = os.path.join(out_dir, "list.txt")
    with open(concat, "w") as fh:
        for png, secs in paths:
            fh.write(f"file '{png}'\nduration {secs}\n")
        fh.write(f"file '{paths[-1][0]}'\n")          # last frame needs repeating
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", concat, "-c:v", "libx264", "-preset", "slow", "-crf", "26",
                    "-pix_fmt", "yuv420p", "-r", "30", "-movflags", "+faststart", a.out],
                   check=True)
    print(f"wrote {a.out}: {total / 60:.1f} min, "
          f"{os.path.getsize(a.out) / 1024 / 1024:.1f} MB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
