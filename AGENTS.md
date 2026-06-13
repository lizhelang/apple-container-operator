# Apple Container Operator Agent Guide

## Project Purpose

Apple Container Operator is a vendor-neutral skill pack that helps AI coding agents operate Apple's native `container` runtime from natural language, Docker-style workflows, and configuration requests. Docker syntax is treated as intent, not as a guarantee of Apple container parity.

## Repository Layout

- `skills/apple-container/SKILL.md` - portable skill entry point.
- `skills/apple-container/references/` - behavior, safety, compatibility, and workflow references.
- `skills/apple-container/scripts/` - small deterministic helper scripts.
- `agents/` - adapter instructions for Claude, Gemini, and Cursor.
- `examples/` - sample agent responses and workflows.
- `tests/` - translation tests and fixtures.

## Development Commands

```sh
python3 skills/apple-container/scripts/translate-docker-command.py "docker ps"
skills/apple-container/scripts/install-container.sh --help
skills/apple-container/scripts/detect-container.sh
skills/apple-container/scripts/inspect-state.sh
```

## Testing Commands

```sh
python3 -m unittest discover -s tests
```

## Rules

- Keep the project vendor-neutral.
- Do not hard-code Codex-specific assumptions.
- Do not claim full Docker compatibility.
- Prefer explicit unsupported-feature documentation over fake parity.
- Treat destructive container operations as requiring confirmation.
- Treat Apple container installation as a system-modifying operation; proceed only when the user explicitly asks for install/setup.
- Keep command mappings conservative and test-backed.
- Verify local `container` CLI help before assuming support for uncertain flags.
- Do not add dependencies for the initial translator without a clear need.

## Preferred Implementation Style

- Use Markdown references for behavior.
- Use small scripts for deterministic checks and translation.
- Use tests for translation behavior.
- Keep mappings easy to audit and update as Apple container evolves.
