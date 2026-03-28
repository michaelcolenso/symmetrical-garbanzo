# KPF (Knowledge Product Factory)

CLI-first runtime for discovering and packaging knowledge-product opportunities.

## Status

This repository currently implements **Milestone 1 — Foundations**:
- Python package skeleton
- `kpf` CLI entrypoint and required command names
- settings model + YAML loader
- workspace manager
- JSONL logging scaffold
- id + clock helpers
- run initializer that creates workspace state/config/log files

## Quickstart

```bash
uv python install 3.12
uv venv --python 3.12
source .venv/bin/activate
uv sync
kpf --help
kpf run "test niche"
```

## Development

```bash
uv sync --group dev
uv run pytest -q
```

## Implemented commands

```bash
kpf run "<niche>"
kpf inspect <run_id>
kpf validate <run_id>
kpf resume <run_id>
kpf export <run_id> --format markdown
```

> In this milestone, only `run` is implemented end-to-end; the others are scaffolds.

## Workspace output

A run creates:

```text
workspaces/run_<date>_<id>_<slug>/
  config.json
  cache/html/
  cache/pdf/
  cache/screenshots/
  artifacts/
  logs/run.jsonl
  logs/agent_calls.jsonl
  state/run_state.json
```
