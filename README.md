# envcheck

A tiny project setup checker. Run `envcheck` in a code project and it tells you,
with readable PASS / WARN / FAIL lines, whether the project is ready to run.

## What it does

1. **Runtime versions**: reads `.python-version`, `.nvmrc`, `requires-python`
   in `pyproject.toml` and `engines.node` in `package.json`, and compares them
   with the installed `python` and `node`.
2. **.env keys**: every key in `.env.example` must exist in `.env`. Missing and
   extra keys are reported. Values are never read into output or printed.
3. **Ports**: ports listed in `[tool.envcheck]` (pyproject.toml) or
   `envcheck.toml` (`ports = [8000, 5432]`) must be free to bind.
4. **Dependencies**: `requirements.txt` and pyproject `dependencies` are checked
   with `importlib.metadata`; for `package.json` it checks `node_modules` exists.

Exit code is `1` if any check FAILs, otherwise `0` (`2` for a bad folder).

## Who it is for

Developers onboarding to a repository, and teams who want a quick "is my machine
set up?" command in READMEs or CI.

## Built with

Python 3.11+ and the standard library only (no runtime dependencies).

## Install

```
pip install git+https://github.com/Chad9100/envcheck.git
```

## Usage

```
envcheck              # check the current folder
envcheck path/to/app  # check another folder
envcheck --format json
```

Config (optional), in `envcheck.toml` or `pyproject.toml` under `[tool.envcheck]`:

```toml
ports = [8000, 5432]
```

Example output, captured from a real run on a small demo project (with a
`.python-version`, `.nvmrc`, `.env.example`, `.env`, `envcheck.toml` and
`requirements.txt`). Only key names are shown, never values:

```
PASS  python (.python-version): python 3.12.10 satisfies 3.12
FAIL  node (.nvmrc): node is required (18) but not installed
FAIL  env: missing keys in .env: DATABASE_URL
WARN  env: extra keys in .env: DEBUG_TOOLBAR
PASS  port 8000: free
FAIL  deps (requirements.txt): not installed: example-missing-pkg

2 passed, 1 warnings, 3 failed
```

The exit code for this run is `1` because some checks failed.

## Development

```
python -m venv .venv
.venv/Scripts/activate        # Windows; use source .venv/bin/activate on Linux/macOS
pip install -e ".[dev]"
pytest -q
```

## License

MIT, see [LICENSE](LICENSE). See [ROADMAP.md](ROADMAP.md) for plans.
