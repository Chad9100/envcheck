from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

from .config import load_toml
from .result import FAIL, PASS, WARN, Result

_VER = re.compile(r"(\d+)(?:\.(\d+))?(?:\.(\d+))?")
_OPS = r"(>=|<=|==|!=|~=|>|<|=|\^|~)?"


def parse_version(text: str) -> tuple[int, ...] | None:
    m = _VER.search(text or "")
    if not m:
        return None
    return tuple(int(g) for g in m.groups() if g is not None)


def _pad(v: tuple[int, ...], n: int = 3) -> tuple[int, ...]:
    return tuple(v) + (0,) * (n - len(v))


def _cmp_one(have: tuple[int, ...], op: str, want: tuple[int, ...]) -> bool:
    h, w = _pad(have), _pad(want)
    if op in ("==", "=", ""):
        return h[: len(want)] == want  # partial versions match on prefix
    if op == "!=":
        return h[: len(want)] != want
    if op == ">=":
        return h >= w
    if op == ">":
        return h > w
    if op == "<=":
        return h <= w
    if op == "<":
        return h < w
    if op == "~=":  # compatible release: ~=3.11 means >=3.11,<4 ; ~=3.11.2 means <3.12
        if len(want) > 1:
            up = _pad(want[:-2] + (want[-2] + 1,))
        else:
            up = (want[0] + 1, 0, 0)
        return h >= w and h < up
    if op == "^":
        if want[0] > 0:
            up = (want[0] + 1, 0, 0)
        else:
            up = (0, _pad(want)[1] + 1, 0)
        return h >= w and h < up
    return True


def satisfies(have: tuple[int, ...], spec: str) -> bool | None:
    """Check a version against a spec like '>=3.11,<4', '^18' or '3.11'.

    Returns None when the spec cannot be understood.
    """
    spec = spec.strip()
    if not spec or spec == "*":
        return True
    any_ok = False
    for alt in spec.split("||"):
        parts = [p for p in re.split(r"[,\s]+", alt.strip()) if p]
        merged: list[str] = []
        for p in parts:  # join "op version" written with a space, e.g. ">= 18"
            if merged and re.fullmatch(r"[<>=!~^]+", merged[-1]):
                merged[-1] += p
            else:
                merged.append(p)
        alt_ok = True
        for part in merged:
            m = re.fullmatch(_OPS + r"v?(\d[\w.*]*)", part)
            if not m:
                return None
            op = m.group(1) or ""
            want = parse_version(m.group(2).replace("*", "").rstrip("."))
            if want is None:
                return None
            if op == "~":
                op = "~=" if len(want) > 1 else "=="
            if not _cmp_one(have, op, want):
                alt_ok = False
        any_ok = any_ok or alt_ok
    return any_ok


def installed_python() -> tuple[int, ...]:
    return tuple(sys.version_info[:3])


def installed_node() -> tuple[int, ...] | None:
    exe = shutil.which("node")
    if not exe:
        return None
    try:
        out = subprocess.run(
            [exe, "--version"], capture_output=True, text=True, timeout=10
        ).stdout
    except (OSError, subprocess.SubprocessError):
        return None
    return parse_version(out)


def _read(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8").strip()
    except OSError:
        return None


def _fmt(v: tuple[int, ...]) -> str:
    return ".".join(str(x) for x in v)


def _judge(name: str, source: str, spec: str, have: tuple[int, ...] | None) -> Result:
    label = f"{name} ({source})"
    if have is None:
        return Result(label, FAIL, f"{name} is required ({spec}) but not installed")
    ok = satisfies(have, spec)
    if ok is None:
        return Result(label, WARN, f"could not understand requirement '{spec}'")
    if ok:
        return Result(label, PASS, f"{name} {_fmt(have)} satisfies {spec}")
    return Result(label, FAIL, f"{name} {_fmt(have)} does not satisfy {spec}")


def check_versions(
    root: Path,
    python_version: tuple[int, ...] | None = None,
    node_version="auto",
) -> list[Result]:
    """node_version may be a tuple, None (not installed) or "auto" (detect)."""
    py = python_version or installed_python()
    results: list[Result] = []
    cache: list = []

    def node():
        if node_version != "auto":
            return node_version
        if not cache:
            cache.append(installed_node())
        return cache[0]

    text = _read(root / ".python-version")
    if text:
        first = text.splitlines()[0].strip()
        if parse_version(first):
            results.append(_judge("python", ".python-version", first, py))
        else:
            results.append(Result("python (.python-version)", WARN, f"unrecognised value '{first}'"))

    pyproj = root / "pyproject.toml"
    if pyproj.is_file():
        req = load_toml(pyproj).get("project", {}).get("requires-python")
        if isinstance(req, str):
            results.append(_judge("python", "pyproject.toml", req, py))

    text = _read(root / ".nvmrc")
    if text:
        first = text.splitlines()[0].strip()
        if parse_version(first):
            results.append(_judge("node", ".nvmrc", first.lstrip("v"), node()))
        else:  # aliases such as lts/*
            results.append(Result("node (.nvmrc)", WARN, f"cannot compare alias '{first}'"))

    pkg = root / "package.json"
    if pkg.is_file():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
        engines = data.get("engines") if isinstance(data, dict) else None
        spec = engines.get("node") if isinstance(engines, dict) else None
        if isinstance(spec, str):
            results.append(_judge("node", "package.json engines", spec, node()))

    if not results:
        results.append(Result("versions", PASS, "no runtime version requirements found"))
    return results
