# GitHub Project Setup Design

## Goal

Support the user flow: "Here is a GitHub project; install or run it with Apple container." The operator should turn a repository URL or checked-out source tree into a conservative Apple `container` setup plan.

## Constraints

- Do not claim generic Docker or Compose parity.
- Do not install dependencies, run build scripts, create containers, delete state, or clone private code unless the user explicitly asks.
- Treat unknown configuration as a user-confirmation requirement, not as a default to invent.
- Keep the project vendor-neutral and dependency-free.

## Chosen Approach

Add a repository setup workflow backed by a deterministic static analyzer. The analyzer inspects a local repository path, or records a GitHub URL as needing a clone step, and emits JSON with:

- detected files and likely runtime signals;
- tentative Apple container workflow steps;
- required user confirmations;
- unsupported or uncertain features;
- safety notes.

The skill uses this JSON as evidence for the final plan. It can ask the user for missing configuration before executing anything that changes the system.

## Alternatives Considered

1. Put the behavior only in Markdown instructions.
   This is easy to write but hard to test, so future edits could silently lose the confirmation behavior.

2. Build a full automatic installer.
   This is too risky for arbitrary open-source projects because many repositories need secrets, ports, data directories, service choices, or non-container setup steps.

3. Add a static analyzer plus references and tests.
   This keeps the first version safe, auditable, and useful. It is the chosen approach.

## Confirmation Model

Ask before:

- cloning into a specific directory when the target path matters;
- building an image when the Dockerfile target, tag, build args, platform, or secrets are unclear;
- running any container with unknown env vars, ports, mounts, commands, or service selection;
- creating stateful data directories;
- running multi-service Compose-like setups;
- installing Apple container itself;
- deleting, replacing, or recreating containers or data.

Read-only analysis can proceed without confirmation.

## Testing

Unit tests cover local fixture repositories with Dockerfile, Compose, package metadata, README, and `.env.example` signals. The tests assert that unclear env vars, ports, mounts, build support, and Compose parity are surfaced as confirmations or uncertainty instead of silently becoming commands.
