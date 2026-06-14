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
I found a Dockerfile and .env.example. Before running it with Apple container, I need:

- image name/tag to build
- values for DATABASE_URL and APP_SECRET
- host port for container port 3000
- whether ./data should be mounted as persistent state

No build or container commands have been run yet.
```

If the project has Compose files, decompose services into explicit service plans and do not claim full Compose parity.
