#!/usr/bin/env python3
"""Translate a conservative Docker-style command subset into intent JSON."""

from __future__ import annotations

import argparse
import json
import shlex
import sys
from typing import Any


def record(
    input_text: str,
    intent: str,
    confidence: str,
    commands: list[str],
    requires_confirmation: bool = False,
    unsupported: list[str] | None = None,
    notes: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "input": input_text,
        "intent": intent,
        "confidence": confidence,
        "apple_container_commands": commands,
        "requires_confirmation": requires_confirmation,
        "unsupported_or_uncertain": unsupported or [],
        "notes": notes or [
            "Docker syntax is treated as intent; verify Apple container CLI help before using uncertain flags."
        ],
    }


def read_input(argv: list[str]) -> tuple[str, list[str]]:
    if not argv:
        text = sys.stdin.read().strip()
    elif len(argv) == 1:
        text = argv[0]
    else:
        text = " ".join(shlex.quote(part) for part in argv)
    try:
        parts = shlex.split(text)
    except ValueError as exc:
        return text, ["docker", "__parse_error__", str(exc)]
    return text, parts


def parse_run(input_text: str, parts: list[str]) -> dict[str, Any]:
    name = None
    ports: list[str] = []
    envs: list[str] = []
    unsupported: list[str] = []
    image = None
    command: list[str] = []
    i = 2

    while i < len(parts):
        token = parts[i]
        if token in ("--name",):
            if i + 1 < len(parts):
                name = parts[i + 1]
                i += 2
                continue
            unsupported.append(token)
            i += 1
            continue
        if token.startswith("--name="):
            name = token.split("=", 1)[1]
            i += 1
            continue
        if token in ("-p", "--publish"):
            if i + 1 < len(parts):
                ports.append(parts[i + 1])
                i += 2
                continue
            unsupported.append(token)
            i += 1
            continue
        if token.startswith("-p") and token != "-p":
            ports.append(token[2:])
            i += 1
            continue
        if token.startswith("--publish="):
            ports.append(token.split("=", 1)[1])
            i += 1
            continue
        if token in ("-e", "--env"):
            if i + 1 < len(parts):
                envs.append(parts[i + 1])
                i += 2
                continue
            unsupported.append(token)
            i += 1
            continue
        if token.startswith("-e") and token != "-e":
            envs.append(token[2:])
            i += 1
            continue
        if token.startswith("--env="):
            envs.append(token.split("=", 1)[1])
            i += 1
            continue
        if token.startswith("-"):
            unsupported.append(token)
            i += 1
            continue
        image = token
        command = parts[i + 1 :]
        break

    commands = ["container run --help"]
    run_bits = ["container", "run"]
    if name:
        run_bits += ["--name", name]
    for port in ports:
        run_bits += ["-p", port]
    for env in envs:
        run_bits += ["-e", env]
    if image:
        run_bits.append(image)
    run_bits += command
    if image:
        commands.append(" ".join(shlex.quote(bit) for bit in run_bits))

    uncertain = list(unsupported)
    if name:
        uncertain.append("--name flag: verify with container run --help")
    if ports:
        uncertain.append("port mapping flag: verify with container run --help")
    if envs:
        uncertain.append("environment flag: verify with container run --help")

    return record(
        input_text,
        "run_container",
        "medium" if image else "low",
        commands,
        unsupported=uncertain,
        notes=[
            "Run flags are tentative until verified against local Apple container help.",
            "Warn before recreating or replacing stateful services.",
        ],
    )


def translate(input_text: str, parts: list[str]) -> dict[str, Any]:
    if len(parts) < 2 or parts[0] != "docker":
        return record(input_text, "unknown", "low", [], unsupported=["not a docker command"])

    sub = parts[1]

    if sub == "ps":
        unsupported = [p for p in parts[2:] if p != "-a"]
        if "-a" in parts[2:]:
            unsupported.append("-a flag: verify stopped-container listing support")
        return record(input_text, "list_containers", "high", ["container list"], unsupported=unsupported)

    if sub == "images":
        return record(input_text, "list_images", "high", ["container image list"], unsupported=parts[2:])

    if sub == "pull" and len(parts) >= 3:
        return record(input_text, "pull_image", "high", [f"container image pull {shlex.quote(parts[2])}"], unsupported=parts[3:])

    if sub == "run":
        return parse_run(input_text, parts)

    if sub == "logs" and len(parts) >= 3:
        follow = False
        unsupported: list[str] = []
        names: list[str] = []
        for token in parts[2:]:
            if token == "-f" or token == "--follow":
                follow = True
            elif token.startswith("-"):
                unsupported.append(token)
            else:
                names.append(token)
        name = names[0] if names else ""
        commands = ["container logs --help"]
        if name:
            commands.append(f"container logs {shlex.quote(name)}")
        if follow:
            unsupported.append("follow logs flag: verify with container logs --help")
        return record(input_text, "view_logs", "high" if name else "low", commands, unsupported=unsupported)

    if sub == "exec" and len(parts) >= 4:
        unsupported: list[str] = []
        rest = parts[2:]
        while rest and rest[0].startswith("-"):
            if rest[0] in ("-i", "-t", "-it", "-ti"):
                unsupported.append(f"{rest[0]} TTY/interactive flag: verify with container exec --help")
            else:
                unsupported.append(rest[0])
            rest = rest[1:]
        name = rest[0] if rest else ""
        command = rest[1:]
        intent = "exec_shell" if command and command[0] in ("sh", "bash", "zsh") else "exec_command"
        commands = ["container exec --help"]
        if name and command:
            quoted = " ".join(shlex.quote(x) for x in [name] + command)
            commands.append(f"container exec {quoted}")
        return record(input_text, intent, "high" if name and command else "low", commands, unsupported=unsupported)

    if sub == "stop" and len(parts) >= 3:
        target = parts[2]
        return record(input_text, "stop_container", "high", [f"container stop {shlex.quote(target)}"], unsupported=parts[3:])

    if sub == "rm" and len(parts) >= 3:
        target = parts[2]
        return record(
            input_text,
            "delete_container",
            "high",
            [f"container delete {shlex.quote(target)}"],
            requires_confirmation=True,
            unsupported=parts[3:],
            notes=["Deleting containers may remove local state; confirm target and data impact first."],
        )

    if sub == "rmi" and len(parts) >= 3:
        image = parts[2]
        return record(
            input_text,
            "delete_image",
            "high",
            [f"container image delete {shlex.quote(image)}"],
            requires_confirmation=True,
            unsupported=parts[3:],
        )

    if sub == "build":
        tag = None
        unsupported: list[str] = []
        context = None
        i = 2
        while i < len(parts):
            token = parts[i]
            if token == "-t" and i + 1 < len(parts):
                tag = parts[i + 1]
                i += 2
            elif token.startswith("-"):
                unsupported.append(token)
                i += 1
            else:
                context = token
                i += 1
        commands = ["container build --help"]
        if tag and context:
            commands.append(f"container build -t {shlex.quote(tag)} {shlex.quote(context)}")
        return record(
            input_text,
            "docker_translation",
            "medium",
            commands,
            unsupported=unsupported + ["container build support: verify before use"],
        )

    if sub == "compose" and len(parts) >= 3 and parts[2] == "up":
        return record(
            input_text,
            "compose_like_service",
            "medium",
            ["Decompose compose services into explicit container image, env, port, mount, and dependency plans."],
            requires_confirmation=True,
            unsupported=["full Docker Compose parity is not guaranteed"],
            notes=["Ask for the compose file or service definitions, then plan service-by-service operations."],
        )

    return record(input_text, "unknown", "low", [], unsupported=parts[1:])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="*", help="Docker-style command string or argv")
    args = parser.parse_args(argv)
    input_text, parts = read_input(args.command)
    print(json.dumps(translate(input_text, parts), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
