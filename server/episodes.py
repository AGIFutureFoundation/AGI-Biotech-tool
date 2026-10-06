"""Turn a shared XR session into robot training data, if everyone agreed.

A person reaching into a headset, grasping a molecule, moving it into a pocket
and letting go is a demonstration: head pose, two hand poses, an object's
trajectory, and a clear grasp/release boundary. That is the shape of data used
to train manipulation policies, and this workspace already produces it -- the
grab arbitration in server.py marks exactly when a hold starts and ends, which
is the segmentation that hand-tracking data usually lacks.

CONSENT IS THE WHOLE DESIGN, NOT A SETTING.

Hand and gaze traces are biometric. Gaze reveals attention and hesitation; hand
kinematics are individuating enough to be re-identifying. Exporting them to
train a model is a different act from showing them to a colleague in the room,
and someone who joined a lab session agreed to the second, not the first.

So: consent defaults to NONE, is per person and per purpose, must be given
before the frames it covers, and is revocable retroactively. An episode exports
only if every actor in it consented at the requested scope; otherwise the
non-consenting actors are dropped and the export SAYS they were dropped, or --
when dropping would leave a misleading fragment -- the whole episode is refused.

An export that quietly omits someone is worse than one that refuses, because
downstream it looks complete. Every manifest therefore carries who consented,
who was excluded, and what was actually removed.

Format: a per-episode directory with a metadata file, which is one of the two
common layouts for LeRobot-style datasets and the one that stays inspectable.
No pandas or pyarrow is required; convert to parquet downstream if a trainer
wants it, using the schema recorded in the manifest.
"""
import datetime as _dt
import json
import os

SCHEMA_VERSION = "1.0"
FORMAT = "lerobot-style/per-episode-dir"

#: Consent scopes, weakest first. Each includes everything to its left.
#: Explicit rather than a boolean, because "you may record this session" and
#: "you may train a commercial model on my hand movements" are not the same
#: permission and collapsing them is how consent becomes meaningless.
SCOPES = ("none", "session_only", "research", "model_training", "redistribution")

SCOPE_MEANING = {
    "none": "No recording may be kept after the session ends.",
    "session_only": "May be replayed by participants. Not used to train anything.",
    "research": "May be analysed and published in aggregate. Not used to train a model.",
    "model_training": "May be used to train models, including robot policies.",
    "redistribution": "May be shared or published as a dataset others can use.",
}

CONSENT_DEFAULT = "none"

BIOMETRIC_NOTICE = (
    "This episode contains head and hand kinematics. Gaze direction reveals attention "
    "and hesitation, and hand motion is individuating enough to be re-identifying. Treat "
    "it as personal data even after the names are removed: pseudonymisation is not "
    "anonymisation for motion traces.")


def _now():
    return _dt.datetime.now(_dt.timezone.utc)


def scope_allows(granted, required):
    """Does `granted` cover `required`? Unknown scopes never allow anything."""
    if granted not in SCOPES or required not in SCOPES:
        return False
    return SCOPES.index(granted) >= SCOPES.index(required)


class ConsentLedger:
    """Who agreed to what, and when. Time-aware on purpose.

    Consent given at 14:05 does not cover what happened at 14:00. People agree
    to recording once they know what it will contain, and treating a later yes
    as retroactive is how "they consented" stops meaning anything.
    """

    def __init__(self):
        self._grants = {}      # client -> list of {scope, at, until, revoked_at}

    def grant(self, client, scope, at=None, display_name=None):
        if scope not in SCOPES:
            raise ValueError(f"unknown consent scope {scope!r}; expected one of {SCOPES}")
        record = {"client": client, "name": display_name, "scope": scope,
                  "at": (at or _now()), "revoked_at": None}
        self._grants.setdefault(client, []).append(record)
        return record

    def revoke(self, client, at=None):
        """Withdraw consent. Applies to everything, including past frames.

        Revocation has to reach data already collected, or it is not a right --
        it is a preference about future collection.
        """
        at = at or _now()
        count = 0
        for record in self._grants.get(client, []):
            if record["revoked_at"] is None:
                record["revoked_at"] = at
                count += 1
        return count

    def scope_at(self, client, when):
        """The strongest scope in force for `client` at `when`."""
        best = CONSENT_DEFAULT
        for record in self._grants.get(client, []):
            if record["at"] > when:
                continue                       # granted after the fact
            if record["revoked_at"] is not None:
                continue                       # revoked: applies retroactively
            if SCOPES.index(record["scope"]) > SCOPES.index(best):
                best = record["scope"]
        return best

    def name_of(self, client):
        for record in self._grants.get(client, []):
            if record.get("name"):
                return record["name"]
        return None


class Episode:
    """One recorded demonstration: frames, actors, objects and grasp events."""

    def __init__(self, episode_id, room, instruction="", started_at=None):
        self.episode_id = episode_id
        self.room = room
        self.instruction = instruction       # natural-language task, as LeRobot expects
        self.started_at = started_at or _now()
        self.frames = []
        self.events = []

    def add_frame(self, t, actors, objects):
        """One timestep. `actors` maps client -> {head, hands}; `objects` -> pose."""
        self.frames.append({"t": t, "actors": dict(actors), "objects": dict(objects)})

    def add_event(self, t, kind, client, obj, detail=None):
        """A grasp boundary. This is the segmentation that makes the data usable."""
        self.events.append({"t": t, "kind": kind, "client": client,
                            "object": obj, "detail": detail})

    @property
    def actors(self):
        seen = set()
        for frame in self.frames:
            seen.update(frame["actors"])
        for event in self.events:
            if event["client"]:
                seen.add(event["client"])
        return seen

    def duration(self):
        return (self.frames[-1]["t"] - self.frames[0]["t"]) if len(self.frames) > 1 else 0.0


def prepare_export(episode, ledger, purpose="model_training", min_frames=10):
    """Decide what of this episode may leave, and say so explicitly.

    Returns a dict with `allowed`, the filtered episode data, and a manifest
    naming every actor who was excluded and why. Never silently drops anyone.
    """
    if purpose not in SCOPES:
        raise ValueError(f"unknown purpose {purpose!r}")

    consenting, excluded = {}, {}
    for client in sorted(episode.actors):
        granted = ledger.scope_at(client, episode.started_at)
        if scope_allows(granted, purpose):
            consenting[client] = granted
        else:
            excluded[client] = granted

    if not consenting:
        return _refused(episode, purpose, excluded,
                        "No participant consented to this purpose. Nothing may be exported.")

    frames, dropped_frames = [], 0
    for frame in episode.frames:
        kept = {c: pose for c, pose in frame["actors"].items() if c in consenting}
        if not kept:
            dropped_frames += 1
            continue
        frames.append({"t": frame["t"], "actors": kept, "objects": frame["objects"]})

    events = [e for e in episode.events if e["client"] in consenting or e["client"] is None]

    # A demonstration where the person doing the manipulating was removed is not
    # a shorter demonstration -- it is an object moving by itself, which teaches
    # a policy something false. Refuse rather than ship a misleading fragment.
    if excluded and _manipulation_lost(episode, events):
        return _refused(
            episode, purpose, excluded,
            "Excluding non-consenting participants removes the manipulation itself. "
            "The remainder would show objects moving with no actor responsible for them, "
            "which is not a shorter demonstration -- it is a false one.")

    if len(frames) < min_frames:
        return _refused(episode, purpose, excluded,
                        f"Only {len(frames)} frames survive consent filtering; "
                        f"{min_frames} is the minimum for a usable demonstration.")

    return {
        "schema_version": SCHEMA_VERSION,
        "allowed": True,
        "refused_reason": None,
        "episode_id": episode.episode_id,
        "format": FORMAT,
        "purpose": purpose,
        "purpose_meaning": SCOPE_MEANING[purpose],
        "instruction": episode.instruction,
        "frames": frames,
        "events": events,
        "consent": {
            "consented": [{"client": c, "scope": s, "name": ledger.name_of(c)}
                          for c, s in sorted(consenting.items())],
            "excluded": [{"client": c, "scope": s, "name": ledger.name_of(c)}
                         for c, s in sorted(excluded.items())],
            "frames_dropped_entirely": dropped_frames,
            "notice": BIOMETRIC_NOTICE,
        },
        "caveats": _caveats(excluded, dropped_frames),
    }


def _manipulation_lost(episode, kept_events):
    """Did filtering remove every grasp, while objects still move?"""
    had_grasp = any(e["kind"] in ("grab", "release") for e in episode.events)
    keeps_grasp = any(e["kind"] in ("grab", "release") for e in kept_events)
    return had_grasp and not keeps_grasp


def _refused(episode, purpose, excluded, reason):
    return {
        "schema_version": SCHEMA_VERSION,
        "allowed": False,
        "refused_reason": reason,
        "episode_id": episode.episode_id,
        "purpose": purpose,
        "frames": [],
        "events": [],
        "consent": {"consented": [], "excluded": [{"client": c, "scope": s}
                                                  for c, s in sorted(excluded.items())],
                    "notice": BIOMETRIC_NOTICE},
        "caveats": [reason],
    }


def _caveats(excluded, dropped_frames):
    out = []
    if excluded:
        out.append(
            f"{len(excluded)} participant(s) did not consent to this purpose and their "
            "tracks were removed. This episode is NOT a complete record of the session; "
            "do not treat gaps as inactivity.")
    if dropped_frames:
        out.append(
            f"{dropped_frames} frame(s) contained only non-consenting participants and "
            "were dropped entirely, so the timeline has holes. Timestamps are preserved, "
            "so resample rather than assuming a fixed rate.")
    return out


def write_episode(export, out_dir):
    """Write a prepared export as a per-episode directory. Refuses if not allowed.

    The consent manifest is written first and as its own file, so a dataset
    cannot be copied around without the terms it was collected under.
    """
    if not export.get("allowed"):
        raise PermissionError(
            f"episode {export.get('episode_id')} may not be exported: {export['refused_reason']}")

    path = os.path.join(out_dir, f"episode_{export['episode_id']}")
    os.makedirs(path, exist_ok=True)

    with open(os.path.join(path, "consent.json"), "w", encoding="utf-8") as fh:
        json.dump(export["consent"], fh, indent=2)

    meta = {k: v for k, v in export.items() if k not in ("frames", "events")}
    meta["frame_count"] = len(export["frames"])
    meta["schema"] = {
        "frame": "t (seconds from episode start), actors{client:{head:{p,q},hands:[p,p]}}, "
                 "objects{id:{p,q,held_by}}",
        "event": "t, kind (grab|release|load), client, object, detail",
        "note": "Convert to parquet/HDF5 downstream if a trainer needs it; this layout "
                "stays inspectable, which matters more while the data is being checked.",
    }
    with open(os.path.join(path, "meta.json"), "w", encoding="utf-8") as fh:
        json.dump(meta, fh, indent=2)

    with open(os.path.join(path, "frames.jsonl"), "w", encoding="utf-8") as fh:
        for frame in export["frames"]:
            fh.write(json.dumps(frame, separators=(",", ":")) + "\n")

    with open(os.path.join(path, "events.jsonl"), "w", encoding="utf-8") as fh:
        for event in export["events"]:
            fh.write(json.dumps(event, separators=(",", ":")) + "\n")

    return {"path": path, "frames": len(export["frames"]), "events": len(export["events"])}
