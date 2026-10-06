"""The renderer must not quietly draw a 150px heading at 8px.

FONTS was a table of four macOS paths with a macOS path as its fallback, and
font() ended in `except OSError: return ImageFont.load_default()`. On any
machine without /System/Library/Fonts -- CI, a Linux box, a colleague's
Windows laptop -- every lookup walked off the end of that table into
load_default(), which is a fixed bitmap face: it accepts a size argument and
ignores it.

Measured, on the title string at the size the title slide asks for:

    load_default()              -> 47 x 8 px
    truetype(Georgia, 150)      -> 670 x 115 px

So the deck still rendered, exit code 0, no warning, and a 1920x1080 frame
came out with a caption-sized title adrift in the top-left corner. A failure
that looks like a design mistake is worse than one that stops: there is
nothing in the output pointing at the missing font.

These tests pin the two halves of the contract -- find a scalable face if one
exists anywhere, and refuse loudly if none does.
"""
import io
import os
import shutil
import sys

import pytest
from PIL import ImageFont

from conftest import SCRIPTS_DIR

sys.path.insert(0, str(SCRIPTS_DIR))
mpv = pytest.importorskip("make_pitch_video")

ROLES = ["display", "display_b", "mono", "body"]
TITLE_SIZE = 150


@pytest.fixture(autouse=True)
def _clear_cache():
    mpv._FONT_CACHE.clear()
    mpv._WARNED.clear()
    yield
    mpv._FONT_CACHE.clear()
    mpv._WARNED.clear()


MACOS_TREE = "/System/Library/Fonts"


def _non_macos(monkeypatch):
    """Make the macOS font tree genuinely absent, not merely hidden.

    Patching os.path.exists alone is not enough, and getting this wrong made
    the suite lie: the pre-fix code reaches for a hardcoded
    /System/Library/Fonts/Helvetica.ttc without consulting exists() at all, so
    on a real Mac ImageFont.truetype opened the actual file and returned a
    properly sized face. The test passed against the defect.

    On a Linux box the file is not there to open, so truetype raises OSError.
    Both doors have to be shut for the simulation to mean anything.
    """
    real_exists = os.path.exists
    monkeypatch.setattr(
        mpv.os.path, "exists",
        lambda p: False if str(p).startswith(MACOS_TREE) else real_exists(p))

    real_truetype = ImageFont.truetype

    def truetype(path, *a, **kw):
        if str(path).startswith(MACOS_TREE):
            raise OSError(f"cannot open resource (simulated: no {MACOS_TREE})")
        return real_truetype(path, *a, **kw)

    monkeypatch.setattr(mpv.ImageFont, "truetype", truetype)


@pytest.fixture
def linux_box(tmp_path, monkeypatch):
    """A machine with fonts-dejavu-core installed and no /System/Library/Fonts.

    Standing up a real one matters. The first version of this test only hid the
    macOS tree, which on a stock Mac leaves no scalable font at all -- so it was
    exercising the give-up path while claiming to exercise fall-through, and it
    would have passed against a one-entry table that happened to raise.

    So: copy real font files to the paths a Debian box would have them at, keep
    each role's macOS candidate first in the list, and hide it. Finding the
    substitute then requires actually walking the list.
    """
    source = "/System/Library/Fonts/Supplemental/Georgia.ttf"
    if not os.path.exists(source):
        pytest.skip("no real font file on this machine to install into the fake tree")

    # Built from fixed names, NOT from FONT_CANDIDATES. Reading the Linux paths
    # out of the table under test made this fixture error out against the
    # pre-fix table instead of failing an assertion -- the fixture would have
    # hidden the very defect it exists to expose.
    installed = {}
    for role, basename in [("display", "DejaVuSerif.ttf"),
                           ("display_b", "DejaVuSerif-Bold.ttf"),
                           ("mono", "DejaVuSansMono.ttf"),
                           ("body", "DejaVuSans.ttf")]:
        dest = tmp_path / basename
        shutil.copyfile(source, dest)
        macos_first = mpv.FONT_CANDIDATES.get(role, [source])[0]
        installed[role] = [macos_first, str(dest)]    # macOS first, then "installed"

    monkeypatch.setattr(mpv, "FONT_CANDIDATES", installed)
    _non_macos(monkeypatch)
    return tmp_path


# ------------------------------------------------------- the size must survive

@pytest.mark.parametrize("role", ROLES)
def test_every_role_honours_the_requested_size(role):
    f = mpv.font(role, TITLE_SIZE)
    assert f.size == TITLE_SIZE, f"{role} came back at {f.size}px, not {TITLE_SIZE}px"


@pytest.mark.parametrize("role", ROLES)
def test_a_title_is_still_title_sized_without_the_macos_font_tree(role, linux_box):
    """The regression. Without the candidate lists this falls to load_default()."""
    f = mpv.font(role, TITLE_SIZE)

    width = f.getbbox("Molecular")[2]
    assert width > 300, (
        f"{role} at {TITLE_SIZE}px drew 'Molecular' {width}px wide. "
        "That is the bitmap default ignoring the size, not a 150px face.")


def test_the_default_face_is_never_what_gets_returned(linux_box):
    """load_default() must not be reachable from font() at all.

    Checking `f is not ImageFont.load_default()` does not work: load_default()
    hands back a fresh object every call, so the comparison is true no matter
    what font() returned. Nor does `getattr(f, "path", None)` -- the default
    face carries a path, but it is a BytesIO over a font Pillow ships inside
    the wheel, and it is pinned at size 10.

    Those two properties are what actually separate it from a real face.
    """
    default = ImageFont.load_default()
    assert isinstance(default.path, io.BytesIO) and default.size == 10, \
        "Pillow's default face changed shape; this test's premise needs rechecking"

    for role in ROLES:
        f = mpv.font(role, 64)
        assert isinstance(getattr(f, "path", None), str), \
            f"{role} is not backed by a font file on disk -- that is the bundled default"
        assert f.size == 64, f"{role} came back at {f.size}px: a fixed-size face"


# ------------------------------------------------------- failing loudly instead

def test_no_scalable_font_anywhere_stops_the_render(monkeypatch):
    """Silence is the bug. With nothing installed, say so and exit."""
    monkeypatch.setattr(mpv.os.path, "exists", lambda p: False)
    monkeypatch.setattr(mpv.ImageFont, "truetype",
                        lambda *a, **kw: (_ for _ in ()).throw(OSError("no fonts")))

    with pytest.raises(SystemExit) as e:
        mpv.font("display", TITLE_SIZE)

    msg = str(e.value)
    assert "150px" in msg                 # the size that would have been lost
    assert "1920x1080" in msg             # and the frame it would have been lost on
    assert "fonts-dejavu-core" in msg     # how to fix it


def test_a_substituted_role_is_announced(monkeypatch, capsys):
    """Serif-for-mono is acceptable; doing it without a word is not."""
    serif = [p for p in mpv.FONT_CANDIDATES["display"] if os.path.exists(p)]
    if not serif:
        pytest.skip("no serif candidate on this machine to substitute from")

    real = os.path.exists
    monkeypatch.setattr(
        mpv.os.path, "exists",
        lambda p: False if p in mpv.FONT_CANDIDATES["mono"] else real(p))

    f = mpv.font("mono", 40)
    assert f.size == 40
    assert "no mono font found" in capsys.readouterr().out


def test_the_candidate_lists_reach_past_macos():
    """A table of only /System paths is the defect; keep it impossible."""
    for role, paths in mpv.FONT_CANDIDATES.items():
        elsewhere = [p for p in paths if not p.startswith("/System/")]
        assert elsewhere, f"{role} has no non-macOS candidate"
        assert any("dejavu" in p.lower() or "liberation" in p.lower() for p in elsewhere), \
            f"{role} names no font from a standard Linux package"
