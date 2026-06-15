#!/usr/bin/env python3
"""Statically analyze a repository for Apple container setup planning."""

from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import shutil
import socket
import subprocess
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


def clean_scalar(value: str) -> str:
    value = value.strip()
    if value in {"", "null", "Null", "NULL", "~"}:
        return ""
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def strip_inline_comment(line: str) -> str:
    quote: str | None = None
    escaped = False
    for index, char in enumerate(line):
        if escaped:
            escaped = False
            continue
        if char == "\\":
            escaped = True
            continue
        if quote:
            if char == quote:
                quote = None
            continue
        if char in {"'", '"'}:
            quote = char
            continue
        if char == "#" and (index == 0 or line[index - 1].isspace()):
            return line[:index]
    return line


def split_mapping(line: str) -> tuple[str, str] | None:
    if ":" not in line:
        return None
    key, value = line.split(":", 1)
    key = clean_scalar(key)
    if not key:
        return None
    return key, clean_scalar(value)


def parse_env_item(value: str) -> tuple[str, str | None] | None:
    value = clean_scalar(value)
    if not value:
        return None
    if "=" in value:
        key, env_value = value.split("=", 1)
        key = key.strip()
        if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
            return key, env_value
        return None
    if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", value):
        return value, None
    return None


def new_compose_service() -> dict[str, Any]:
    return {
        "image": "",
        "build": {},
        "ports": [],
        "environment": {},
        "volumes": [],
        "depends_on": [],
        "healthcheck": False,
        "restart": "",
        "command": "",
        "entrypoint": "",
        "working_dir": "",
    }


def parse_compose_file(path: Path) -> dict[str, Any]:
    """Parse the conservative Compose subset needed for setup planning.

    This intentionally avoids a YAML dependency. Unknown fields are ignored rather
    than guessed, and the result is only used for planning/confirmation.
    """

    services: dict[str, dict[str, Any]] = {}
    named_volumes: list[str] = []
    text = read_text(path)
    in_services = False
    in_top_volumes = False
    current_service: str | None = None
    current_key: str | None = None
    current_build_key: str | None = None
    current_depends_mode = False

    for raw_line in text.splitlines():
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        line = strip_inline_comment(raw_line).rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()

        if indent == 0:
            key = stripped.rstrip(":")
            in_services = key == "services"
            in_top_volumes = key == "volumes"
            current_service = None
            current_key = None
            current_build_key = None
            current_depends_mode = False
            continue

        if in_services and indent == 2 and stripped.endswith(":"):
            current_service = clean_scalar(stripped[:-1])
            services[current_service] = new_compose_service()
            current_key = None
            current_build_key = None
            current_depends_mode = False
            continue

        if in_top_volumes and indent == 2 and stripped.endswith(":"):
            named_volumes.append(clean_scalar(stripped[:-1]))
            continue

        if not in_services or not current_service:
            continue

        service = services[current_service]
        if indent == 4:
            current_build_key = None
            current_depends_mode = False
            mapping = split_mapping(stripped)
            if not mapping:
                continue
            key, value = mapping
            current_key = key
            if key == "image":
                service["image"] = value
            elif key == "build":
                if value:
                    service["build"]["context"] = value
                else:
                    service["build"].setdefault("context", ".")
            elif key == "ports":
                pass
            elif key == "volumes":
                pass
            elif key == "environment":
                pass
            elif key == "depends_on":
                current_depends_mode = True
                if value:
                    service["depends_on"].append(value)
            elif key == "healthcheck":
                service["healthcheck"] = True
            elif key == "restart":
                service["restart"] = value
            elif key == "command":
                service["command"] = value
            elif key == "entrypoint":
                service["entrypoint"] = value
            elif key in {"working_dir", "workdir"}:
                service["working_dir"] = value
            continue

        if indent >= 6 and current_key == "build":
            if stripped.startswith("- "):
                continue
            mapping = split_mapping(stripped)
            if not mapping:
                continue
            key, value = mapping
            if key == "args":
                current_build_key = "args"
                service["build"].setdefault("args", {})
            elif current_build_key == "args":
                service["build"].setdefault("args", {})[key] = value
            else:
                service["build"][key] = value
            continue

        if indent >= 6 and current_key in {"ports", "volumes"} and stripped.startswith("- "):
            value = clean_scalar(stripped[2:])
            if value:
                service[current_key].append(value)
            continue

        if indent >= 6 and current_key == "environment":
            if stripped.startswith("- "):
                item = parse_env_item(stripped[2:])
                if item:
                    key, value = item
                    service["environment"][key] = value
                continue
            mapping = split_mapping(stripped)
            if mapping:
                key, value = mapping
                if re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", key):
                    service["environment"][key] = value
            continue

        if indent >= 6 and current_key == "depends_on":
            if stripped.startswith("- "):
                dep = clean_scalar(stripped[2:])
                if dep:
                    service["depends_on"].append(dep)
                continue
            mapping = split_mapping(stripped)
            if mapping and current_depends_mode and indent == 6:
                dep, _ = mapping
                service["depends_on"].append(dep)

    for service in services.values():
        service["depends_on"] = sorted(set(service["depends_on"]))

    return {
        "path": path.name,
        "services": services,
        "named_volumes": sorted(set(named_volumes)),
    }


def parse_compose_files(root: Path, compose_files: list[str]) -> list[dict[str, Any]]:
    return [parse_compose_file(root / item) for item in compose_files]


def compose_host_port(port_spec: str) -> str:
    spec = clean_scalar(port_spec)
    if not spec:
        return ""
    spec = spec.split("/", 1)[0]
    parts = spec.split(":")
    if len(parts) == 1:
        return ""
    if len(parts) == 2:
        return parts[0]
    return parts[-2]


def compose_container_port(port_spec: str) -> str:
    spec = clean_scalar(port_spec)
    if not spec:
        return ""
    spec = spec.split("/", 1)[0]
    return spec.split(":")[-1]


def compose_volume_name(volume_spec: str) -> str:
    spec = clean_scalar(volume_spec)
    if not spec or ":" not in spec:
        return ""
    source = spec.split(":", 1)[0]
    if source.startswith((".", "/", "~", "$")):
        return ""
    return source


def build_service_plans(compose_details: list[dict[str, Any]]) -> list[dict[str, Any]]:
    plans: list[dict[str, Any]] = []
    for compose in compose_details:
        service_names = set(compose["services"].keys())
        for name, service in compose["services"].items():
            run_notes: list[str] = []
            service_name_env_references: list[dict[str, str]] = []
            if service["build"]:
                run_notes.append("build image before run")
            if service["depends_on"]:
                run_notes.append("start dependencies first and wait for readiness manually")
            if service["healthcheck"]:
                run_notes.append("healthcheck exists; Apple container orchestration must wait explicitly")
            if service["restart"]:
                run_notes.append("restart policy requires verification or an external supervisor")
            for env_key, env_value in service["environment"].items():
                if not env_value:
                    continue
                for candidate in service_names:
                    if env_value_references_service(env_value, candidate):
                        service_name_env_references.append(
                            {"env": env_key, "value": env_value, "service": candidate}
                        )
            if service_name_env_references:
                run_notes.append("environment references Compose service names; verify Apple container DNS or provide an explicit host")

            plans.append(
                {
                    "service": name,
                    "source": "build" if service["build"] else "image" if service["image"] else "unknown",
                    "image": service["image"],
                    "build": service["build"],
                    "ports": [
                        {
                            "compose": port,
                            "host": compose_host_port(port),
                            "container": compose_container_port(port),
                        }
                        for port in service["ports"]
                    ],
                    "environment_keys": sorted(service["environment"].keys()),
                    "environment_values": service["environment"],
                    "volumes": service["volumes"],
                    "named_volume_sources": sorted(
                        value for value in {compose_volume_name(item) for item in service["volumes"]} if value
                    ),
                    "depends_on": service["depends_on"],
                    "healthcheck": service["healthcheck"],
                    "restart": service["restart"],
                    "service_name_env_references": service_name_env_references,
                    "run_notes": run_notes,
                }
            )
    return plans


def compose_env_keys(compose_details: list[dict[str, Any]]) -> list[str]:
    keys: set[str] = set()
    for compose in compose_details:
        for service in compose["services"].values():
            keys.update(service["environment"].keys())
    return sorted(keys)


def command_stdout(command: list[str]) -> str:
    try:
        result = subprocess.run(command, check=False, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
    except OSError:
        return ""
    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def detect_docker_compose_state(project_name: str, service_plans: list[dict[str, Any]]) -> dict[str, Any]:
    state: dict[str, Any] = {"containers": {}, "volumes": {}}
    if not shutil.which("docker"):
        return state

    for plan in service_plans:
        container_name = f"{project_name}-{plan['service']}-1"
        inspect = command_stdout(
            ["docker", "inspect", container_name, "--format", "{{.Name}} {{.State.Status}}"]
        )
        if inspect:
            state["containers"][plan["service"]] = {
                "name": container_name,
                "status": inspect.split()[-1],
            }
        for source in plan["named_volume_sources"]:
            volume_name = f"{project_name}_{source}"
            inspect_volume = command_stdout(
                ["docker", "volume", "inspect", volume_name, "--format", "{{.Name}}"]
            )
            if inspect_volume:
                state["volumes"][source] = {
                    "name": volume_name,
                    "service": plan["service"],
                }
    return state


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "app"


def env_value_references_service(value: str, service_name: str) -> bool:
    if value == service_name:
        return True
    if re.search(rf"://{re.escape(service_name)}(?::|/|$)", value):
        return True
    if re.search(rf"@{re.escape(service_name)}(?::|/|$)", value):
        return True
    if re.search(rf"(^|[;, ]){re.escape(service_name)}:\d+", value):
        return True
    return False


def replace_service_reference(value: str, service_name: str, replacement: str) -> str:
    if value == service_name:
        return replacement
    value = re.sub(rf"(://){re.escape(service_name)}(?=[:/]|$)", rf"\1{replacement}", value)
    value = re.sub(rf"(@){re.escape(service_name)}(?=[:/]|$)", rf"\1{replacement}", value)
    value = re.sub(rf"(^|[;, ]){re.escape(service_name)}(?=:\d+)", rf"\1{replacement}", value)
    return value


def default_env_value(key: str, value: str | None) -> str:
    if value is None:
        return f"${{{key}}}"
    match = re.fullmatch(r"\$\{([A-Za-z_][A-Za-z0-9_]*):-([^}]*)\}", value)
    if match:
        return match.group(2)
    return value


def service_container_name(project_name: str, service_name: str) -> str:
    return f"{project_name}-{slugify(service_name)}"


def shell_join(parts: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def shell_double_quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"').replace("`", "\\`") + '"'


def shell_env_assignment(key: str, value: str) -> str:
    assignment = f"{key}={value}"
    if re.search(r"\$\{[A-Za-z_][A-Za-z0-9_]*\}", value):
        return shell_double_quote(assignment)
    return shlex.quote(assignment)


def image_tag_for_service(project_name: str, service_name: str) -> str:
    return f"{project_name}-{slugify(service_name)}:apple-container"


def ordered_service_plans(service_plans: list[dict[str, Any]]) -> list[dict[str, Any]]:
    plans = {plan["service"]: plan for plan in service_plans}
    ordered: list[dict[str, Any]] = []
    temporary: set[str] = set()
    permanent: set[str] = set()

    def visit(name: str) -> None:
        if name in permanent:
            return
        if name in temporary:
            return
        temporary.add(name)
        for dependency in plans.get(name, {}).get("depends_on", []):
            if dependency in plans:
                visit(dependency)
        temporary.remove(name)
        permanent.add(name)
        if name in plans:
            ordered.append(plans[name])

    for plan in service_plans:
        visit(plan["service"])
    return ordered


def make_run_command(
    project_name: str,
    plan: dict[str, Any],
    env_overrides: dict[str, str],
    host_port_overrides: dict[str, str] | None = None,
) -> str:
    name = service_container_name(project_name, plan["service"])
    network = f"{project_name}-net"
    image = plan["image"] or image_tag_for_service(project_name, plan["service"])
    parts = ["container", "run", "-d", "--name", name, "--network", network]
    host_port_overrides = host_port_overrides or {}

    for port in plan["ports"]:
        host = host_port_overrides.get(plan["service"], port["host"] or "<choose-host-port>")
        container_port = port["container"] or "<container-port>"
        parts.extend(["-p", f"127.0.0.1:{host}:{container_port}"])
    for volume in plan["volumes"]:
        source = compose_volume_name(volume)
        target = volume.split(":", 1)[1] if ":" in volume else ""
        if source and target:
            parts.extend(["-v", f"{project_name}-{slugify(source)}:{target}"])
        elif volume:
            parts.extend(["-v", volume])
    rendered = [shlex.quote(part) for part in parts]
    for key in sorted(env_overrides):
        rendered.extend(["-e", shell_env_assignment(key, env_overrides[key])])
    rendered.append(shlex.quote(image))
    return " ".join(rendered)


def make_build_command(root: Path, project_name: str, plan: dict[str, Any]) -> str:
    build = plan["build"]
    context = build.get("context") or "."
    dockerfile = build.get("dockerfile")
    context_path = root / context if not Path(context).is_absolute() else Path(context)
    parts = ["container", "build", "-t", image_tag_for_service(project_name, plan["service"])]
    if dockerfile:
        parts.extend(["-f", str((root / dockerfile).resolve() if not Path(dockerfile).is_absolute() else dockerfile)])
    for key, value in sorted(build.get("args", {}).items()):
        parts.extend(["--build-arg", f"{key}={default_env_value(key, value)}"])
    parts.append(str(context_path.resolve()))
    return shell_join(parts)


def port_is_available(port: str) -> bool:
    if not port.isdigit():
        return False
    checks = [(socket.AF_INET, "127.0.0.1")]
    if socket.has_ipv6:
        checks.append((socket.AF_INET6, "::1"))
    for family, host in checks:
        with socket.socket(family, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((host, int(port)))
            except OSError:
                return False
    return True


def choose_host_port(preferred: str) -> tuple[str, str]:
    if not preferred or not preferred.isdigit():
        return preferred, "no preferred host port detected"
    if port_is_available(preferred):
        return preferred, "preferred host port is available"
    start = int(preferred)
    for candidate in range(start + 1, start + 51):
        if port_is_available(str(candidate)):
            return str(candidate), f"preferred host port {preferred} is unavailable; selected next available port"
    return preferred, f"preferred host port {preferred} is unavailable and no nearby free port was found"


def postgres_migration_command(source_container: str, target_container: str, user: str, database: str) -> str:
    return (
        f"SOURCE_WAS_RUNNING=$(docker inspect -f '{{{{.State.Running}}}}' {shlex.quote(source_container)} "
        "2>/dev/null || printf false); "
        'if [ "$SOURCE_WAS_RUNNING" != "true" ]; then '
        f"docker start {shlex.quote(source_container)} >/dev/null; fi; "
        "source_ready=0; "
        f"for i in $(seq 1 30); do if docker exec {shlex.quote(source_container)} "
        f"pg_isready -U {shlex.quote(user)} -d {shlex.quote(database)}; then source_ready=1; break; fi; "
        "sleep 2; done; "
        'if [ "$source_ready" != 1 ]; then '
        f"docker logs {shlex.quote(source_container)}; exit 1; fi; "
        f"docker exec {shlex.quote(source_container)} pg_dump -U {shlex.quote(user)} -d {shlex.quote(database)} "
        "--clean --if-exists --no-owner --no-privileges | "
        f"container exec -i {shlex.quote(target_container)} psql -U {shlex.quote(user)} -d {shlex.quote(database)}; "
        'if [ "$SOURCE_WAS_RUNNING" != "true" ]; then '
        f"docker stop {shlex.quote(source_container)} >/dev/null; fi"
    )


def build_recommended_solution(root: Path, service_plans: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not service_plans:
        return None

    project_name = slugify(root.name)
    ordered = ordered_service_plans(service_plans)
    docker_state = detect_docker_compose_state(project_name, ordered)
    resource_names = {
        "network": f"{project_name}-net",
        "containers": {
            plan["service"]: service_container_name(project_name, plan["service"]) for plan in ordered
        },
        "images": {
            plan["service"]: image_tag_for_service(project_name, plan["service"])
            for plan in ordered
            if plan["source"] == "build"
        },
        "volumes": {},
    }
    for plan in ordered:
        for source in plan["named_volume_sources"]:
            resource_names["volumes"][source] = f"{project_name}-{slugify(source)}"

    commands: list[dict[str, Any]] = []
    assumptions: list[str] = [
        "Use isolated Apple container resource names derived from the repository directory.",
        "Bind published application ports to 127.0.0.1 by default for local development.",
        "Use detected Compose default environment values when present.",
        "Disable or externalize Compose restart semantics unless a supervisor is added.",
    ]
    dynamic_values: list[dict[str, str]] = []
    verification: list[dict[str, str]] = []
    port_recommendations: dict[str, list[dict[str, str]]] = {}
    host_port_overrides: dict[str, str] = {}
    data_migration: dict[str, Any] = {
        "strategy": "fresh-empty-volumes",
        "detected_source": docker_state,
        "included_in_shell_script": False,
        "commands": [],
        "warnings": [
            "Without data migration, Apple container named volumes start empty and the application may only have seed data.",
        ],
    }

    commands.append(
        {
            "id": "create-network",
            "phase": "prepare",
            "command": (
                f"container network inspect {shlex.quote(resource_names['network'])} >/dev/null 2>&1 "
                f"|| container network create {shlex.quote(resource_names['network'])}"
            ),
            "reason": "Create an isolated network for the migrated Compose services.",
            "idempotency": "Skip if the network already exists.",
        }
    )
    for compose_volume, apple_volume in resource_names["volumes"].items():
        commands.append(
            {
                "id": f"create-volume-{slugify(compose_volume)}",
                "phase": "prepare",
                "command": (
                    f"container volume inspect {shlex.quote(apple_volume)} >/dev/null 2>&1 "
                    f"|| container volume create {shlex.quote(apple_volume)}"
                ),
                "reason": f"Preserve Compose named volume `{compose_volume}` as Apple container volume `{apple_volume}`.",
                "idempotency": "Skip if the volume already exists.",
            }
        )

    for plan in ordered:
        if plan["ports"]:
            port_recommendations[plan["service"]] = []
            for port in plan["ports"]:
                selected, reason = choose_host_port(port["host"])
                port_recommendations[plan["service"]].append(
                    {
                        "compose": port["compose"],
                        "detected_host": port["host"],
                        "recommended_host": selected,
                        "container": port["container"],
                        "reason": reason,
                    }
                )
                if selected and selected != port["host"]:
                    host_port_overrides[plan["service"]] = selected

        if plan["source"] == "build":
            commands.append(
                {
                    "id": f"build-{slugify(plan['service'])}",
                    "phase": "build",
                    "command": make_build_command(root, project_name, plan),
                    "reason": f"Build the local image for Compose service `{plan['service']}`.",
                }
            )

    service_ip_placeholders: dict[str, str] = {}
    for plan in ordered:
        for ref in plan["service_name_env_references"]:
            placeholder = service_ip_placeholders.setdefault(
                ref["service"],
                f"${{{service_container_name(project_name, ref['service']).upper().replace('-', '_')}_IP}}",
            )
            dynamic_values.append(
                {
                    "name": placeholder.strip("${}"),
                    "source_service": ref["service"],
                    "consumer_service": plan["service"],
                    "env": ref["env"],
                    "reason": "Apple container service-name DNS must be verified; use inspected dependency IP as the conservative fallback.",
                    "command": (
                        f"{placeholder.strip('${}')}=$(container inspect "
                        f"{shlex.quote(service_container_name(project_name, ref['service']))} "
                        "| python3 -c 'import json,sys; data=json.load(sys.stdin); "
                        "print(data[0][\"status\"][\"networks\"][0][\"ipv4Address\"].split(\"/\")[0])')"
                    ),
                }
            )

    compose_service_lookup: dict[str, dict[str, Any]] = {plan["service"]: plan for plan in ordered}
    for plan in ordered:
        env_values: dict[str, str] = {}
        service_env = plan.get("environment_values", {})
        for key, value in service_env.items():
            env_values[key] = default_env_value(key, value)
        if (
            plan["service"] == "app"
            and env_values.get("SMM_SYNC_ENABLED", "").lower() == "true"
            and not env_values.get("ALU_CHANGJIANG_PRICE_URL")
            and not (env_values.get("SMM_PRICE_URL") and env_values.get("SMM_COOKIE"))
        ):
            env_values["SMM_SYNC_ENABLED"] = "false"
            assumptions.append("Disable SMM sync in the recommended local plan when no SMM/ALU source credentials are configured.")
        for ref in plan["service_name_env_references"]:
            replacement = service_ip_placeholders.get(ref["service"], ref["value"])
            env_values[ref["env"]] = replace_service_reference(ref["value"], ref["service"], replacement)

        for dependency in plan["depends_on"]:
            if dependency in service_ip_placeholders:
                placeholder_name = service_ip_placeholders[dependency].strip("${}")
                commands.append(
                    {
                        "id": f"resolve-{slugify(dependency)}-ip-for-{slugify(plan['service'])}",
                        "phase": "resolve",
                        "command": next(
                            item["command"] for item in dynamic_values if item["name"] == placeholder_name
                        ),
                        "reason": f"Resolve dependency `{dependency}` IP before running `{plan['service']}`.",
                    }
                )

        commands.append(
            {
                "id": f"run-{slugify(plan['service'])}",
                "phase": "run",
                "command": make_run_command(project_name, plan, env_values, host_port_overrides),
                "reason": f"Run service `{plan['service']}` with detected env, ports, volumes, and network.",
                "depends_on": [
                    f"run-{slugify(dep)}" for dep in plan["depends_on"] if dep in compose_service_lookup
                ],
            }
        )
        if plan.get("healthcheck"):
            readiness_command = f"container logs {service_container_name(project_name, plan['service'])}"
            if plan["image"].startswith("postgres:"):
                user = default_env_value("POSTGRES_USER", plan.get("environment_values", {}).get("POSTGRES_USER", "postgres"))
                database = default_env_value("POSTGRES_DB", plan.get("environment_values", {}).get("POSTGRES_DB", user))
                readiness_command = (
                    "ready=0; "
                    f"for i in $(seq 1 30); do "
                    f"if container exec {shlex.quote(service_container_name(project_name, plan['service']))} "
                    f"pg_isready -U {shlex.quote(user)} -d {shlex.quote(database)}; then ready=1; break; fi; "
                    "sleep 2; done; "
                    'if [ "$ready" != 1 ]; then '
                    f"container logs {shlex.quote(service_container_name(project_name, plan['service']))}; exit 1; fi"
                )
            commands.append(
                {
                    "id": f"wait-{slugify(plan['service'])}",
                    "phase": "wait",
                    "command": readiness_command,
                    "reason": "Inspect logs or run service-specific readiness checks before starting dependents.",
                }
            )
        if plan["image"].startswith("postgres:") and plan["service"] in docker_state["containers"]:
            user = default_env_value("POSTGRES_USER", plan.get("environment_values", {}).get("POSTGRES_USER", "postgres"))
            database = default_env_value("POSTGRES_DB", plan.get("environment_values", {}).get("POSTGRES_DB", user))
            source_container = docker_state["containers"][plan["service"]]["name"]
            target_container = service_container_name(project_name, plan["service"])
            migration = {
                "id": f"migrate-data-{slugify(plan['service'])}",
                "phase": "migrate-data",
                "command": postgres_migration_command(source_container, target_container, user, database),
                "reason": (
                    f"Migrate PostgreSQL database `{database}` from Docker/OrbStack container "
                    f"`{source_container}` into Apple container `{target_container}` before dependents start."
                ),
                "destructive_to_target": True,
            }
            commands.append(migration)
            data_migration = {
                "strategy": "postgres-dump-restore-from-docker-compose",
                "detected_source": docker_state,
                "included_in_shell_script": True,
                "commands": [migration],
                "warnings": [
                    "Restoring with pg_dump --clean overwrites matching objects in the target Apple container database.",
                    "Run this only before using the target Apple container database, or after explicitly approving replacement.",
                ],
            }

    first_web = next((plan for plan in ordered if plan["ports"]), None)
    if first_web:
        host = host_port_overrides.get(first_web["service"], first_web["ports"][0]["host"] or "<choose-host-port>")
        verification.append(
            {
                "id": "http-check",
                "command": f"curl -fsS -I http://localhost:{host}/login || curl -fsS -I http://localhost:{host}/",
                "success": "HTTP responds from the published application port.",
            }
        )
    verification.append(
        {
            "id": "container-list",
            "command": "container list --all",
            "success": "Expected Apple container services are present and application services are running.",
        }
    )

    approval_text = (
        "Use the recommended Apple container plan: build local images, create isolated network and volumes, "
        "start dependencies first, inspect dependency IPs for Compose service-name replacements, run dependents, "
        "and verify HTTP access."
    )
    shell_script_lines = ["set -euo pipefail"]
    shell_script_lines.extend(command["command"] for command in commands)
    shell_script_lines.extend(item["command"] for item in verification)
    return {
        "strategy": "compose-to-apple-container-explicit-plan",
        "confidence": "medium",
        "approval_text": approval_text,
        "resource_names": resource_names,
        "ports": port_recommendations,
        "assumptions": assumptions,
        "data_migration": data_migration,
        "dynamic_values": dynamic_values,
        "commands": commands,
        "shell_script": "\n".join(shell_script_lines),
        "verification": verification,
        "remaining_confirmations": [
            "Confirm replacing existing Apple container resources if names already exist.",
            "Confirm any sensitive environment variable values that were empty in Compose.",
            "Confirm host port changes if the detected port is already in use.",
            "Confirm target database replacement before running included data migration commands.",
        ],
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
    ports = extract_exposed_ports(root, dockerfiles, readmes)
    runtimes = detect_runtimes(package_files)
    compose_details = parse_compose_files(root, compose_files)
    service_plans = build_service_plans(compose_details)
    recommended_solution = build_recommended_solution(root, service_plans)
    env_keys = sorted(set(extract_env_keys(root, env_examples, dockerfiles)) | set(compose_env_keys(compose_details)))

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
        service_names = sorted({plan["service"] for plan in service_plans})
        if service_names:
            confirmations.append(f"Confirm which Compose services to run: {', '.join(service_names)}.")
        else:
            confirmations.append("Confirm which Compose service or services to run.")
        uncertain.append("Full Docker Compose parity is not guaranteed.")
        if any(plan["depends_on"] for plan in service_plans):
            workflow.append("Create/start dependency services before dependents and wait for readiness outside Compose.")
            uncertain.append("Compose depends_on and healthcheck ordering must be replaced by explicit waits.")
        if any(plan["service_name_env_references"] for plan in service_plans):
            workflow.append("Replace Compose service-name DNS assumptions with a help-verified Apple container networking plan.")
            uncertain.append("Compose service names in environment variables may not resolve automatically under Apple container.")
        if any(plan["named_volume_sources"] for plan in service_plans):
            workflow.append("Create Apple container volumes for detected named Compose volumes before running services.")
        if any(plan["ports"] for plan in service_plans):
            workflow.append("Map detected Compose host/container ports with help-verified `container run --publish`.")
        if any(plan["run_notes"] for plan in service_plans):
            uncertain.append("Compose restart policies, healthchecks, and dependency semantics need explicit Apple container handling.")

    if env_keys:
        confirmations.append("Confirm runtime values for detected environment variables.")
    for plan in service_plans:
        if plan["environment_keys"]:
            confirmations.append(
                f"Confirm runtime environment for service `{plan['service']}`: {', '.join(plan['environment_keys'])}."
            )
        if plan["service_name_env_references"]:
            refs = ", ".join(
                f"{item['env']}={item['value']} references `{item['service']}`"
                for item in plan["service_name_env_references"]
            )
            confirmations.append(
                f"Confirm Apple container service-discovery replacement for service `{plan['service']}`: {refs}."
            )

    if ports:
        confirmations.append("Confirm host port mappings for detected application ports.")
    else:
        confirmations.append("Confirm which host ports, if any, should be exposed.")
    for plan in service_plans:
        if plan["ports"]:
            mappings = ", ".join(
                f"{item['host'] or '<choose-host>'}->{item['container']}" for item in plan["ports"]
            )
            confirmations.append(f"Confirm host port mapping for service `{plan['service']}`: {mappings}.")
        if plan["named_volume_sources"]:
            confirmations.append(
                f"Confirm Apple container volume mapping for service `{plan['service']}`: "
                + ", ".join(plan["named_volume_sources"])
                + "."
            )

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
            "compose": compose_details,
            "service_plans": service_plans,
        },
        "apple_container_workflow": workflow,
        "recommended_solution": recommended_solution,
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
