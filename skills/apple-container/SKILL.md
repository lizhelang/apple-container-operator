---
name: apple-container
description: Apple Container Operator skill for portable AI agent instructions that operate, install, update, troubleshoot, and migrate Apple's native container runtime workflows from natural language, Docker-style commands, repository setup requests, and configuration adjustment requests. Use when a user asks to install or update this apple-container skill, set up, run, stop, restart, inspect, debug, exec into, configure, recreate, clean up, migrate from Docker, analyze a GitHub repository for Apple container setup, or troubleshoot local containers and images on macOS with Apple container, including Docker-style workflows such as docker run, docker ps, docker logs, docker exec, docker build, docker pull, docker stop, and compose-like service requests.
---

# Apple Container Operator

## Core Behavior

Operate Apple's native `container` runtime safely and conservatively. First identify what the user wants, then check local CLI capability before producing commands with uncertain flags. Never invent unsupported Apple container flags.

## Built-In Freshness Checks

At the start of a request that uses this skill, run `scripts/update-skill.sh --check` as a best-effort freshness check. The script caches remote freshness results for 24 hours by default, so normal skill use does not hit the network every time. Set `APPLE_CONTAINER_CHECK_TTL_SECONDS` to tune the interval, or pass `--refresh` when the user explicitly asks to check the latest version now. If a skill update is available and the local checkout has no conflicting changes, update the skill before continuing and report the new revision. If the check fails, continue with the current skill and mention the check failure briefly.

When the request involves the Apple `container` runtime, also run `scripts/install-container.sh --check` before assuming the local CLI is installed or current. This always checks local installation state, while remote release metadata is cached for 24 hours by default. Set `APPLE_CONTAINER_CHECK_TTL_SECONDS` to tune the interval, or pass `--refresh` when the user explicitly asks to check the latest Apple release now. If `container` is missing and the user asked to install/setup/run a container workflow, use the installation workflow. If a newer Apple container release appears available, prefer installing the latest official package when the user asked for setup/update; otherwise report the available update and continue conservatively.

## Intent-First Operation

Classify the request before acting: run, list, pull, logs, exec, stop, restart, delete, cleanup, configuration change, debug failure, Docker-style translation, GitHub/repository project setup, or compose-like service planning. Use `references/intent-model.md` for required inputs and confirmation rules.

## Installation

If the user explicitly asks to install or set up Apple container, consult `references/installation.md` and use `scripts/install-container.sh`. The script installs from the official `apple/container` GitHub release package, checks Apple silicon and macOS requirements, and starts the system service unless `--no-start` is supplied. Do not install Docker Desktop as a substitute.

## Self Update

Self-update is an internal capability, not a separate user workflow. Consult `references/self-update.md` when the freshness check reports an available update or fails.

## Docker As Intent Language

If the user says `docker` but the environment is Apple container, treat Docker syntax as a source of intent. Translate only the conservative subset you understand. When Apple container lacks an equivalent feature, say so and suggest a safe fallback. Use `references/docker-compatibility.md` and `scripts/translate-docker-command.py`.

## GitHub Or Repository Project Setup

If the user gives a GitHub URL, repository URL, or local source tree and asks to install, run, or set it up with Apple container, use `references/github-project-setup.md` and `scripts/analyze-repo-setup.py`. Treat this as analysis and planning first. Ask for missing configuration such as service choice, env vars, ports, mounts, build args, image tag, command, and data paths before executing system-changing commands.

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
- `references/github-project-setup.md` - analyze GitHub repositories or local source trees and plan Apple container setup with confirmation gates.
- `references/lifecycle-operations.md` - run, list, logs, exec, stop, restart, delete, update, and cleanup workflows.
- `references/configuration-changes.md` - plan changes to ports, env, mounts, names, tags, commands, working directory, and runtime behavior.
- `references/troubleshooting.md` - debug failures and environment issues.
- `references/safety-rules.md` - decide whether confirmation is needed.
- `references/unsupported-features.md` - document non-parity and uncertain features.

## Script Usage

- Run `scripts/install-container.sh` when the user explicitly asks to install or set up Apple container.
- Run `scripts/update-skill.sh --check` at the start of skill use; the default remote freshness cache TTL is 24 hours. Use `--refresh` for explicit latest-version requests, and run `scripts/update-skill.sh` when the check reports an available safe update.
- Run `scripts/install-container.sh --check` before Apple `container` runtime operations; local state is checked each time, while remote release metadata uses the default 24-hour TTL unless `--refresh` is supplied.
- Run `scripts/detect-container.sh` to detect the local `container` CLI, version, system status, CPU architecture, and macOS version.
- Run `scripts/inspect-state.sh` for safe read-only diagnostics.
- Run `scripts/translate-docker-command.py "docker ps"` to convert Docker-style commands into JSON intent records.
- Run `scripts/analyze-repo-setup.py PATH_OR_URL` to analyze a GitHub URL or local checkout for Apple container setup planning.

When support is uncertain, run the relevant `container ... --help` command before giving a final command.
