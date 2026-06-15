<p align="center">
  <img src="./docs/assets/apple-container-operator-icon.svg" alt="Apple Container Operator icon" width="156" />
</p>

<h1 align="center">Apple Container Operator</h1>

<p align="center">
  A problem-solving operator that helps AI agents safely understand, translate, install, update, and execute Apple native <code>container</code> workflows.
</p>

<p align="center">
  <a href="./LICENSE"><img alt="license Apache-2.0" src="https://img.shields.io/badge/license-Apache--2.0-blue" /></a>
  <a href="https://skills.sh/lizhelang/apple-container-operator/apple-container"><img alt="skills.sh installs" src="https://skills.sh/b/lizhelang/apple-container-operator" /></a>
  <img alt="skill apple-container" src="https://img.shields.io/badge/skill-apple--container-5B6B8C" />
  <img alt="runtime Apple container" src="https://img.shields.io/badge/runtime-Apple%20container-111827" />
</p>

<p align="center">
  English | <a href="./README.md">简体中文</a>
</p>

Apple Container Operator helps AI agents safely understand, translate, install, update, and execute Apple native `container` workflows.

> Treat Docker commands as intent, Apple `container` as the execution target, and local CLI help as the source of truth for uncertain flags.

## Setup

When this skill is invoked, the agent should perform a lightweight freshness check with bounded network use: verify whether Apple Container Operator itself is current; when the request involves Apple `container`, also check whether the local `container` CLI is installed and whether a newer release may be available. Remote freshness checks are cached for 24 hours by default. Set `APPLE_CONTAINER_CHECK_TTL_SECONDS` to another interval, such as `604800` for seven days, or pass `--refresh` when the user explicitly asks to check latest versions now.

### Install This Skill Pack

If your agent supports [skills.sh](https://skills.sh/), install it directly:

```sh
npx skills add lizhelang/apple-container-operator --skill apple-container-operator
```

`apple-container-operator` is the discoverable public name. `apple-container` remains available as a stable alias for existing install commands.

Or open the skills.sh page to inspect and install it:

```text
https://skills.sh/lizhelang/apple-container-operator/apple-container
https://skills.sh/lizhelang/apple-container-operator/apple-container-operator
```

Send this prompt to your AI coding agent:

```text
Install the Apple Container Operator skill pack from https://github.com/lizhelang/apple-container-operator.

Clone the repository, inspect its README and skills/apple-container/SKILL.md, then install or reference the apple-container skill in your local agent skill/rules system so future requests about Apple container use this skill automatically.
```

### Install Apple Container

Send this prompt after the skill pack is available:

```text
Use the apple-container skill to install Apple's native container runtime on this Mac.

Follow the skill's installation workflow: verify this is an Apple silicon Mac, check the macOS version, download the latest official signed installer package from apple/container GitHub Releases, install it with the macOS installer, run container --version, start the system service with container system start, and verify the result. Do not install Docker Desktop as a substitute.
```

### Install Skill Pack And Apple Container Together

Send this prompt to do both in one pass:

```text
Set up Apple Container Operator end to end.

First install the Apple Container Operator skill pack from https://github.com/lizhelang/apple-container-operator into your local agent skill/rules system. Then use that skill to install Apple's native container runtime on this Mac from the official apple/container GitHub Releases signed installer package. Verify Apple silicon and macOS support, install the package, run container --version, start container system service, and report the final status. Do not install Docker Desktop as a substitute.
```

### Migrate Docker Services To Apple Container

Send this prompt to migrate existing Docker-based services:

```text
Use Apple Container Operator to inspect my Docker-based service setup, identify images, ports, env vars, volumes, commands, dependencies, and stateful data, then create and execute a safe migration plan to Apple's native container runtime without assuming full Docker or Compose parity.
```

### Run A GitHub Project With Apple Container

Many open-source projects do not document Apple `container` directly. Send the repository link and ask the agent to analyze before running anything:

```text
Use Apple Container Operator to inspect this GitHub repository and create an Apple container setup plan: https://github.com/OWNER/REPO.

Clone only after confirming the target location if needed. Analyze Dockerfile, Compose files, README, env examples, package metadata, ports, commands, and persistent data needs. Ask me for missing configuration such as service choice, environment variable values, host ports, mounts, image tag, build args, and startup command before building or running containers.
```

## Installation And Usage

### Generic AI Agents

Copy or reference `skills/apple-container/SKILL.md` in your agent's skill, rule, or instruction system. The skill routes detailed behavior to `skills/apple-container/references/` and deterministic helpers in `skills/apple-container/scripts/`.

Agents should run:

```sh
skills/apple-container/scripts/detect-container.sh
skills/apple-container/scripts/install-container.sh --check
skills/apple-container/scripts/inspect-state.sh
skills/apple-container/scripts/analyze-repo-setup.py /path/to/repo
skills/apple-container/scripts/update-skill.sh --check
```

before assuming local support for commands or flags. The `--check` commands use a 24-hour remote metadata TTL by default; use `--refresh` to bypass the cache.

### Codex Via AGENTS.md

Use the root `AGENTS.md` as repository guidance. When operating Apple container for a user, load `skills/apple-container/SKILL.md`, consult the relevant reference file, and verify local CLI support with `container --help` or subcommand help before using uncertain flags.

### Claude Via CLAUDE.md

Point Claude Code at `agents/CLAUDE.md`. It summarizes the portable behavior and directs Claude to the skill and references without relying on Codex-specific APIs.

### Cursor Via Rules File

Use `agents/cursor-rules.md` as Cursor project rules. Keep command mappings conservative and test any changes to Docker-style translation.

## Examples

User: "run postgres with password pass and expose it locally"

Agent behavior: identify `run_container`, check `container run --help`, plan env and port settings, warn about database persistence, then produce a conservative `container run` command only with verified flags.

User: `docker ps`

Agent behavior: treat this as `list_containers`, translate to the nearest Apple container list command, and verify exact list syntax with help if uncertain.

User: `docker logs -f app`

Agent behavior: treat this as `view_logs`, use Apple container logs if available, and verify whether follow mode is supported before adding a follow flag.

User: "change app port from 3000 to 8080"

Agent behavior: treat this as `configuration_change`, inspect current settings if possible, then generate a stop/recreate plan that preserves the image, env, mounts, command, and name as much as possible.

User: "this container will not start, debug it"

Agent behavior: follow the troubleshooting sequence: check system, image, container status, logs, command/configuration, ports, mounts, then suggest a minimal reproduction.

User: "install Apple container for me"

Agent behavior: verify Apple silicon and macOS support, download the latest signed installer package from the official `apple/container` GitHub release, run the macOS installer, then start and verify the system service.

User: "use container to install this GitHub project: https://github.com/OWNER/REPO"

Agent behavior: identify `github_project_setup`, confirm whether and where to clone, statically analyze Dockerfile, Compose, README, package metadata, and `.env.example` files in the local checkout, then list the ports, env vars, mounts, image tag, build args, startup command, and service choice that must be confirmed. It does not run builds or create containers before confirmation.

## Compatibility Disclaimer

Apple container is not Docker. Docker-style commands are interpreted as intent, not as proof of flag or workflow parity. Agents and maintainers should check the local `container` CLI help and version before assuming flag support.
