from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .deps import check_deps
from .envfile import check_env
from .ports import check_ports
from .result import FAIL, Result
from .versions import check_versions


def run_checks(root: Path) -> list[Result]:
    results: list[Result] = []
    for fn in (check_versions, check_env, check_ports, check_deps):
        results.extend(fn(root))
    return results


def format_text(results: list[Result]) -> str:
    lines = [f"{r.status:<4}  {r.check}: {r.message}" for r in results]
    n = {s: sum(1 for r in results if r.status == s) for s in ("PASS", "WARN", "FAIL")}
    lines.append("")
    lines.append(f"{n['PASS']} passed, {n['WARN']} warnings, {n['FAIL']} failed")
    return "\n".join(lines)


def format_json(results: list[Result]) -> str:
    return json.dumps(
        {
            "ok": not any(r.status == FAIL for r in results),
            "results": [r.to_dict() for r in results],
        },
        indent=2,
    )


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="envcheck", description="Check a project's setup.")
    p.add_argument("folder", nargs="?", default=".", help="project folder (default: .)")
    p.add_argument("--format", choices=["text", "json"], default="text")
    p.add_argument("--version", action="version", version=f"envcheck {__version__}")
    args = p.parse_args(argv)
    root = Path(args.folder)
    if not root.is_dir():
        print(f"envcheck: not a folder: {args.folder}", file=sys.stderr)
        return 2
    results = run_checks(root)
    print(format_json(results) if args.format == "json" else format_text(results))
    return 1 if any(r.status == FAIL for r in results) else 0
