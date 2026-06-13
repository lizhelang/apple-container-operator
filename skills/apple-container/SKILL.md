---
name: apple-container
description: portable ai agent instructions for operating, installing, and updating apple's native container runtime workflows from natural language, docker-style commands, and configuration adjustment requests. use when a user asks to install or update this apple-container skill, set up, run, stop, restart, inspect, debug, exec into, configure, recreate, clean up, migrate from docker, or troubleshoot local containers and images on macos with apple container, including docker-style workflows such as docker run, docker ps, docker logs, docker exec, docker build, docker pull, docker stop, and compose-like service requests.
---

# Apple Container Operator

## Core Behavior

Operate Apple's native `container` runtime safely and conservatively. First identify what the user wants, then check local CLI capability before producing commands with uncertain flags. Never invent unsupported Apple container flags.

## Intent-First Operation

Classify the request before acting: run, list, pull, logs, exec, stop, restart, delete, cleanup, configuration change, debug failure, Docker-style translation, or compose-like service planning. Use `references/intent-model.md` for required inputs and confirmation rules.

## Installation

If the user explicitly asks to install or set up Apple container, consult `references/installation.md` and use `scripts/install-container.sh`. The script installs from the official `apple/container` GitHub release package, checks Apple silicon and macOS requirements, and starts the system service unless `--no-start` is supplied. Do not install Docker Desktop as a substitute.

## Self Update

If the user asks to update or refresh this skill, consult `references/self-update.md` and use `scripts/update-skill.sh`. Check first with `--check` when the user only asks whether an update exists. When the user explicitly asks to update, run the updater and report the resulting revision.

## Docker As Intent Language

If the user says `docker` but the environment is Apple container, treat Docker syntax as a source of intent. Translate only the conservative subset you understand. When Apple container lacks an equivalent feature, say so and suggest a safe fallback. Use `references/docker-compatibility.md` and `scripts/translate-docker-command.py`.

## Safety Model

Read-only actions are allowed. Destructive operations require confirmation unless the user already explicitly requested the destructive operation and the target is narrow and unambiguous. Warn before deleting or recreating stateful services such as databases. Use `references/safety-rules.md`.

## Configuration Changes

Treat runtime configuration changes as state transition plans, not blind command rewrites. Inspect current state when possible. If the change cannot be applied in place, generate a stop/recreate plan that preserves existing settings as much as possible. Use `references/configuration-changes.md`.

## Troubleshooting Workflow

Diagnose in order: system, image, container status, logs, command/configuration, ports, mounts, and minimal reproduction. Use safe read-only commands first. Use `references/troubleshooting.md`.

## When To Consult Each Reference File

- `references/intent-model.md` - classify user requests and identify missing required information.
- `references/self-update.md` - update this skill from the upstream GitHub repository.
- `references/installation.md` - install or upgrade Apple container from official release packages.
- `references/command-map.md` - choose conservative Apple container commands and help checks.
- `references/docker-compatibility.md` - translate Docker-style commands into Apple container intent.
- `references/lifecycle-operations.md` - run, list, logs, exec, stop, restart, delete, update, and cleanup workflows.
- `references/configuration-changes.md` - plan changes to ports, env, mounts, names, tags, commands, working directory, and runtime behavior.
- `references/troubleshooting.md` - debug failures and environment issues.
- `references/safety-rules.md` - decide whether confirmation is needed.
- `references/unsupported-features.md` - document non-parity and uncertain features.

## Script Usage

- Run `scripts/install-container.sh` when the user explicitly asks to install or set up Apple container.
- Run `scripts/update-skill.sh` when the user explicitly asks to update this skill.
- Run `scripts/detect-container.sh` to detect the local `container` CLI, version, system status, CPU architecture, and macOS version.
- Run `scripts/inspect-state.sh` for safe read-only diagnostics.
- Run `scripts/translate-docker-command.py "docker ps"` to convert Docker-style commands into JSON intent records.

When support is uncertain, run the relevant `container ... --help` command before giving a final command.
