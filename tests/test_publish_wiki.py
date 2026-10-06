"""The wiki publisher must not ship a page that will render broken.

Two failure modes this guards, both of which produce a wiki that looks fine in
the repository and wrong on GitHub:

  A page embedding an image the publisher does not copy renders a broken-image
  icon. Worse than omitting the figure, because the page still claims one.

  GitHub serves a wiki's .svg as text/plain, so an <img> pointing at one shows
  nothing at all. The charts here are rasterised from their SVG sources for
  exactly that reason, and a page referencing the .svg would look correct in
  any local markdown preview and blank once published.
"""
import os
import shutil
import subprocess
import sys

import pytest

from conftest import REPO_ROOT

SCRIPT = os.path.join(REPO_ROOT, "scripts", "publish_wiki.py")
PY_BIN = os.path.join(REPO_ROOT, ".venv", "bin", "python")

sys.path.insert(0, os.path.join(REPO_ROOT, "scripts"))
import publish_wiki as pw  # noqa: E402


PAGE = "# Title\n\n" + ("Body text that is long enough to be a real page. " * 12) + "\n"


@pytest.fixture
def wiki(tmp_path, monkeypatch):
    src = tmp_path / "wiki"
    media = tmp_path / "media"
    src.mkdir()
    media.mkdir()
    monkeypatch.setattr(pw, "WIKI_SRC", str(src))
    monkeypatch.setattr(pw, "MEDIA_SRC", str(media))
    (src / "Home.md").write_text(PAGE)
    return src, media


def dry_run(cwd=REPO_ROOT, env=None):
    return subprocess.run([PY_BIN, SCRIPT, "--dry-run"], cwd=cwd, env=env,
                          capture_output=True, text=True)


# ------------------------------------------------------------ what gets shipped

def test_only_images_the_pages_reference_are_shipped(wiki):
    src, media = wiki
    (src / "Home.md").write_text(PAGE + "\n![a chart](used.png)\n")
    (media / "used.png").write_bytes(b"\x89PNG")
    (media / "never-referenced.png").write_bytes(b"\x89PNG")

    assert pw.media_referenced(["Home.md"]) == ["used.png"]


def test_an_image_hosted_elsewhere_is_not_treated_as_ours(wiki):
    """A GitHub blob URL is a link, not a file this publisher owns."""
    src, _ = wiki
    (src / "Home.md").write_text(
        PAGE + "\n![poster](https://github.com/o/r/blob/main/docs/media/frame.jpg)\n")

    assert pw.media_referenced(["Home.md"]) == []


def test_a_page_may_reference_the_same_image_twice(wiki):
    src, media = wiki
    (src / "Home.md").write_text(PAGE + "\n![one](c.png)\n\n![again](c.png)\n")
    (media / "c.png").write_bytes(b"\x89PNG")

    assert pw.media_referenced(["Home.md"]) == ["c.png"]


# ------------------------------------------------------------------- the guards

def test_a_missing_image_stops_the_publish(wiki, monkeypatch):
    src, _ = wiki
    (src / "Home.md").write_text(PAGE + "\n![gone](absent.png)\n")
    monkeypatch.setattr(sys, "argv", ["publish_wiki.py", "--dry-run"])

    with pytest.raises(SystemExit) as e:
        pw.main()
    assert "absent.png" in str(e.value)


def test_an_svg_reference_stops_the_publish(wiki, monkeypatch):
    """The one that would have looked right locally and been blank on GitHub."""
    src, media = wiki
    (src / "Home.md").write_text(PAGE + "\n![chart](chart.svg)\n")
    (media / "chart.svg").write_text("<svg/>")
    monkeypatch.setattr(sys, "argv", ["publish_wiki.py", "--dry-run"])

    with pytest.raises(SystemExit) as e:
        pw.main()
    assert "chart.svg" in str(e.value) and "rasterise" in str(e.value)


# ------------------------------------------------------------- the real content

def test_the_real_wiki_ships_every_image_its_pages_embed():
    """Against docs/wiki as it stands, not a fixture."""
    r = dry_run()
    assert r.returncode == 0, f"the real wiki does not pass its own publish checks:\n{r.stdout}{r.stderr}"
    assert "[image]" in r.stdout, "no images are being shipped; the figures would 404"


def test_the_published_charts_are_rasters_not_svg():
    media = os.path.join(REPO_ROOT, "docs", "media")
    for name in ("chart-redock", "chart-ceiling", "graph-provenance"):
        png = os.path.join(media, f"{name}.png")
        assert os.path.exists(png), f"{name}.png is missing; the wiki embeds it"
        with open(png, "rb") as fh:
            assert fh.read(8) == b"\x89PNG\r\n\x1a\n", f"{name}.png is not a PNG"


def test_readme_is_never_published_as_a_page():
    """It is instructions for maintainers and would read as a wiki page."""
    assert "README.md" in pw.NOT_A_PAGE
    r = dry_run()
    assert "<- docs/wiki/README.md" not in r.stdout
