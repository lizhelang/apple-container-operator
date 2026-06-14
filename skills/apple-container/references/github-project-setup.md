# GitHub Project Setup

Use this workflow when the user gives a GitHub URL, repository URL, or local source tree and asks to install, run, or set it up with Apple `container`.

## Principle

Repository setup is an analysis-and-plan workflow first. Most open-source projects do not document Apple `container` directly, so infer intent from common project files but do not invent missing configuration.

## Safe Default

Read-only analysis is safe:

1. Identify whether the input is a URL or a local path.
2. If it is a URL and the user has not explicitly allowed cloning, explain the clone step that would be needed.
3. If a local checkout is available, run `scripts/analyze-repo-setup.py PATH`.
4. Read Dockerfile, Compose, README, package, and env-example signals from the analyzer output.
5. Produce a setup plan with clear user-confirmation questions before any system-changing command.

## What To Inspect

- `Dockerfile`, `Containerfile`, and `*.Dockerfile` for image build signals.
- `compose.yaml`, `compose.yml`, `docker-compose.yaml`, and `docker-compose.yml` for multi-service signals.
- `.env.example`, `.env.sample`, and similar files for required environment variables.
- `README*` for documented ports, commands, and setup notes.
- `package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml`, and similar files for runtime hints.

## Confirmation Required

Ask the user when any of these are missing or ambiguous:

- Which service to run from a multi-service project.
- Image name/tag to build or pull.
- Build target, build args, platform, or secrets.
- Runtime environment variable values.
- Host ports to expose.
- Host directories for persistent data or bind mounts.
- Startup command or working directory.
- Whether to create, replace, stop, delete, or recreate containers.
- Whether to install Apple `container` itself.

If the first user prompt already gives a narrow explicit value, use that value and still verify Apple `container` CLI support before execution.

## Planning Output

A good response should include:

1. What was detected.
2. What can be done safely now.
3. What must be confirmed by the user.
4. Tentative Apple `container` commands only for supported or help-verified options.
5. Unsupported or uncertain Docker/Compose features.

## Execution Gate

Do not run build, pull, run, stop, delete, installer, package-manager, migration, or data-directory creation commands from this workflow until the required confirmations are resolved.

When the user confirms the missing values, continue through `references/lifecycle-operations.md`, `references/docker-compatibility.md`, and `references/safety-rules.md`.
