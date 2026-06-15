# Self Update

Use this file when the skill performs its built-in freshness check, or when the user asks to update, upgrade, refresh, or sync the Apple Container Operator skill itself.

## Behavior

The skill should check itself at the start of normal use. Remote revision lookup is cached for 24 hours by default to avoid repeated network calls:

```sh
skills/apple-container/scripts/update-skill.sh --check
```

Use `--refresh` when the user explicitly asks to check the latest version now. Set `APPLE_CONTAINER_CHECK_TTL_SECONDS` to tune the interval.

If the check reports an available update and there are no local conflicts, update from the upstream repository:

```sh
skills/apple-container/scripts/update-skill.sh
```

The updater supports two install shapes:

- Git clone: it runs `git pull --ff-only origin main` from the repository root.
- Copied skill directory: it downloads the latest repository archive and replaces the local `apple-container` skill directory.

## Safe Checks

Check without modifying files:

```sh
skills/apple-container/scripts/update-skill.sh --check
```

Bypass the freshness cache:

```sh
skills/apple-container/scripts/update-skill.sh --check --refresh
```

Preview the update source and target:

```sh
skills/apple-container/scripts/update-skill.sh --dry-run
```

## Rules

- Update only this skill directory or its containing `apple-container-operator` git clone.
- Do not modify unrelated agent skills.
- If the repository has local uncommitted changes, the git update path should fail rather than merge or overwrite them.
- If a copied skill directory is updated, the updater records the upstream commit in `.apple-container-source-revision`.
- Built-in check results should respect the script's remote freshness TTL instead of fetching on every skill invocation.
- Treat check failures as non-fatal; continue with the current skill and report that freshness could not be verified.
- Report the updated revision and rerun a relevant smoke check after updating.
