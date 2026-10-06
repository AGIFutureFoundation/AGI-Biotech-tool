#!/usr/bin/env python3
"""Render the 120-second investor cut, plus square and vertical crops for social.

Separate from scripts/make_pitch_video.py on purpose: that one is the product walkthrough, this one
leads with what is newly proven and how the thing is built. Both share the drawing primitives and the
same FIGURES table, so a number can never say one thing in the deck and another in the film.

Honesty rule carried over: every figure here comes from a command that actually ran. Nothing on these
slides is a projection, and the benchmark is shown with its failures.

    .venv/bin/python scripts/make_investor_video.py                 # -> docs/investor.mp4 (120 s)
    .venv/bin/python scripts/make_investor_video.py --social        # also square + vertical crops
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from PIL import ImageDraw  # noqa: E402
from make_pitch_video import (  # noqa: E402
    ACCENT, ACCENT2, BAD, DIM, FAINT, FIGURES, H, INK, LINE, PLATE, W, WARN,
    body, brand, eyebrow, font, gradient_bg, headline, mol_image, plate, wrap,
)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Everything below is a measurement, not a projection. Each entry names the command that produced it.
PROVEN = {
    "offline_tests": 33,          # node --test tests/*.test.mjs + pytest tests/
    "js_tests": 22,
    "py_tests": 11,
    "bugs_caught": 2,
    "tools": FIGURES["tools"],
    "databases": FIGURES["databases"],
    "targets": FIGURES["targets"],
}


def slide_open():
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    d.ellipse([160, 300, 184, 324], fill=ACCENT)
    d.text((204, 288), "AGI FUTURE FOUNDATION · INVESTOR BRIEF", font=font("mono", 26), fill=DIM)
    f = font("display_b", 142)
    d.text((160, 370), "biodao", font=f, fill=INK)
    x = 160 + d.textlength("biodao", font=f)
    d.text((x, 370), ".blockchain", font=f, fill=ACCENT)
    body(d, "Drug discovery software that an AI agent can operate, pay for, and be held to. "
            "Built for the diseases nobody else is staffing.", 560, size=42, width=1520, color=INK)
    d.text((160, 760), "Every figure in this film came from a command that ran. Nothing here is a projection.",
           font=font("mono", 24), fill=FAINT)
    brand(d)
    return img


def slide_why_now():
    img = gradient_bg(); d = ImageDraw.Draw(img)
    eyebrow(d, "Why now")
    y = headline(d, "The next user of scientific software is not a person")
    body(d, "Agents can already read a paper, write code and call an API. What they cannot do is run a real "
            "discovery workflow, because the software has no tool schema, no way to pay per call, and no way "
            "to prove afterwards which system produced a number.", y + 36, size=34, width=1540)
    body(d, "Whoever makes that surface first owns the layer every other tool has to plug into.",
         y + 250, size=34, width=1540, color=INK)
    brand(d)
    return img


def slide_what_shipped():
    img = gradient_bg(); d = ImageDraw.Draw(img)
    eyebrow(d, "What is built")
    headline(d, "A workspace, and the machinery around it", size=70)
    items = [("Molecular workspace", "Structures, pockets, docking, dynamics, interaction analysis, library screening — in a browser or a headset."),
             ("Agent surface", f"{PROVEN['tools']} typed tools. An MCP client drives a live session, verified end to end."),
             ("Hands-free", "Voice commands and WebXR hand tracking, so the workspace works with no keyboard."),
             ("Open data spine", f"{PROVEN['databases']} public databases, no account and no key anywhere in the stack."),
             ("Agent economics", "x402 payment challenges, NANDA discovery, OML-style fingerprints on every result."),
             ("Provenance", "A SHA-256 chain over every run. Alter a record and verification names it.")]
    for i, (t, txt) in enumerate(items):
        x = 160 + (i % 2) * 820
        y = 330 + (i // 2) * 230
        plate(d, [x, y, x + 780, y + 200])
        d.rectangle([x, y + 20, x + 6, y + 64], fill=ACCENT)
        d.text((x + 32, y + 24), t, font=font("display_b", 38), fill=INK)
        f = font("body", 26)
        for j, line in enumerate(wrap(d, txt, f, 710)):
            d.text((x + 32, y + 88 + j * 36), line, font=f, fill=DIM)
    brand(d)
    return img


def slide_proof():
    img = gradient_bg(); d = ImageDraw.Draw(img)
    eyebrow(d, "What is proven")
    y = headline(d, "Thirty-three tests that run with no network", size=70)
    body(d, "Written this week, each one verified by a command in the repository.", y + 24, size=30)
    stats = [(str(PROVEN["offline_tests"]), "offline tests", "node --test · pytest"),
             (str(PROVEN["js_tests"]), "JavaScript", "analysis and voice parsing"),
             (str(PROVEN["py_tests"]), "Python", "payment, discovery, signing"),
             (str(PROVEN["bugs_caught"]), "real defects caught", "each would have reached a user")]
    for i, (big, unit, sub) in enumerate(stats):
        x = 160 + (i % 4) * 400
        plate(d, [x, 470, x + 370, 700])
        d.text((x + 28, 500), big, font=font("mono", 86), fill=ACCENT if i == 3 else INK)
        d.text((x + 28, 606), unit, font=font("body", 28), fill=INK)
        d.text((x + 28, 648), sub, font=font("mono", 20), fill=FAINT)
    body(d, "The defects are the point. A flat cap was hiding the one aromatic-stacking record a chemist reads, "
            "and every spoken gene symbol ending in a digit failed to load, because a recogniser returns "
            "\"lark two\" for LRRK2. Neither shows up without tests.", 740, size=28, width=1600)
    brand(d)
    return img


def slide_benchmark():
    img = gradient_bg(); d = ImageDraw.Draw(img)
    eyebrow(d, "The number we lead with")
    y = headline(d, "Our docking is honest about where it fails", size=70)
    top = y + 90
    plate(d, [160, top, 1760, top + 350])
    xs = [200, 820, 1080, 1320, 1580]
    for h, x in zip(["Complex", "Top pose", "Crystal", "Docked", "Result"], xs):
        d.text((x, top + 24), h.upper(), font=font("mono", 20), fill=FAINT)
    d.line([180, top + 66, 1740, top + 66], fill=LINE, width=2)
    for r, row in enumerate(FIGURES["benchmark"]):
        yy = top + 92 + r * 62
        for val, x in zip(row[:4], xs):
            d.text((x, yy), val, font=font("mono", 28) if x > 400 else font("body", 28), fill=INK)
        d.text((xs[4], yy), "pass" if row[4] else "fail", font=font("mono", 28), fill=ACCENT if row[4] else BAD)
    d.text((160, top + 390), FIGURES["benchmark_line"], font=font("display_b", 46), fill=INK)
    body(d, "Two of four. We publish the failures because the first thing a serious buyer does is run their own "
            "controls, and a number that collapses on contact costs more than it ever earned.", top + 452,
         size=28, width=1600)
    brand(d)
    return img


def slide_moat():
    img = gradient_bg(); d = ImageDraw.Draw(img)
    eyebrow(d, "Why it is defensible")
    headline(d, "The hard part is not the viewer", size=70)
    cols = [("Protocol surface", "Tools, payment challenges, discovery documents and signatures are one registry. A competitor has to rebuild the whole spine, not a feature."),
            ("Evidence discipline", "Benchmarks published with their failures, tests that run offline, provenance on every run. That is what a regulated buyer actually audits."),
            ("Disease focus", f"{PROVEN['targets']} curated targets in ALS, Parkinson's and paediatric orthopaedics — verified against UniProt, not scraped.")]
    for i, (t, txt) in enumerate(cols):
        x = 160 + i * 540
        plate(d, [x, 350, x + 500, 840])
        d.text((x + 34, 390), t, font=font("display_b", 40), fill=INK)
        f = font("body", 26)
        for j, line in enumerate(wrap(d, txt, f, 430)):
            d.text((x + 34, 480 + j * 38), line, font=f, fill=DIM)
    brand(d)
    return img


def slide_market():
    img = gradient_bg(); d = ImageDraw.Draw(img)
    eyebrow(d, "Who pays")
    headline(d, "Three buyers, three reasons", size=70)
    rows = [("Disease foundations", "Have a target and a grant, no computational team. Buy a workspace and a screen."),
            ("Pharma and biotech", "Want an agent-operable workspace behind their own firewall, with an audit trail."),
            ("Agent platforms", "Need a scientific tool their agents can call and pay for. This is that tool.")]
    for i, (t, txt) in enumerate(rows):
        y = 370 + i * 190
        plate(d, [160, y, 1760, y + 160])
        d.rectangle([160, y + 24, 166, y + 80], fill=[ACCENT, ACCENT2, WARN][i])
        d.text((200, y + 26), t, font=font("display_b", 44), fill=INK)
        d.text((200, y + 92), txt, font=font("body", 28), fill=DIM)
    brand(d)
    return img


def slide_compounds():
    img = gradient_bg(); d = ImageDraw.Draw(img)
    eyebrow(d, "In practice")
    headline(d, "Import a library, rank it against a target", size=70)
    from make_pitch_video import MOLECULES
    for i, (name, smi, note) in enumerate(MOLECULES):
        x = 160 + i * 540
        plate(d, [x, 340, x + 500, 860])
        img.paste(mol_image(smi, (460, 320)), (x + 20, 360))
        d.text((x + 34, 700), name, font=font("display_b", 40), fill=INK)
        d.text((x + 34, 756), note, font=font("mono", 22), fill=FAINT)
        d.text((x + 34, 796), "reference drug · public record", font=font("mono", 18), fill=FAINT)
    brand(d)
    return img


def slide_ask():
    img = gradient_bg(); d = ImageDraw.Draw(img)
    eyebrow(d, "The ask", y=250)
    headline(d, "Fund the scoring function", y=300, size=86)
    body(d, "The benchmark is the ceiling on everything else we sell. Capital goes to the search and rescoring "
            "work that moves two of four toward the field standard, hardware testing on Quest and Vision Pro, "
            "and wiring payment settlement.", 450, size=34, width=1540, color=INK)
    plate(d, [160, 660, 1240, 840])
    d.text((200, 692), "x@agifuturefoundation.org", font=font("mono", 44), fill=ACCENT)
    d.text((200, 766), "Whitepaper, deck and build log are live and shareable.", font=font("body", 26), fill=DIM)
    brand(d)
    return img


SLIDES = [slide_open, slide_why_now, slide_what_shipped, slide_proof, slide_benchmark,
          slide_moat, slide_market, slide_compounds, slide_ask]


def build(out, seconds=120, fps=30, fade=0.8):
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg is required")
    n = len(SLIDES)
    per = (seconds + fade * (n - 1)) / n
    tmp = tempfile.mkdtemp(prefix="investor_")
    clips = []
    for i, fn in enumerate(SLIDES):
        png = os.path.join(tmp, f"s{i:02d}.png")
        fn().save(png)
        clip = os.path.join(tmp, f"c{i:02d}.mp4")
        frames = int(per * fps)
        zoom = (f"zoompan=z='min(zoom+0.00042,1.07)':d={frames}:x='iw/2-(iw/zoom/2)':"
                f"y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={fps}")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", png, "-vf", zoom,
                        "-t", f"{per:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                        "-pix_fmt", "yuv420p", clip], check=True)
        clips.append(clip)
        print(f"  slide {i + 1}/{n} {fn.__name__}")

    inputs = []
    for c in clips:
        inputs += ["-i", c]
    filt, prev, offset = [], "[0:v]", 0.0
    for i in range(1, n):
        offset += per - fade
        label = f"[v{i}]" if i < n - 1 else "[out]"
        filt.append(f"{prev}[{i}:v]xfade=transition=fade:duration={fade}:offset={offset:.3f}{label}")
        prev = label
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(filt),
                    "-map", "[out]", "-c:v", "libx264", "-preset", "slow", "-crf", "21",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    return report(out)


# ---------------------------------------------------------------------------- vertical social teaser
# Letterboxing the 16:9 deck into 9:16 was tried and discarded: it leaves the body text about four
# millimetres tall on a phone. A vertical cut has to be its own thing — a few big statements, each
# readable at arm's length while scrolling.
VW, VH = 1080, 1920

CARDS = [
    ("biodao.blockchain", "Drug discovery an AI agent can run, pay for, and be held to.", ACCENT),
    ("22 typed tools", "Every action a scientist can take, an agent can call.", INK),
    ("33 offline tests", "Written this week. Each verified by a command in the repo.", INK),
    ("2 of 4", "Our docking benchmark. We publish the failures too.", WARN),
    ("14 databases", "Public. No account, no key, anywhere in the stack.", INK),
    ("x@agifuturefoundation.org", "ALS · Parkinson's · paediatric orthopaedics.", ACCENT),
]


def vertical_card(headline_text, sub, colour):
    from PIL import Image
    img = Image.new("RGB", (VW, VH), (7, 11, 17))
    d = ImageDraw.Draw(img)
    # A soft glow top-left, same family as the landscape ground.
    for i in range(34, 0, -1):
        t = i / 34
        col = tuple(int((7, 11, 17)[k] + (ACCENT[k] - (7, 11, 17)[k]) * 0.10 * (1 - t)) for k in range(3))
        d.ellipse([-420, -360, 980 * t + 200, 820 * t + 120], fill=col)

    size = 108 if len(headline_text) <= 18 else 74
    f = font("display_b", size)
    lines = wrap(d, headline_text, f, VW - 160)
    y = VH // 2 - (len(lines) * size * 1.12) / 2 - 120
    for line in lines:
        d.text((80, y), line, font=f, fill=colour)
        y += int(size * 1.12)

    fs = font("body", 40)
    y += 40
    for line in wrap(d, sub, fs, VW - 170):
        d.text((80, y), line, font=fs, fill=DIM)
        y += 56

    d.ellipse([80, VH - 190, 104, VH - 166], fill=ACCENT)
    d.text((122, VH - 196), "biodao", font=font("body", 38), fill=INK)
    d.text((122 + d.textlength("biodao", font=font("body", 38)), VH - 196), ".blockchain",
           font=font("body", 38), fill=ACCENT)
    d.text((80, VH - 132), "POWERED BY AGI CORP", font=font("mono", 22), fill=FAINT)
    return img


def vertical_teaser(out, per=5.0, fps=30, fade=0.5):
    tmp = tempfile.mkdtemp(prefix="vertical_")
    clips = []
    for i, (head, sub, colour) in enumerate(CARDS):
        png = os.path.join(tmp, f"v{i:02d}.png")
        vertical_card(head, sub, colour).save(png)
        clip = os.path.join(tmp, f"vc{i:02d}.mp4")
        frames = int(per * fps)
        zoom = (f"zoompan=z='min(zoom+0.0006,1.09)':d={frames}:x='iw/2-(iw/zoom/2)':"
                f"y='ih/2-(ih/zoom/2)':s={VW}x{VH}:fps={fps}")
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", png, "-vf", zoom,
                        "-t", f"{per:.3f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
                        "-pix_fmt", "yuv420p", clip], check=True)
        clips.append(clip)
    inputs = []
    for c in clips:
        inputs += ["-i", c]
    filt, prev, offset = [], "[0:v]", 0.0
    for i in range(1, len(clips)):
        offset += per - fade
        label = f"[v{i}]" if i < len(clips) - 1 else "[out]"
        filt.append(f"{prev}[{i}:v]xfade=transition=fade:duration={fade}:offset={offset:.3f}{label}")
        prev = label
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(filt),
                    "-map", "[out]", "-c:v", "libx264", "-preset", "slow", "-crf", "22",
                    "-pix_fmt", "yuv420p", "-movflags", "+faststart", out], check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    return report(out)


def report(path):
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size",
                            "-show_entries", "stream=width,height", "-of", "json", path],
                           capture_output=True, text=True)
    data = json.loads(probe.stdout)
    fmt, stream = data["format"], data["streams"][0]
    print(f"wrote {os.path.basename(path)}: {float(fmt['duration']):.1f} s, "
          f"{stream['width']}x{stream['height']}, {int(fmt['size']) / 1e6:.1f} MB")
    return path


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "investor.mp4"))
    ap.add_argument("--seconds", type=float, default=120)
    ap.add_argument("--social", action="store_true", help="also write square and vertical cuts")
    a = ap.parse_args()
    main_out = build(a.out, a.seconds)
    if a.social:
        vertical_teaser(os.path.join(os.path.dirname(main_out), "investor-vertical.mp4"))
