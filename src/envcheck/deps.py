from __future__ import annotations

import json
import re
from importlib import metadata
from pathlib import Path

from .config import load_toml
from .result import FAIL, PASS, WARN, Result

_NAME = re.compile(r"^\s*([A-Za-z0-9][A-Za-z0-9._-]*)")


def requirement_name(line: str) -> str | None:
    line = line.split("#", 1)[0].strip()
    if not line or line.startswith(("-", "git+", "http")):
        return None
    m = _NAME.match(line)
    return m.group(1) if m else None


def is_installed(name: str) -> bool:
    try:
        metadata.version(name)
        return True
    except metadata.PackageNotFoundError:
        return False


def _requirements_txt(path: Path) -> list[str]:
    names = []
    for line in path.read_text(encoding="utf-8").splitlines():
        n = requirement_name(line)
        if n:
            names.append(n)
    return names


def _pyproject_deps(path: Path) -> list[str]:
    deps = load_toml(path).get("project", {}).get("dependencies", [])
    names = []
    for d in deps if isinstance(deps, list) else []:
        n = requirement_name(d) if isinstance(d, str) else None
        if n:
            names.append(n)
    return names


def _python_results(source: str, names: list[str]) -> list[Result]:
    label = f"deps ({source})"
    missing = [n for n in names if not is_installed(n)]
    if missing:
        return [Result(label, FAIL, "not installed: " + ", ".join(sorted(missing)))]
    return [Result(label, PASS, f"{len(names)} packages installed")]


def check_deps(root: Path) -> list[Result]:
    results: list[Result] = []
    req = root / "requirements.txt"
    if req.is_file():
        results += _python_results("requirements.txt", _requirements_txt(req))
    pyproj = root / "pyproject.toml"
    if pyproj.is_file():
        names = _pyproject_deps(pyproj)
        if names:
            results += _python_results("pyproject.toml", names)
    pkg = root / "package.json"
    if pkg.is_file():
        try:
            data = json.loads(pkg.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
        declared = isinstance(data, dict) and (
            data.get("dependencies") or data.get("devDependencies")
        )
        if (root / "node_modules").is_dir():
            results.append(Result("deps (package.json)", PASS, "node_modules exists"))
        elif declared:
            results.append(
                Result("deps (package.json)", FAIL, "node_modules missing, run npm install")
            )
        else:
            results.append(Result("deps (package.json)", WARN, "no dependencies declared"))
    if not results:
        results.append(Result("deps", PASS, "no dependency files found"))
    return results
