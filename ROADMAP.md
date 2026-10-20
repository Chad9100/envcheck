# Roadmap

## v0.1 (done)

- [x] Runtime version checks: `.python-version`, `.nvmrc`, `requires-python`, `engines.node`
- [x] `.env` vs `.env.example` key comparison (values never printed)
- [x] Port availability from `[tool.envcheck]` / `envcheck.toml`
- [x] Dependency checks: requirements.txt, pyproject dependencies, node_modules
- [x] Text and JSON output, exit code 1 on FAIL
- [x] pytest suite, CI on Ubuntu and Windows

## v0.2 - Better dependency checks (~5h)

- [ ] Verify installed versions against specifiers, not just presence (~2h)
- [ ] Support `optional-dependencies` groups and `requirements-*.txt` with `-r` includes (~2h)
- [ ] Check lockfile freshness (package-lock.json, poetry.lock, uv.lock) (~1h)

## v0.3 - More runtimes (~6h)

- [ ] `.tool-versions` (asdf), `.ruby-version`, `go.mod`, `rust-toolchain.toml` (~3h)
- [ ] `.sdkmanrc` / Java version, `.dotnet` global.json (~2h)
- [ ] Check `npm`/`pnpm`/`yarn` and `packageManager` field (~1h)

## v0.4 - Config and UX (~5h)

- [ ] `--only` / `--skip` check selection (~1h)
- [ ] Colored output, `--no-color`, `NO_COLOR` support (~1h)
- [ ] `--quiet` and `--strict` (treat WARN as FAIL) (~1h)
- [ ] Custom checks: required commands on PATH, required files (~2h)

## v0.5 - Services (~5h)

- [ ] Check that ports are *listening* (for dependent services such as a database) (~2h)
- [ ] Docker / docker compose availability and running containers (~2h)
- [ ] Optional TCP/HTTP health probes with timeouts, opt-in only (~1h)

## v0.6 - Env file depth (~4h)

- [ ] Proper dotenv parsing: quotes, multiline values, interpolation (~2h)
- [ ] Detect empty required values and placeholder values (~1h)
- [ ] Support `.env.local`, `.env.development` layering (~1h)

## v0.7 - Reporting (~4h)

- [ ] SARIF / JUnit XML output for CI (~2h)
- [ ] GitHub Actions annotations format (~1h)
- [ ] `--fix-hint` suggestions per failure (~1h)

## v0.8 - Monorepos (~4h)

- [ ] Recursive discovery of sub-projects (~2h)
- [ ] Per-project config and summary table (~2h)

## v0.9 - Hardening (~4h)

- [ ] Full PEP 440 / semver parser edge cases (~2h)
- [ ] macOS CI, Python 3.14 (~1h)
- [ ] Type hints checked with mypy, ruff in CI (~1h)

## v1.0 - Release (~3h)

- [ ] Stable JSON schema and documented exit codes (~1h)
- [ ] PyPI publishing workflow (~1h)
- [ ] Docs site / full usage guide (~1h)
