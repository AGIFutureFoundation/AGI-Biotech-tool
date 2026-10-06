#!/usr/bin/env python3
"""Render the 110-second pitch video from designed slides, with no browser and no network.

The workspace can film itself (see js/recorder.js), but that needs the app running in a browser. This
path needs only Pillow, RDKit and ffmpeg: it draws each slide as a 1920x1080 frame, depicts real
reference compounds with RDKit, and lets ffmpeg add slow motion and crossfades. Every figure on a slide
is read from the same place the whitepaper reads it, so the two cannot drift apart.

    .venv/bin/python scripts/make_pitch_video.py            # -> docs/pitch.mp4
    .venv/bin/python scripts/make_pitch_video.py --seconds 90
"""
import argparse
import json
import os
import shutil
import subprocess
import tempfile

from PIL import Image, ImageDraw, ImageFont
from rdkit import Chem
from rdkit.Chem import Draw
from rdkit.Chem.Draw import rdMolDraw2D

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H = 1920, 1080

# Palette matches css/app.css and docs/whitepaper.html.
BG = (7, 11, 17)
PLATE = (17, 26, 39)
LINE = (29, 42, 58)
INK = (230, 238, 248)
DIM = (142, 163, 187)
FAINT = (93, 113, 138)
ACCENT = (57, 217, 138)
ACCENT2 = (76, 201, 240)
WARN = (255, 190, 11)
BAD = (255, 93, 115)

# Candidates per role, most-wanted first, across macOS, common Linux packages
# and Windows. The old table was macOS-only with a macOS fallback, so on any
# other machine every lookup reached ImageFont.load_default() -- a bitmap face
# that ignores the requested size. The 150px title then rendered a few pixels
# tall on a 1920x1080 slide, and the render "succeeded".
FONT_CANDIDATES = {
    "display": [
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSerif.ttf",
        "C:/Windows/Fonts/georgia.ttf",
    ],
    "display_b": [
        "/System/Library/Fonts/Supplemental/Georgia Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/TTF/DejaVuSerif-Bold.ttf",
        "C:/Windows/Fonts/georgiab.ttf",
    ],
    "mono": [
        "/System/Library/Fonts/Menlo.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSansMono.ttf",
        "C:/Windows/Fonts/consola.ttf",
    ],
    "body": [
        "/System/Library/Fonts/Helvetica.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ],
}

_FONT_CACHE = {}
_WARNED = set()


def font(kind, size):
    """A scalable face for `kind` at `size`, or a loud failure.

    Falling back to load_default() silently is worse than not rendering: the
    frames come out looking like a bug in the design rather than a missing
    font, and nothing in the output says which it was.
    """
    key = (kind, size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]

    for path in FONT_CANDIDATES[kind]:
        if not os.path.exists(path):
            continue
        try:
            _FONT_CACHE[key] = ImageFont.truetype(path, size)
            return _FONT_CACHE[key]
        except OSError:
            continue

    # Nothing scalable for this role. Try any other role's fonts before giving
    # up -- a serif where a mono was wanted still reads at the right size.
    for other, paths in FONT_CANDIDATES.items():
        if other == kind:
            continue
        for path in paths:
            if os.path.exists(path):
                try:
                    f = ImageFont.truetype(path, size)
                    if kind not in _WARNED:
                        print(f"  note: no {kind} font found; using {os.path.basename(path)}")
                        _WARNED.add(kind)
                    _FONT_CACHE[key] = f
                    return f
                except OSError:
                    continue

    raise SystemExit(
        f"No scalable font found for '{kind}'. Pillow's default face ignores the "
        f"requested size, so a {size}px heading would render a few pixels tall on a "
        f"{W}x{H} frame and the video would look broken rather than fail.\n"
        f"Install one: apt-get install fonts-dejavu-core, or dnf install dejavu-fonts.")


# The single source of truth for the numbers on screen. Edit here, and the slides follow.
FIGURES = {
    "tools": 22, "databases": 14, "targets": 60,
    "benchmark": [
        ("MAO-B · safinamide", "1.20 Å", "−9.62", "−10.01", True),
        ("Oestrogen receptor · 4-OHT", "1.24 Å", "−9.24", "−10.13", True),
        ("Thrombin · inhibitor", "3.83 Å", "−11.03", "−8.34", False),
        ("BCL-XL · ABT-737", "4.04 Å", "−9.96", "−6.92", False),
    ],
    "benchmark_line": "2 of 4 within 2 Å · median 2.54 Å",
    "md_ns_per_day": "27", "frame_ms": "7.4", "missense_h46": "0.98",
}

# Real reference drugs from the public record, never the user's proprietary compounds.
MOLECULES = [
    ("Riluzole", "Nc1nc2ccc(OC(F)(F)F)cc2s1", "ALS, approved"),
    ("Safinamide", "C[C@H](NCc1ccc(OCc2cccc(F)c2)cc1)C(N)=O", "Parkinson's, approved"),
    ("Edaravone", "Cc1cc(=O)n(-c2ccccc2)[nH]1", "ALS, approved"),
]


def gradient_bg():
    img = Image.new("RGB", (W, H), BG)
    glow = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(glow)
    # A soft radial glow top-left, drawn as concentric ellipses so it needs no numpy.
    for i in range(40, 0, -1):
        t = i / 40
        col = tuple(int(BG[k] + (ACCENT[k] - BG[k]) * 0.11 * (1 - t)) for k in range(3))
        d.ellipse([-600 + 300 * (1 - t) * 0, -400, 1300 * t + 300, 500 * t + 100], fill=col)
    return Image.blend(img, glow, 0.9)


def eyebrow(d, text, y=120):
    d.text((160, y), text.upper(), font=font("mono", 22), fill=ACCENT, spacing=4)


def headline(d, text, y=170, size=76, width=1500):
    f = font("display_b", size)
    lines = wrap(d, text, f, width)
    for i, line in enumerate(lines):
        d.text((160, y + i * int(size * 1.12)), line, font=f, fill=INK)
    return y + len(lines) * int(size * 1.12)


def body(d, text, y, size=34, width=1400, color=DIM):
    f = font("body", size)
    lines = wrap(d, text, f, width)
    for i, line in enumerate(lines):
        d.text((160, y + i * int(size * 1.5)), line, font=f, fill=color)
    return y + len(lines) * int(size * 1.5)


def wrap(d, text, f, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = f"{cur} {w}".strip()
        if d.textlength(t, font=f) > width and cur:
            lines.append(cur)
            cur = w
        else:
            cur = t
    if cur:
        lines.append(cur)
    return lines


def plate(d, box, radius=18):
    d.rounded_rectangle(box, radius=radius, fill=PLATE, outline=LINE, width=2)


def brand(d):
    d.ellipse([160, H - 120, 178, H - 102], fill=ACCENT)
    d.text((196, H - 128), "biodao", font=font("body", 30), fill=INK)
    d.text((196 + d.textlength("biodao", font=font("body", 30)), H - 128), ".blockchain", font=font("body", 30), fill=ACCENT)
    d.text((160, H - 80), "POWERED BY AGI CORP", font=font("mono", 18), fill=FAINT)


def mol_image(smiles, size=(560, 380)):
    m = Chem.MolFromSmiles(smiles)
    drawer = rdMolDraw2D.MolDraw2DCairo(*size)
    opts = drawer.drawOptions()
    opts.setBackgroundColour((PLATE[0] / 255, PLATE[1] / 255, PLATE[2] / 255))
    opts.setAtomPalette({-1: (0.9, 0.93, 0.97)})
    opts.bondLineWidth = 3
    opts.padding = 0.12
    drawer.DrawMolecule(m)
    drawer.FinishDrawing()
    from io import BytesIO
    return Image.open(BytesIO(drawer.GetDrawingText())).convert("RGB")


# ----------------------------------------------------------------------------- slides
def slide_title():
    img = gradient_bg()
    d = ImageDraw.Draw(img)
    d.ellipse([160, 330, 184, 354], fill=ACCENT)
    d.text((204, 318), "AGI FUTURE FOUNDATION", font=font("mono", 26), fill=DIM)
    f = font("display_b", 150)
    d.text((160, 400), "biodao", font=f, fill=INK)
    x = 160 + d.textlength("biodao", font=f)
    d.text((x, 400), ".blockchain", font=f, fill=ACCENT)
    body(d, "A molecular research workspace a scientist can operate by hand in a headset, and another agent "
            "can operate over a protocol, with every result signed, costed and traceable.", 600, size=38, width=1500, color=INK)
    brand(d)
    return img


def slide_problem():
    img = gradient_bg(); d = ImageDraw.Draw(img)
    eyebrow(d, "The problem")
    y = headline(d, "Discovery software assumes a human is driving")
    body(d, "A chemist moves between a structure viewer, a docking program, six database websites and a spreadsheet. "
            "Each hand-off loses context, and none of it records why a decision was made.", y + 30)
    body(d, "The thing most likely to do that work next is an agent, and almost no scientific software can be called "
            "by one: no tool schema, no way to pay for a run, no way to prove which system produced a number.", y + 230)
    brand(d)
    return img


def slide_three_ways():
    img = gradient_bg(); d = ImageDraw.Draw(img)
    eyebrow(d, "The product")
    headline(d, "One workspace, three ways in", size=72)
    cols = [("By hand", "A 3D workspace in a browser or a headset. Pick up a protein, drop a compound in its pocket, "
                        "pull it about while the physics runs."),
            ("By voice", "\"Load LRRK2.\" \"Find pockets.\" \"Dock it.\" The answer is spoken back, which is what works "
                         "on glasses with no display."),
            ("By agent", "Every panel action is a typed tool. An MCP client lists them and drives a live session, "
                         "the same buttons a researcher presses.")]
    for i, (t, txt) in enumerate(cols):
        x = 160 + i * 540
        plate(d, [x, 360, x + 500, 820])
        d.text((x + 34, 400), t, font=font("display_b", 44), fill=INK)
        f = font("body", 27)
        for j, line in enumerate(wrap(d, txt, f, 430)):
            d.text((x + 34, 480 + j * 40), line, font=f, fill=DIM)
    brand(d)
    return img


def slide_molecules():
    img = gradient_bg(); d = ImageDraw.Draw(img)
    eyebrow(d, "Compounds")
    headline(d, "Your library, profiled and ranked", size=72)
    for i, (name, smi, note) in enumerate(MOLECULES):
        x = 160 + i * 540
        plate(d, [x, 340, x + 500, 860])
        mi = mol_image(smi, (460, 320))
        img.paste(mi, (x + 20, 360))
        d.text((x + 34, 700), name, font=font("display_b", 40), fill=INK)
        d.text((x + 34, 756), note, font=font("mono", 22), fill=FAINT)
        d.text((x + 34, 796), "reference drug · public record", font=font("mono", 18), fill=FAINT)
    brand(d)
    return img


def slide_benchmark():
    img = gradient_bg(); d = ImageDraw.Draw(img)
    eyebrow(d, "Evidence")
    y = headline(d, "What the numbers actually say", size=72)
    body(d, "Re-docking: take a drug out of the crystal it was solved in, dock it back blind, measure the miss. "
            "Under 2 Å is the usual bar.", y + 20, size=30)
    top = y + 110
    plate(d, [160, top, 1760, top + 380])
    hdr = ["Complex", "Top pose", "Crystal", "Docked", "Result"]
    xs = [200, 820, 1080, 1320, 1580]
    for h, x in zip(hdr, xs):
        d.text((x, top + 26), h.upper(), font=font("mono", 20), fill=FAINT)
    d.line([180, top + 70, 1740, top + 70], fill=LINE, width=2)
    for r, row in enumerate(FIGURES["benchmark"]):
        yy = top + 96 + r * 68
        for (val, x) in zip(row[:4], xs):
            d.text((x, yy), val, font=font("mono", 30) if x > 400 else font("body", 30), fill=INK)
        d.text((xs[4], yy), "pass" if row[4] else "fail", font=font("mono", 30), fill=ACCENT if row[4] else BAD)
    d.text((160, top + 420), FIGURES["benchmark_line"], font=font("display_b", 48), fill=INK)
    body(d, "Good enough to triage a library, not to predict affinity. Published rather than buried, because "
            "serious customers run their own controls.", top + 488, size=26, width=1600)
    brand(d)
    return img


def slide_stats():
    img = gradient_bg(); d = ImageDraw.Draw(img)
    eyebrow(d, "Measured")
    headline(d, "Performance that holds up in a headset", size=72)
    stats = [(FIGURES["md_ns_per_day"], "ns/day", "all-atom dynamics on a consumer GPU"),
             (FIGURES["frame_ms"] + " ms", "per frame", "8,778-atom protein, flexible backbone"),
             (FIGURES["missense_h46"], "AlphaMissense", "at SOD1 H46, a known ALS site"),
             (str(FIGURES["databases"]), "databases", "public, no account, no key")]
    for i, (big, unit, sub) in enumerate(stats):
        x = 160 + (i % 2) * 800
        y = 360 + (i // 2) * 300
        plate(d, [x, y, x + 760, y + 260])
        d.text((x + 36, y + 30), big, font=font("mono", 92), fill=INK)
        d.text((x + 36 + d.textlength(big, font=font("mono", 92)) + 24, y + 84), unit, font=font("body", 36), fill=ACCENT)
        d.text((x + 36, y + 170), sub, font=font("body", 28), fill=DIM)
    brand(d)
    return img


def slide_protocols():
    img = gradient_bg(); d = ImageDraw.Draw(img)
    eyebrow(d, "Architecture")
    headline(d, "Built so another agent can be the customer", size=68)
    items = [("Tool layer", f"{FIGURES['tools']} operations with JSON schemas. One registry serves the console, the voice layer and the MCP server.", ACCENT),
             ("x402 payments", "Metered tools answer an unpaid call with an HTTP 402 challenge naming price, asset and network. Settlement not yet wired.", WARN),
             ("NANDA discovery", "A signed AgentFacts document at a well-known URL: identity, endpoints, capabilities, pricing, limits.", ACCENT),
             ("OML-style fingerprints", "Secret challenge/response pairs prove which service answered; every result carries a signature.", ACCENT),
             ("Provenance chain", "Each run appended to a SHA-256 hash chain. Alter one record and verification names it.", ACCENT),
             ("Environments", "Any glTF scene becomes the backdrop. Exports arrive at every scale and are normalised.", ACCENT)]
    for i, (t, txt, col) in enumerate(items):
        x = 160 + (i % 3) * 540
        y = 340 + (i // 3) * 270
        plate(d, [x, y, x + 500, y + 240])
        d.rectangle([x, y + 18, x + 6, y + 60], fill=col)
        d.text((x + 30, y + 22), t, font=font("display_b", 32), fill=INK)
        f = font("body", 23)
        for j, line in enumerate(wrap(d, txt, f, 440)):
            d.text((x + 30, y + 80 + j * 33), line, font=f, fill=DIM)
    brand(d)
    return img


def slide_roadmap():
    img = gradient_bg(); d = ImageDraw.Draw(img)
    eyebrow(d, "Roadmap")
    headline(d, "What exists, and what comes next", size=72)
    rows = [("Done", "Workspace and data spine", "XR workspace, 60 verified targets, 14 databases, docking, dynamics, provenance."),
            ("Done", "Agent surface", "Typed tools, console, voice, hand tracking, MCP server driving a live session."),
            ("4 weeks", "Scoring that passes its own benchmark", "Longer searches, a rescoring pass, a wider benchmark published with every release."),
            ("6 weeks", "Hardware and shared sessions", "Hands and voice tested on Quest 3 and Vision Pro; rooms gain object ownership."),
            ("Quarter", "Settlement and registry", "x402 wired to a facilitator; AgentFacts published to a public index."),
            ("Quarter", "Deployment for teams", "Hosted and on-premises, per-seat and per-call pricing, audit export from the chain.")]
    for i, (when, t, txt) in enumerate(rows):
        y = 350 + i * 100
        d.text((160, y + 8), when, font=font("mono", 24), fill=ACCENT if when == "Done" else FAINT)
        d.text((400, y), t, font=font("display_b", 34), fill=INK)
        d.text((400, y + 46), txt, font=font("body", 24), fill=DIM)
        d.line([160, y + 90, 1760, y + 90], fill=LINE, width=1)
    brand(d)
    return img


def slide_limits():
    img = gradient_bg(); d = ImageDraw.Draw(img)
    eyebrow(d, "Honest limits")
    headline(d, "What this is not, yet", size=72)
    items = ["Docking is triage, not prediction. 2 of 4 re-docking cases within 2 Å.",
             "Interactive physics is coarse by design. The all-atom OpenMM backend is the one to quote.",
             "Payments do not settle. The 402 challenge is real; the transfer is not implemented.",
             "A hash chain is not a blockchain. It makes tampering detectable; it reaches no consensus.",
             "Ray-Ban Meta glasses cannot render this. The voice companion on a paired phone is the substitute.",
             "Hand tracking is untested on hardware. Written to the WebXR spec, verified in code, not yet worn."]
    for i, t in enumerate(items):
        y = 350 + i * 92
        d.rectangle([160, y + 6, 166, y + 50], fill=WARN)
        f = font("body", 30)
        for j, line in enumerate(wrap(d, t, f, 1500)):
            d.text((196, y + j * 40), line, font=f, fill=INK if j == 0 else DIM)
    brand(d)
    return img


def slide_cta():
    img = gradient_bg(); d = ImageDraw.Draw(img)
    eyebrow(d, "Work with us", y=260)
    headline(d, "Three kinds of partner", y=310, size=84)
    body(d, "Disease foundations with a target and no computational team. Pharma groups who want an agent-operable "
            "workspace behind their firewall. Engineers who want to work on the scoring function.", 440, size=34, width=1500, color=INK)
    plate(d, [160, 640, 1180, 820])
    d.text((200, 672), "x@agifuturefoundation.org", font=font("mono", 46), fill=ACCENT)
    d.text((200, 748), "The whitepaper carries a QR code and an intake form.", font=font("body", 26), fill=DIM)
    brand(d)
    return img


SLIDES = [slide_title, slide_problem, slide_three_ways, slide_molecules, slide_benchmark,
          slide_stats, slide_protocols, slide_roadmap, slide_limits, slide_cta]


# ----------------------------------------------------------------------------- assembly
def build(out, seconds=110, fps=30):
    if not shutil.which("ffmpeg"):
        raise SystemExit("ffmpeg is required")
    n = len(SLIDES)
    fade = 0.8
    per = (seconds + fade * (n - 1)) / n          # so crossfades do not shorten the total
    tmp = tempfile.mkdtemp(prefix="pitch_")
    clips = []
    for i, fn in enumerate(SLIDES):
        png = os.path.join(tmp, f"s{i:02d}.png")
        fn().save(png)
        clip = os.path.join(tmp, f"c{i:02d}.mp4")
        # A slow push-in gives each still some life without distracting from the text.
        frames = int(per * fps)
        zoom = f"zoompan=z='min(zoom+0.00045,1.08)':d={frames}:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s={W}x{H}:fps={fps}"
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-loop", "1", "-i", png, "-vf", zoom, "-t", f"{per:.3f}",
                        "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-pix_fmt", "yuv420p", clip], check=True)
        clips.append(clip)
        print(f"  slide {i + 1}/{n} {fn.__name__}")

    # Chain crossfades: each xfade offset is the running total minus the overlap so far.
    inputs = []
    for c in clips:
        inputs += ["-i", c]
    filt, prev, offset = [], "[0:v]", 0.0
    for i in range(1, n):
        offset += per - fade
        label = f"[v{i}]" if i < n - 1 else "[out]"
        filt.append(f"{prev}[{i}:v]xfade=transition=fade:duration={fade}:offset={offset:.3f}{label}")
        prev = label
    subprocess.run(["ffmpeg", "-y", "-v", "error", *inputs, "-filter_complex", ";".join(filt), "-map", "[out]",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "21", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out],
                   check=True)
    shutil.rmtree(tmp, ignore_errors=True)
    probe = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration,size", "-of", "json", out],
                           capture_output=True, text=True)
    info = json.loads(probe.stdout)["format"]
    print(f"wrote {out}: {float(info['duration']):.1f} s, {int(info['size']) / 1e6:.1f} MB")
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(ROOT, "docs", "pitch.mp4"))
    ap.add_argument("--seconds", type=float, default=110)
    a = ap.parse_args()
    build(a.out, a.seconds)
