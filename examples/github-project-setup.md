# GitHub Project Setup

Repository setup requests are analysis-first. Do not assume an arbitrary open-source project has Apple `container` documentation.

## "用 Apple container 安装这个 GitHub 项目"

Intent: `github_project_setup`.

Safe workflow:

1. Record the repository URL.
2. If the repository is not already checked out, ask or confirm where to clone it before fetching code.
3. On a local checkout, run:

```sh
skills/apple-container/scripts/analyze-repo-setup.py /path/to/repo
```

4. Summarize detected Dockerfile, Compose, README, package, env-example, ports, and runtime signals.
5. Ask for missing configuration before execution: service, env values, host ports, data mounts, image tag, build args, command, and whether to create containers.
6. Verify Apple `container` CLI support with local help before using build or run flags.

Example response shape:

```text
I found a Dockerfile, Compose file, and .env.example. The Compose services are:

- postgres: pulls postgres:18-alpine, uses named volume postgres_data, has a healthcheck.
- web: builds from Dockerfile, publishes 8080->3000, depends on postgres.

Before running it with Apple container, I need:

- image name/tag to build
- values for DATABASE_URL and APP_SECRET
- host port for container port 3000
- whether postgres_data should be created as an Apple container volume
- whether to replace Compose depends_on/healthcheck with an explicit wait script
- how Apple container should replace the Compose service-name DNS in DATABASE_URL=...@postgres...

No build or container commands have been run yet.
```

Recommended solution:

- create network `sample-repo-net`
- create volume `sample-repo-postgres-data`
- build `sample-repo-web:apple-container`
- run `sample-repo-postgres`
- wait for `pg_isready`
- if Docker/OrbStack source data exists, run `pg_dump | psql` into the Apple container database before starting web
- inspect the postgres container IP and use it in `DATABASE_URL`
- run `sample-repo-web`
- verify `curl -fsS -I http://localhost:8080/`

If the user says "use the recommended solution", execute the generated `recommended_solution.shell_script` after confirming it will not replace existing state.

If the project has Compose files, decompose services into explicit service plans, provide a recommended solution when enough information is available, and do not claim full Compose parity.
