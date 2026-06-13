# Claude Instructions

Use Apple Container Operator as a portable skill pack for Apple's native `container` runtime.

- Load `skills/apple-container/SKILL.md` first.
- Treat Docker commands as intent, not guaranteed compatibility.
- If the user asks to install Apple container, use `skills/apple-container/scripts/install-container.sh` and the official GitHub release package flow.
- If the user asks to update this skill, use `skills/apple-container/scripts/update-skill.sh`.
- Check `container --help` and subcommand help before using uncertain flags.
- Consult `skills/apple-container/references/safety-rules.md` before destructive actions.
- Use `skills/apple-container/scripts/translate-docker-command.py` for Docker-style input.
- Do not require Docker Desktop or Codex-specific APIs.
