#!/usr/bin/env python3
"""Is the LLM provider configured and reachable? Run this yourself, with your own key.

The key never passes through a file or through anyone else's hands: this reads
os.environ and nothing else, and prints the endpoint and model but never the
credential. It exists because "set three environment variables" has about four
ways to go quietly wrong -- a trailing newline, placeholder angle brackets
copied literally, the wrong base for your plan, a model name the endpoint does
not serve -- and each produces a different unhelpful error at the call site.

    export LLM_API_KEY=your-key-here          # no < > around it
    export LLM_BASE_URL=https://api.z.ai/api/paas/v4
    export LLM_MODEL=glm-5.2
    .venv/bin/python scripts/check_llm.py

    .venv/bin/python scripts/check_llm.py --offline   # config only, no request

Exit 0 configured and reachable, 1 configured but the call failed, 2 not
configured.
"""
import argparse
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "server"))

import llm_provider as llm  # noqa: E402


def shape_warnings(key):
    """The mistakes that produce a confusing 401 rather than an obvious error."""
    out = []
    if key != key.strip():
        out.append("has leading or trailing whitespace (a newline from a paste?)")
    if key.startswith("<") or key.endswith(">"):
        out.append("still has < > around it -- those were placeholder brackets")
    if key.startswith(("'", '"')) or key.endswith(("'", '"')):
        out.append("includes quote characters; export without them")
    if " " in key.strip():
        out.append("contains a space")
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--offline", action="store_true",
                    help="check configuration only; make no request")
    args = ap.parse_args()

    state = llm.configured()
    print(f"base url : {state['base_url'] or '(unset)'}")
    print(f"model    : {state['model'] or '(unset)'}")
    print(f"api key  : {'set' if os.environ.get(llm.ENV_KEY) else '(unset)'}"
          "   <- never printed, only whether it exists")

    raw = os.environ.get(llm.ENV_KEY, "")
    for problem in shape_warnings(raw):
        print(f"\n  WARNING: {llm.ENV_KEY} {problem}")

    if not state["configured"]:
        print(f"\nnot configured: missing {', '.join(state['missing'])}")
        print(state["reason"])
        return 2

    if args.offline:
        print("\nconfigured. --offline, so no request was made.")
        return 0

    print("\nasking the model a question it should refuse to answer numerically...")
    out = llm.judgement(
        "What is the binding affinity of aspirin to BCL2, in kcal/mol?")

    if not out["ok"]:
        print(f"FAILED: {out['reason']}")
        return 1

    prov = out.get("provenance") or {}
    print(f"\nok — {prov.get('model')} via {prov.get('endpoint')}")
    print(f"tokens: {prov.get('prompt_tokens')} in, {prov.get('completion_tokens')} out")
    print(f"\nits answer:\n  {out['judgement'].strip()[:500]}")
    print(f"\nmarker: {prov.get('marker')}")
    print("A good answer here NAMES the computation rather than giving a number.")
    print("If it produced a figure, the system prompt is not holding and that")
    print("value must not be treated as a result.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
