"""An OpenAI-compatible LLM client, configured entirely from the environment.

This repository had no LLM client at all before this file. Its "agents" are
rule-based Python -- OptimizerModule picks a box size from a lookup, and
predict_synthesis_difficulty returns random.uniform(2.0, 8.0). Adding this does
not redirect existing model calls, because there were none. It gives those
modules the ability to ask a model, for the first time.

WHY THE KEY IS ONLY EVER AN ENVIRONMENT VARIABLE. There is no config file, no
constructor argument, and no way to pass a key as a string. A key written to a
file gets committed eventually -- this repository is public, and the .env entry
in .gitignore was added after the first push, not before. Reading os.environ is
the one path where the credential never exists as repository state. If
LLM_API_KEY is unset, every call reports itself unavailable and names the
variable, exactly as compound_sourcing does for Mcule.

A MODEL'S ANSWER IS NOT A MEASUREMENT, AND NOT A PLACEHOLDER EITHER. This repo
already separates computed values from SyntheticValue placeholders. A model
judgment is a third thing: it was produced by something, but that something was
a language model reasoning about text, not a docking run. Every response
carries provenance naming the model and endpoint, and judgement() returns a
value tagged so it can never be mistaken for either of the other two. An LLM
guessing a binding affinity is worth strictly less than a placeholder, because
a placeholder announces itself.

    export LLM_API_KEY=...                      # required; never written down
    export LLM_BASE_URL=https://api.z.ai/api/paas/v4   # default is unset
    export LLM_MODEL=glm-5.2

Known OpenAI-compatible bases (the API shape here is theirs, not ours):
    Z.ai general      https://api.z.ai/api/paas/v4
    Z.ai coding plan  https://api.z.ai/api/coding/paas/v4
    OpenAI            https://api.openai.com/v1
"""
import json
import os
import re
import urllib.error
import urllib.request

SCHEMA_VERSION = "1.0"

ENV_KEY = "LLM_API_KEY"
ENV_BASE = "LLM_BASE_URL"
ENV_MODEL = "LLM_MODEL"

DEFAULT_TIMEOUT = 60

#: Marker for a value a language model asserted. Deliberately distinct from
#: synthetic_provenance's SYNTHETIC: that marks "no model ran"; this marks "a
#: model ran, but it was a language model, not physics".
JUDGEMENT_MARKER = "MODEL-JUDGEMENT"

NOT_CONFIGURED = (
    f"No LLM is configured. Set {ENV_KEY} and {ENV_BASE} to enable model calls. "
    "Nothing in this repository requires one: the agent modules fall back to their "
    "rule-based behaviour, which is what they have always done.")

JUDGEMENT_CAVEAT = (
    "A language model produced this. It is not a measurement, not a simulation result, "
    "and not a placeholder -- it is an opinion expressed in text. Do not report it as a "
    "computed value, and do not let it stand in for a docking, MD or assay result.")


def _redact(text):
    """Strip anything key-shaped from a string before it reaches a log or a caller.

    Error bodies quote request headers more often than anyone expects, and this
    is the only place a key could escape into output.
    """
    key = os.environ.get(ENV_KEY)
    out = str(text)
    if key and len(key) > 6:
        out = out.replace(key, "<redacted>")
    # Belt and braces: anything that looks like a long opaque token.
    return re.sub(r"\b[A-Za-z0-9_\-]{24,}\.[A-Za-z0-9_\-]{8,}\b", "<redacted>", out)


def configured():
    """Is a provider set up? Reports what is missing rather than a bare False."""
    key, base = os.environ.get(ENV_KEY), os.environ.get(ENV_BASE)
    missing = [name for name, value in ((ENV_KEY, key), (ENV_BASE, base)) if not value]
    return {
        "configured": not missing,
        "missing": missing,
        "base_url": base,                       # never the key, at any verbosity
        "model": os.environ.get(ENV_MODEL),
        "reason": None if not missing else NOT_CONFIGURED,
    }


def _result(ok, reason=None, **extra):
    return {"schema_version": SCHEMA_VERSION, "ok": ok, "reason": reason,
            "caveat": JUDGEMENT_CAVEAT, **extra}


def complete(messages, model=None, temperature=0.2, max_tokens=1024,
             timeout=DEFAULT_TIMEOUT):
    """One chat completion. Returns a result dict; never raises, never logs the key.

    `messages` is the OpenAI shape: [{"role": "user", "content": "..."}].
    """
    state = configured()
    if not state["configured"]:
        return _result(False, NOT_CONFIGURED, missing=state["missing"])

    model = model or os.environ.get(ENV_MODEL)
    if not model:
        return _result(False, f"No model selected. Set {ENV_MODEL}.")

    base = state["base_url"].rstrip("/")
    body = json.dumps({"model": model, "messages": messages,
                       "temperature": temperature,
                       "max_tokens": max_tokens}).encode()
    req = urllib.request.Request(
        f"{base}/chat/completions", data=body, method="POST",
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {os.environ[ENV_KEY]}",
                 "User-Agent": "agi-bioxr/1.0"})

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read().decode())
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = _redact(exc.read().decode()[:400])
        except Exception:                        # noqa: BLE001 - body may be gone
            pass
        return _result(False, f"HTTP {exc.code} from the provider. {detail}".strip())
    except (urllib.error.URLError, TimeoutError, ValueError, OSError) as exc:
        return _result(False, _redact(f"{type(exc).__name__}: {exc}"))

    try:
        text = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError):
        return _result(False, "Provider returned no choices in the expected shape.",
                       raw_keys=sorted(payload) if isinstance(payload, dict) else None)

    usage = payload.get("usage") or {}
    return _result(
        True, None, text=text,
        provenance={
            "marker": JUDGEMENT_MARKER,
            "model": payload.get("model") or model,
            "endpoint": base,                    # where it came from, never the key
            "prompt_tokens": usage.get("prompt_tokens"),
            "completion_tokens": usage.get("completion_tokens"),
        })


def judgement(question, context="", model=None, **kw):
    """Ask a model a question and return an answer that is labelled as an opinion.

    The system prompt is not decoration. These modules sit beside docking and MD
    code whose outputs are numbers, and the failure this repository is built to
    prevent is a number with nothing behind it. A model told to "estimate the
    binding affinity" will happily produce -8.4 kcal/mol, and that value is
    worth less than a placeholder because a placeholder announces itself.
    """
    system = (
        "You are assisting inside a molecular research workspace. Answer in prose and "
        "reasoning only. Do NOT invent numeric results that would normally come from a "
        "docking run, a molecular dynamics simulation, an ADMET model or an assay -- if "
        "asked for one, say which computation would produce it instead. If you do not "
        "know something, say so; a recorded gap is more useful here than a plausible "
        "guess.")
    messages = [{"role": "system", "content": system}]
    if context:
        messages.append({"role": "user", "content": f"Context:\n{context}"})
    messages.append({"role": "user", "content": question})

    out = complete(messages, model=model, **kw)
    if out["ok"]:
        out["judgement"] = out["text"]
        out["is_measurement"] = False            # stated, not left to be inferred
    return out
