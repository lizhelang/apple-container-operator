# Self Update

Use this file when the user asks to update, upgrade, refresh, or sync the Apple Container Operator skill itself.

## Behavior

The skill can update itself from the upstream repository:

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

Preview the update source and target:

```sh
skills/apple-container/scripts/update-skill.sh --dry-run
```

## Rules

- Update only this skill directory or its containing `apple-container-operator` git clone.
- Do not modify unrelated agent skills.
- If the repository has local uncommitted changes, the git update path should fail rather than merge or overwrite them.
- If a copied skill directory is updated, the updater records the upstream commit in `.apple-container-source-revision`.
- Report the updated revision and rerun a relevant smoke check after updating.
