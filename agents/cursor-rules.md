# Cursor Rules

- Use `skills/apple-container/SKILL.md` for Apple container operations.
- Keep this project vendor-neutral and agent-portable.
- Do not add OpenAI-only, Claude-only, Cursor-only, or Gemini-only runtime code.
- Treat Docker syntax as intent.
- Support explicit Apple container install/setup requests through `skills/apple-container/scripts/install-container.sh`.
- Support explicit self-update requests through `skills/apple-container/scripts/update-skill.sh`.
- Keep command mappings conservative and covered by `tests/test_translate_docker_command.py`.
- Never write scripts that stop, delete, prune, or mutate containers without explicit user confirmation.
- Prefer Markdown reference updates plus small standard-library scripts.
