"""Provenance marking for synthetic (placeholder) scientific values.

Stub pipelines emit numbers that no engine computed. Anything leaving a stub
must announce that at every exit: the value's own str/repr/format, the record
it sits in, and a one-time runtime warning. Real integrations set
``provenance`` explicitly; the default is always "synthetic".
"""

import warnings

MARKER = "SYNTHETIC"
_VALUE_SUFFIX = f" [{MARKER}]"
_warned = False


class SyntheticResultWarning(UserWarning):
    """Raised once per process the first time a synthetic value is created."""


def _warn_once():
    global _warned
    if _warned:
        return
    _warned = True
    warnings.warn(
        "Synthetic placeholder values are being generated: no docking, MD, ADMET "
        "or assay model has run. Every such number prints with '[SYNTHETIC]' and "
        "every record carries a 'provenance' field. Do not report them as results.",
        SyntheticResultWarning, stacklevel=4,
    )


class SyntheticValue(float):
    """A number with no measurement or model behind it.

    Behaves as a float for arithmetic and comparison; arithmetic results stay
    SyntheticValue. Every textual form carries the marker. Only ``float(x)``
    and ``json.dumps`` of a bare value strip it, which is why records also
    carry ``provenance``.
    """
    __slots__ = ()

    def __new__(cls, value):
        _warn_once()
        return float.__new__(cls, value)

    def __repr__(self):
        return f"<{MARKER} {float.__repr__(self)}>"

    def __str__(self):
        return float.__repr__(self) + _VALUE_SUFFIX

    def __format__(self, spec):
        # Convert to a plain float first: an empty spec otherwise routes back
        # through this class's __str__, which has already added the suffix.
        return format(float(self), spec) + _VALUE_SUFFIX

    def __reduce__(self):
        return (SyntheticValue, (float(self),))


def _propagating(name):
    op = getattr(float, name)

    def method(self, *args):
        out = op(self, *args)
        return SyntheticValue(out) if type(out) is float else out
    method.__name__ = name
    return method


for _name in ("__add__", "__radd__", "__sub__", "__rsub__", "__mul__", "__rmul__",
              "__truediv__", "__rtruediv__", "__floordiv__", "__rfloordiv__",
              "__mod__", "__rmod__", "__pow__", "__rpow__", "__neg__", "__pos__",
              "__abs__", "__round__"):
    setattr(SyntheticValue, _name, _propagating(_name))


def synthetic_label(text) -> str:
    """Mark a categorical/string output as synthetic; survives JSON."""
    text = str(text)
    return text if text.endswith(_VALUE_SUFFIX) else text + _VALUE_SUFFIX


def is_synthetic(*values) -> bool:
    """True if any value (recursing into dicts/lists/tuples) is synthetic."""
    for v in values:
        if isinstance(v, SyntheticValue):
            return True
        if isinstance(v, str) and MARKER in v:
            return True
        if isinstance(v, dict) and is_synthetic(*v.values()):
            return True
        if isinstance(v, (list, tuple)) and is_synthetic(*v):
            return True
    return False


def derive(value, *inputs):
    """Tag `value` as synthetic when any input is. Use after clamps (max/min
    return the bound, dropping the taint) and after math.* calls."""
    if not is_synthetic(*inputs):
        return value
    if isinstance(value, bool) or value is None:
        return value
    if isinstance(value, (int, float)):
        return SyntheticValue(value)
    if isinstance(value, str):
        return synthetic_label(value)
    return value


def provenance(note: str, *fields) -> str:
    """Record-level provenance string; always starts with the marker."""
    text = f"{MARKER}: {note}"
    if fields:
        text += f" Placeholder fields: {', '.join(sorted(set(fields)))}."
    return text


def stamp(record: dict, note: str, *extra_fields) -> dict:
    """Add a 'provenance' entry naming every synthetic field in `record`."""
    found = {k for k, v in record.items() if k != "provenance" and is_synthetic(v)}
    record["provenance"] = provenance(note, *found, *extra_fields)
    return record


def json_default(obj):
    """Fallback encoder for types json cannot serialize.

    WARNING -- this does NOT catch SyntheticValue, and cannot. `default=` is
    only consulted for objects the encoder does not already understand, and
    SyntheticValue subclasses float, so json serializes it natively as a bare
    number and this function is never called for one. It is kept for genuinely
    unserializable types.

    Use `json_ready()` below before dumping anything that may hold synthetic
    values. That is the only reliable way to keep the marker through JSON.
    """
    if isinstance(obj, SyntheticValue):     # unreachable via default=; see above
        return str(obj)
    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def json_ready(obj):
    """Recursively replace synthetic values with their marked string form.

    The reliable counterpart to json_default. json.dumps will happily write a
    SyntheticValue as `-9.4`, losing the one thing that distinguished it from a
    measurement, and no `default=` hook can intercept that because the value is
    already a float as far as the encoder is concerned. So the substitution has
    to happen before the encoder ever sees it.

    Non-synthetic input is returned structurally unchanged, which matters for
    content addressing: hashes of real data must not move because this exists.
    """
    if isinstance(obj, SyntheticValue):
        return str(obj)
    if isinstance(obj, dict):
        return {k: json_ready(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [json_ready(v) for v in obj]
    if isinstance(obj, tuple):
        return tuple(json_ready(v) for v in obj)
    return obj


def dumps(obj, **kw):
    """json.dumps that keeps the SYNTHETIC marker. Use instead of json.dumps."""
    import json as _json
    kw.setdefault("default", json_default)
    return _json.dumps(json_ready(obj), **kw)
