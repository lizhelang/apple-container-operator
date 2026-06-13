# Gemini Instructions

Apple Container Operator helps agents operate Apple's native `container` runtime from natural language and Docker-style requests.

Follow this order:

1. Identify intent.
2. Consult the matching reference under `skills/apple-container/references/`.
3. Verify local `container` CLI support with help commands.
4. Produce conservative commands or a recreate/debug plan.
5. Ask for confirmation before destructive, multi-target, or data-affecting actions.

For install/setup requests, use `skills/apple-container/references/installation.md` and `skills/apple-container/scripts/install-container.sh`.

For skill update requests, use `skills/apple-container/references/self-update.md` and `skills/apple-container/scripts/update-skill.sh`.

Do not claim Docker Compose or Docker flag parity without local verification.
