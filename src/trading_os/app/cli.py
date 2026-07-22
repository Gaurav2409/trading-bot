"""Operator CLI. Commands are read-only or narrowly-scoped control actions;
none accept a natural-language order."""

import argparse

COMMANDS = (
    "readiness",
    "observe",
    "reconcile",
    "replay",
    "run-cycle",
    "activate-policy",
    "entry-disable",
    "reduce-only",
    "halt",
    "issue-live-authority",
    "verify-live-authority",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="trading_os", description="Trading OS operator CLI")
    sub = parser.add_subparsers(dest="command", required=True)

    readiness = sub.add_parser("readiness", help="print broker readiness report")
    readiness.add_argument("--all-accounts", action="store_true")
    readiness.add_argument("--read-only", action="store_true")

    for name in COMMANDS:
        if name == "readiness":
            continue
        p = sub.add_parser(name)
        p.add_argument("--account-id", default=None)
    return parser


def main(argv: list[str] | None = None) -> int:  # pragma: no cover - thin entry point
    parser = build_parser()
    args = parser.parse_args(argv)
    print(f"command={args.command}")
    return 0
