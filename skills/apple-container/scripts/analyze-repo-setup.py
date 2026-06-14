#!/usr/bin/env python3
"""Statically analyze a repository for Apple container setup planning."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Any


COMPOSE_NAMES = {
    "compose.yaml",
    "compose.yml",
    "docker-compose.yaml",
    "docker-compose.yml",
}

PACKAGE_HINTS = {
    "package.json": "node",
    "pnpm-lock.yaml": "node",
    "yarn.lock": "node",
    "package-lock.json": "node",
    "pyproject.toml": "python",
    "requirements.txt": "python",
    "Pipfile": "python",
    "go.mod": "go",
    "Cargo.toml": "rust",
    "Gemfile": "ruby",
    "pom.xml": "java",
    "build.gradle": "java",
    "Makefile": "make",
}

ENV_EXAMPLE_NAMES = {
    ".env.example",
    ".env.sample",
    ".env.template",
    "env.example",
    "env.sample",
}


def is_url(value: str) -> bool:
    return bool(re.match(r"^(https?|git|ssh)://", value)) or value.startswith("git@")


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def read_text(path: Path, limit: int = 120_000) -> str:
    try:
        data = path.read_bytes()[:limit]
    except OSError:
        return ""
    return data.decode("utf-8", errors="replace")


def find_files(root: Path) -> dict[str, list[str]]:
    found: dict[str, list[str]] = {
        "dockerfiles": [],
        "compose_files": [],
        "env_examples": [],
        "readmes": [],
        "package_files": [],
    }
    ignored_dirs = {".git", "node_modules", "vendor", ".venv", "dist", "build", "target"}

    for current, dirs, files in os.walk(root):
        dirs[:] = [name for name in dirs if name not in ignored_dirs]
        current_path = Path(current)
        for name in files:
            path = current_path / name
            lower = name.lower()
            if name == "Dockerfile" or name == "Containerfile" or name.endswith(".Dockerfile"):
                found["dockerfiles"].append(rel(path, root))
            if lower in COMPOSE_NAMES:
                found["compose_files"].append(rel(path, root))
            if name in ENV_EXAMPLE_NAMES or name.endswith(".env.example") or name.endswith(".env.sample"):
                found["env_examples"].append(rel(path, root))
            if lower.startswith("readme"):
                found["readmes"].append(rel(path, root))
            if name in PACKAGE_HINTS:
                found["package_files"].append(rel(path, root))

    return {key: sorted(values) for key, values in found.items()}


def extract_exposed_ports(root: Path, dockerfiles: list[str], readmes: list[str]) -> list[str]:
    ports: set[str] = set()
    for item in dockerfiles:
        text = read_text(root / item)
        for match in re.finditer(r"(?im)^\s*EXPOSE\s+(.+)$", text):
            for token in match.group(1).split():
                ports.add(token.strip())
    for item in readmes[:3]:
        text = read_text(root / item, limit=80_000)
        for match in re.finditer(r"\b(?:localhost|127\.0\.0\.1):(\d{2,5})\b", text):
            ports.add(match.group(1))
    return sorted(ports)


def extract_env_keys(root: Path, env_examples: list[str], dockerfiles: list[str]) -> list[str]:
    keys: set[str] = set()
    for item in env_examples:
        text = read_text(root / item)
        for line in text.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key = stripped.split("=", 1)[0].strip()
            if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
                keys.add(key)
    for item in dockerfiles:
        text = read_text(root / item)
        for match in re.finditer(r"(?im)^\s*(?:ARG|ENV)\s+([A-Za-z_][A-Za-z0-9_]*)", text):
            keys.add(match.group(1))
    return sorted(keys)


def detect_runtimes(package_files: list[str]) -> list[str]:
    runtimes = {PACKAGE_HINTS[Path(item).name] for item in package_files if Path(item).name in PACKAGE_HINTS}
    return sorted(runtimes)


def record_url(source: str) -> dict[str, Any]:
    return {
        "input": source,
        "input_type": "url",
        "intent": "github_project_setup",
        "confidence": "medium",
        "detected": {
            "dockerfiles": [],
            "compose_files": [],
            "env_examples": [],
            "readmes": [],
            "package_files": [],
            "runtimes": [],
            "exposed_ports": [],
            "env_keys": [],
        },
        "apple_container_workflow": [
            "Clone or otherwise fetch the repository only after the user approves the target location.",
            "Run static repository analysis on the local checkout.",
            "Verify Apple container CLI help before build or run commands.",
        ],
        "requires_confirmation": True,
        "confirmation_questions": [
            "Where should the repository be cloned or checked out?",
            "Which branch, tag, or commit should be used if not the default branch?",
            "After analysis, confirm service, env vars, ports, mounts, image tag, and command before running containers.",
        ],
        "unsupported_or_uncertain": [
            "Repository contents are not available until cloned or supplied as a local path.",
        ],
        "notes": [
            "Do not execute installer, build, package-manager, or container commands from a URL alone.",
        ],
    }


def analyze_path(path: Path) -> dict[str, Any]:
    root = path.resolve()
    found = find_files(root)
    dockerfiles = found["dockerfiles"]
    compose_files = found["compose_files"]
    env_examples = found["env_examples"]
    package_files = found["package_files"]
    readmes = found["readmes"]
    env_keys = extract_env_keys(root, env_examples, dockerfiles)
    ports = extract_exposed_ports(root, dockerfiles, readmes)
    runtimes = detect_runtimes(package_files)

    workflow = ["Inspect detected repository files before choosing commands."]
    confirmations: list[str] = []
    uncertain: list[str] = []

    if dockerfiles:
        workflow.append("Verify container build support with `container build --help` before building an image.")
        confirmations.append("Confirm image name/tag and any build args, target, platform, or secrets before building.")
        uncertain.append("container build support and Dockerfile feature parity must be verified locally.")
    else:
        confirmations.append("Confirm whether to use an existing registry image or add a Dockerfile/Containerfile.")

    if compose_files:
        workflow.append("Decompose Compose services into explicit Apple container service plans.")
        confirmations.append("Confirm which Compose service or services to run.")
        uncertain.append("Full Docker Compose parity is not guaranteed.")

    if env_keys:
        confirmations.append("Confirm runtime values for detected environment variables.")

    if ports:
        confirmations.append("Confirm host port mappings for detected application ports.")
    else:
        confirmations.append("Confirm which host ports, if any, should be exposed.")

    confirmations.append("Confirm container name, startup command, working directory, and persistent data mounts.")

    if not dockerfiles and not compose_files:
        uncertain.append("No Dockerfile or Compose file detected; containerization path must be inferred from project runtime files.")

    if not runtimes and not dockerfiles and not compose_files:
        uncertain.append("No common runtime metadata detected.")

    return {
        "input": str(path),
        "input_type": "local_path",
        "intent": "github_project_setup",
        "confidence": "high" if dockerfiles or compose_files or package_files else "low",
        "detected": {
            **found,
            "runtimes": runtimes,
            "exposed_ports": ports,
            "env_keys": env_keys,
        },
        "apple_container_workflow": workflow,
        "requires_confirmation": True,
        "confirmation_questions": confirmations,
        "unsupported_or_uncertain": uncertain,
        "notes": [
            "Static analysis only; no dependencies, builds, or containers were run.",
            "Use local Apple container help as the source of truth before execution.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", help="GitHub/repository URL or local repository path")
    args = parser.parse_args(argv)

    source = args.source
    if is_url(source):
        print(json.dumps(record_url(source), indent=2, sort_keys=True))
        return 0

    path = Path(source)
    if not path.exists() or not path.is_dir():
        print(f"not a repository directory or URL: {source}", file=sys.stderr)
        return 2

    print(json.dumps(analyze_path(path), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
