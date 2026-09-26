"""The asset catalogue must not break the session it is trying to improve.

js/assets.js opens ~2,400 Poly Haven assets to a browser that previously had
five hardcoded presets. Two things can go wrong, and neither is a crash:

  It pulls something enormous. An 8k texture is a 37 MB JPEG and its PNG is
  131 MB. Handed to a headset on conference wifi that is not a slow load, it is
  a dropped session. Size is therefore reported before any fetch, 1k is the
  default, and anything over the limit must be asked for explicitly.

  It disappears. The catalogue is someone else's API. When it is down the
  workspace must keep working on its built-in presets rather than presenting an
  empty picker, which reads to a user as "this feature is broken".

Driven through a node harness with fetch stubbed, so it runs offline and does
not depend on Poly Haven being up to pass. The live API is exercised separately
by evals/asset_catalogue.mjs, which is an eval precisely because it can fail for
reasons that are nobody's fault.
"""
import json
import pathlib
import shutil
import subprocess

import pytest

from conftest import REPO_ROOT

HARNESS = pathlib.Path(__file__).parent / "fixtures" / "assets_harness.mjs"


@pytest.fixture(scope="module")
def result():
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed; cannot exercise the JS catalogue")
    proc = subprocess.run([node, str(HARNESS)], capture_output=True, text=True,
                          cwd=str(REPO_ROOT), timeout=60)
    assert proc.returncode == 0, f"harness failed:\n{proc.stderr}"
    return json.loads(proc.stdout)


# --------------------------------------------------------------------------- browsing

def test_the_catalogue_parses_into_records(result):
    assert result["catalogue_ok"] is True
    assert result["count"] == 3
    assert "Venice Sunset" in result["names"]


def test_search_matches_tags_not_just_names(result):
    """A user types 'laboratory'; Poly Haven files it under tags, not the name."""
    assert result["by_text_lab"] == ["lab_bench_02"]


def test_search_matches_names(result):
    assert result["by_text_name"] == ["venice_sunset"]


def test_search_filters_by_category(result):
    assert set(result["by_category"]) == {"studio_small_09", "lab_bench_02"}


def test_text_and_category_combine(result):
    """Both filters must apply, not whichever one is checked last.

    The category alone matches two environments; adding the text narrows it to
    one. Asserted this way round so the test cannot pass with one filter being
    silently a no-op.
    """
    assert len(result["by_category_only"]) == 2
    assert result["by_both"] == ["lab_bench_02"]


def test_a_search_with_no_matches_returns_nothing_rather_than_everything(result):
    """The failure that looks like success: an empty filter silently ignored."""
    assert result["no_match"] == 0


def test_limit_is_respected(result):
    assert result["limited"] == 2


def test_categories_are_counted_for_a_filter_ui(result):
    counts = {c["name"]: c["count"] for c in result["categories"]}
    assert counts.get("indoor") == 2 or counts.get("studio") == 2


def test_authors_are_credited_even_though_cc0_does_not_require_it(result):
    assert "Greg Zaal" in result["credit"]
    assert "CC0" in result["credit"]


# --------------------------------------------------------------------------- the size gate

def test_a_small_asset_resolves(result):
    small = result["small"]
    assert small["ok"] is True
    assert small["url"].endswith("_1k.hdr")
    assert small["bytes"] == 1440400


def test_a_large_asset_is_not_fetched_silently(result):
    """22 MB must be a decision, not a surprise."""
    blocked = result["large_blocked"]
    assert blocked["ok"] is False
    assert blocked["tooLarge"] is True
    assert "MB" in blocked["reason"]
    # The URL is still reported, so the caller can choose to proceed.
    assert blocked["url"]


def test_a_large_asset_can_be_requested_deliberately(result):
    """The gate is a speed bump, not a wall: the user may know what they want."""
    allowed = result["large_allowed"]
    assert allowed["ok"] is True
    assert allowed["bytes"] == 22000000


def test_an_8k_texture_is_blocked_by_default(result):
    """37 MB into a headset is a dropped session, not a slow load."""
    blocked = result["texture_8k_blocked"]
    assert blocked["ok"] is False
    assert blocked["tooLarge"] is True


def test_the_default_resolution_is_browser_sane(result):
    assert result["default_resolution"] == "1k"


def test_a_missing_asset_reports_a_reason_rather_than_a_dead_url(result):
    missing = result["missing"]
    assert missing["ok"] is False
    assert missing["url"] is None
    assert missing["reason"]
    assert missing["tooLarge"] is False      # absent, not oversized


def test_sizes_are_rendered_for_humans(result):
    assert result["bytes"] == ["unknown size", "879 KB", "35.8 MB"]


# --------------------------------------------------------------------------- absence

def test_the_catalogue_being_down_is_not_an_exception(result):
    """An empty picker reads as 'broken feature'; this must say what happened."""
    offline = result["offline"]
    assert offline["ok"] is False
    assert offline["assets"] == []
    assert "network problem, not a missing feature" in offline["error"]
