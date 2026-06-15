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
5. When `detected.service_plans` is present, treat it as the primary service inventory for Compose migration planning.
6. Produce both a factual service plan and a recommended deployment plan with clear user-confirmation questions before any system-changing command.

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

For Compose-derived projects, include a service-by-service summary from `detected.service_plans`:

- service name and whether it is built locally or pulled as an image
- detected host/container port mappings
- detected environment variable keys
- named volumes and bind mounts that must be preserved
- service dependencies that require explicit start order or readiness checks
- environment variables that reference Compose service names such as `postgres`, `redis`, or `db`
- Compose-only semantics such as `depends_on`, `healthcheck`, and `restart` that Apple `container` will not apply automatically

Do not assume Docker Compose service-name DNS works in Apple `container`. If an env var such as `PGHOST=postgres` or `DATABASE_URL=...@postgres...` points at another Compose service, ask for or derive a verified Apple `container` networking replacement before claiming the stack can run.

Also include `recommended_solution` when the analyzer provides it. Treat it as the default "do this for me" plan:

- resource names for networks, volumes, images, and containers
- recommended host ports, including any automatic change when a detected port is already in use
- dynamic runtime values, such as inspected dependency IPs that replace Compose service-name DNS
- data migration strategy for named volumes and databases; never silently treat a new Apple container volume as migrated data
- ordered commands and a single `shell_script` that can be run as one unit after user approval
- verification commands that prove the app responds
- remaining confirmations that would block safe execution, such as replacing existing resources or filling sensitive secrets

If `recommended_solution.shell_script` is present, the user may approve with language such as "use the recommended solution". Execute that script only after checking the remaining confirmations are acceptable for the requested scope.

For stateful services, distinguish "recreate" from "migrate". If Docker/OrbStack Compose volumes or containers are detected, include a `data_migration` section. For PostgreSQL, prefer an explicit `pg_dump | psql` restore step from the source Docker/OrbStack container into the target Apple container database, after target readiness and before dependent apps start. Mark target database replacement as destructive and require clear approval before running it against an existing Apple container database.

## Execution Gate

Do not run build, pull, run, stop, delete, installer, package-manager, migration, or data-directory creation commands from this workflow until the required confirmations are resolved.

When the user confirms the missing values, continue through `references/lifecycle-operations.md`, `references/docker-compatibility.md`, and `references/safety-rules.md`.
