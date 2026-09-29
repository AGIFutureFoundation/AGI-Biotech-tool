#!/usr/bin/env python3
"""Anchor a research run on Monad, or check an anchor that already exists.

Takes a results file, stores it content-addressed, screens it for placeholder
values, and prints the unsigned transaction that would anchor its Merkle root.
It stops there on purpose: no key is read, no wallet is touched, nothing is
broadcast. You sign it yourself, or you do not.

    .venv/bin/python scripts/anchor_run.py results.json --label bcl2-run-1
    .venv/bin/python scripts/anchor_run.py results.json --registry 0xABC... --from 0xDEF...
    .venv/bin/python scripts/anchor_run.py --verify 0xTXHASH --root 0xROOT

The screening step is the reason this is a script and not a one-liner. A run
whose numbers came from the synthetic placeholder engines is REFUSED, and no
transaction is built at all. Anchoring is permanent and reads as authority;
"verified on-chain" attached to a placeholder is worse than no anchor, because
it is a claim that cannot be withdrawn. Pass --allow-synthetic to override, and
the override is recorded on the payload so it travels with the record.

Exit status: 0 anchor payload built (or verified), 1 refused, 2 bad input,
3 verification failed. A run that could not reach the network exits 3 as well,
because an unchecked anchor is not a checked one.
"""
import argparse
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "server"))

import chain_anchor as ca          # noqa: E402
import content_store               # noqa: E402

BAR = "-" * 72


def _load(path):
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        sys.exit(f"no such file: {path}")
    except ValueError as exc:
        sys.exit(f"{path} is not valid JSON: {exc}")


def _print_payload(payload, verbose=False):
    print(BAR)
    print(f"  merkle root : {payload['merkle_root']}")

    if payload.get("refused"):
        print(f"  status      : REFUSED")
        print(BAR)
        print()
        print(payload["reason"])
        print()
        print("Nothing was built. Re-run with --allow-synthetic only if you have")
        print("read the above and still want this on a public chain permanently.")
        return

    net = payload["network"]
    tx = payload["unsigned_transaction"]
    print(f"  network     : {net['name']} (chain id {net['chain_id']})")
    print(f"  mode        : {payload['mode']}")
    print(f"  status      : {ca.anchor_status(payload)}")
    print(BAR)

    print("\nUNSIGNED TRANSACTION\n")
    print(json.dumps(tx, indent=2))

    if payload.get("caveats"):
        print("\nCAVEATS\n")
        for caveat in payload["caveats"]:
            print(f"  * {caveat}")

    print("\nWHAT AN ANCHOR PROVES\n")
    print(f"  {payload['anchor_meaning']}")

    print("\nNEXT\n")
    for i, step in enumerate(payload["next_steps"], 1):
        print(f"  {i}. {step}")

    print(f"\n{payload['boundary']}\n")


def cmd_anchor(args):
    data = _load(args.results)
    entries = data if isinstance(data, dict) else {"results.json": data}
    if not isinstance(data, dict):
        print(f"note: {args.results} is not an object, wrapping it as 'results.json'\n")

    manifest = content_store.manifest(entries, label=args.label or "")
    print(f"stored {len(manifest['entries'])} entr"
          f"{'y' if len(manifest['entries']) == 1 else 'ies'}; "
          f"manifest at {manifest['manifest_address'][:16]}...\n")

    payload = ca.anchor_payload(
        manifest, network=args.network, registry_address=args.registry,
        label=args.label or "", from_address=getattr(args, "from_address", None),
        allow_synthetic=args.allow_synthetic)

    _print_payload(payload)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, indent=2)
        print(f"payload written to {args.out}")

    return 1 if payload.get("refused") else 0


def cmd_verify(args):
    result = ca.verify_anchor(args.verify, args.root, network=args.network)

    print(BAR)
    print(f"  tx          : {result.get('tx_hash', args.verify)}")
    print(f"  expected    : {result['expected_root']}")
    print(f"  status      : {result['status']}")
    print(f"  verified    : {result['verified']}")
    print(BAR)

    if result.get("note"):
        print(f"\n{result['note']}")
    if result.get("block_number") is not None:
        print(f"\nblock {result['block_number']}  |  {result['explorer_url']}")
    if result.get("error"):
        print(f"\nerror: {result['error']}")
    print(f"\n{result['anchor_meaning']}\n")

    if not result.get("parse_verified", True):
        print("NOTE: this response parse has not been confirmed against a live Monad")
        print("node. Treat a pass here as provisional until it has been.\n")

    return 0 if result["verified"] else 3


def main(argv=None):
    p = argparse.ArgumentParser(
        description="Anchor a research run's Merkle root on Monad, or verify one.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="No key is ever read and nothing is broadcast. You sign it yourself.")
    p.add_argument("results", nargs="?", help="JSON file holding the run's results")
    p.add_argument("--label", help="human-readable run label, emitted with the anchor")
    p.add_argument("--network", default=ca.DEFAULT_NETWORK, choices=sorted(ca.NETWORKS),
                   help="default: %(default)s (testnet, on purpose)")
    p.add_argument("--registry", metavar="0x...",
                   help="ProvenanceRegistry address; omit for contract-free calldata")
    p.add_argument("--from", dest="from_address", metavar="0x...",
                   help="the address that will sign, for the payload's 'from' field")
    p.add_argument("--allow-synthetic", action="store_true",
                   help="anchor a record containing placeholder values anyway")
    p.add_argument("--out", metavar="FILE", help="also write the payload as JSON")
    p.add_argument("--verify", metavar="0xTXHASH", help="check an existing anchor instead")
    p.add_argument("--root", metavar="0xROOT", help="the root --verify should find")

    args = p.parse_args(argv)

    if args.verify:
        if not args.root:
            p.error("--verify also needs --root: there is nothing to check it against")
        return cmd_verify(args)
    if not args.results:
        p.error("give a results file, or --verify with --root")
    return cmd_anchor(args)


if __name__ == "__main__":
    sys.exit(main())
