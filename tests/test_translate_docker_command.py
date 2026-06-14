import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "apple-container" / "scripts" / "translate-docker-command.py"
REPO_ANALYZER = ROOT / "skills" / "apple-container" / "scripts" / "analyze-repo-setup.py"
INSTALL_SCRIPT = ROOT / "skills" / "apple-container" / "scripts" / "install-container.sh"
UPDATE_SCRIPT = ROOT / "skills" / "apple-container" / "scripts" / "update-skill.sh"


def translate(command):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), command],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return json.loads(result.stdout)


def analyze_repo(source):
    result = subprocess.run(
        [sys.executable, str(REPO_ANALYZER), str(source)],
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    )
    return json.loads(result.stdout)


class TranslateDockerCommandTests(unittest.TestCase):
    def assert_shape(self, data):
        self.assertIn("input", data)
        self.assertIn("intent", data)
        self.assertIn("confidence", data)
        self.assertIsInstance(data["apple_container_commands"], list)
        self.assertIsInstance(data["requires_confirmation"], bool)
        self.assertIsInstance(data["unsupported_or_uncertain"], list)
        self.assertIsInstance(data["notes"], list)

    def test_fixture_commands_have_json_shape(self):
        commands = json.loads((ROOT / "tests" / "fixtures" / "docker_commands.json").read_text())
        for command in commands:
            with self.subTest(command=command):
                self.assert_shape(translate(command))

    def test_docker_ps(self):
        data = translate("docker ps")
        self.assertEqual(data["intent"], "list_containers")
        self.assertFalse(data["requires_confirmation"])

    def test_docker_images(self):
        data = translate("docker images")
        self.assertEqual(data["intent"], "list_images")

    def test_docker_pull_redis(self):
        data = translate("docker pull redis")
        self.assertEqual(data["intent"], "pull_image")
        self.assertIn("container image pull redis", data["apple_container_commands"])

    def test_docker_run_redis(self):
        data = translate("docker run redis")
        self.assertEqual(data["intent"], "run_container")
        self.assertFalse(data["requires_confirmation"])

    def test_docker_run_name_and_port_are_uncertain(self):
        data = translate("docker run --name redis -p 6379:6379 redis")
        self.assertEqual(data["intent"], "run_container")
        joined = " ".join(data["unsupported_or_uncertain"])
        self.assertIn("--name", joined)
        self.assertIn("port mapping", joined)

    def test_docker_run_env_is_uncertain(self):
        data = translate("docker run -e POSTGRES_PASSWORD=pass postgres")
        self.assertEqual(data["intent"], "run_container")
        self.assertIn("environment flag", " ".join(data["unsupported_or_uncertain"]))

    def test_docker_logs_follow(self):
        data = translate("docker logs -f app")
        self.assertEqual(data["intent"], "view_logs")
        self.assertIn("follow logs flag", " ".join(data["unsupported_or_uncertain"]))

    def test_docker_exec_shell(self):
        data = translate("docker exec -it app sh")
        self.assertEqual(data["intent"], "exec_shell")
        self.assertIn("TTY/interactive", " ".join(data["unsupported_or_uncertain"]))

    def test_docker_stop(self):
        data = translate("docker stop app")
        self.assertEqual(data["intent"], "stop_container")
        self.assertFalse(data["requires_confirmation"])

    def test_docker_rm_requires_confirmation(self):
        data = translate("docker rm app")
        self.assertEqual(data["intent"], "delete_container")
        self.assertTrue(data["requires_confirmation"])

    def test_docker_rmi_requires_confirmation(self):
        data = translate("docker rmi redis")
        self.assertEqual(data["intent"], "delete_image")
        self.assertTrue(data["requires_confirmation"])

    def test_docker_build_is_uncertain(self):
        data = translate("docker build -t my-app .")
        self.assertEqual(data["intent"], "docker_translation")
        self.assertIn("container build support", " ".join(data["unsupported_or_uncertain"]))

    def test_docker_compose_up_is_not_full_parity(self):
        data = translate("docker compose up")
        self.assertEqual(data["intent"], "compose_like_service")
        self.assertTrue(data["requires_confirmation"])
        self.assertIn("Compose parity", " ".join(data["unsupported_or_uncertain"]))

    def test_install_script_is_executable_and_has_help(self):
        self.assertTrue(INSTALL_SCRIPT.exists())
        self.assertTrue(INSTALL_SCRIPT.stat().st_mode & 0o111)
        result = subprocess.run(
            [str(INSTALL_SCRIPT), "--help"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        self.assertIn("Install Apple's native container CLI", result.stdout)
        self.assertIn("--check", result.stdout)

    def test_update_script_is_executable_and_has_help(self):
        self.assertTrue(UPDATE_SCRIPT.exists())
        self.assertTrue(UPDATE_SCRIPT.stat().st_mode & 0o111)
        result = subprocess.run(
            [str(UPDATE_SCRIPT), "--help"],
            check=True,
            text=True,
            stdout=subprocess.PIPE,
        )
        self.assertIn("Update the apple-container skill", result.stdout)

    def test_repo_analyzer_url_requires_clone_confirmation(self):
        data = analyze_repo("https://github.com/example/project")
        self.assertEqual(data["intent"], "github_project_setup")
        self.assertEqual(data["input_type"], "url")
        self.assertTrue(data["requires_confirmation"])
        self.assertIn("Where should the repository be cloned", " ".join(data["confirmation_questions"]))
        self.assertIn("Repository contents are not available", " ".join(data["unsupported_or_uncertain"]))

    def test_repo_analyzer_detects_project_signals_and_questions(self):
        data = analyze_repo(ROOT / "tests" / "fixtures" / "sample_repo")
        detected = data["detected"]
        self.assertEqual(data["intent"], "github_project_setup")
        self.assertEqual(data["input_type"], "local_path")
        self.assertTrue(data["requires_confirmation"])
        self.assertIn("Dockerfile", detected["dockerfiles"])
        self.assertIn("compose.yaml", detected["compose_files"])
        self.assertIn(".env.example", detected["env_examples"])
        self.assertIn("package.json", detected["package_files"])
        self.assertIn("node", detected["runtimes"])
        self.assertIn("3000", detected["exposed_ports"])
        self.assertIn("APP_SECRET", detected["env_keys"])
        self.assertIn("DATABASE_URL", detected["env_keys"])
        self.assertIn("POSTGRES_PASSWORD", detected["env_keys"])
        self.assertIn("compose", detected)
        self.assertIn("service_plans", detected)
        self.assertEqual(detected["compose"][0]["named_volumes"], ["postgres_data"])

        plans = {plan["service"]: plan for plan in detected["service_plans"]}
        self.assertEqual(set(plans), {"postgres", "redis", "web"})
        self.assertEqual(plans["web"]["source"], "build")
        self.assertEqual(plans["web"]["build"]["context"], ".")
        self.assertEqual(plans["web"]["build"]["dockerfile"], "Dockerfile")
        self.assertEqual(plans["web"]["build"]["args"]["BUILD_MODE"], "production")
        self.assertEqual(plans["web"]["depends_on"], ["postgres"])
        self.assertEqual(plans["web"]["ports"][0]["host"], "8080")
        self.assertEqual(plans["web"]["ports"][0]["container"], "3000")
        self.assertIn("DATABASE_URL", plans["web"]["environment_keys"])
        self.assertEqual(
            plans["web"]["service_name_env_references"],
            [
                {
                    "env": "DATABASE_URL",
                    "service": "postgres",
                    "value": "postgres://dev:dev@postgres:5432/dev",
                }
            ],
        )
        self.assertEqual(plans["postgres"]["source"], "image")
        self.assertEqual(plans["postgres"]["image"], "postgres:18-alpine")
        self.assertEqual(plans["postgres"]["named_volume_sources"], ["postgres_data"])
        self.assertIn("healthcheck exists", " ".join(plans["postgres"]["run_notes"]))

        joined_questions = " ".join(data["confirmation_questions"])
        self.assertIn("image name/tag", joined_questions)
        self.assertIn("environment variables", joined_questions)
        self.assertIn("host port mappings", joined_questions)
        self.assertIn("persistent data mounts", joined_questions)
        self.assertIn("web", joined_questions)
        self.assertIn("postgres_data", joined_questions)
        self.assertIn("8080->3000", joined_questions)
        self.assertIn("service-discovery replacement", joined_questions)
        self.assertIn("Compose parity", " ".join(data["unsupported_or_uncertain"]))
        self.assertIn("depends_on", " ".join(data["unsupported_or_uncertain"]))
        self.assertIn("service names", " ".join(data["unsupported_or_uncertain"]))

        recommended = data["recommended_solution"]
        self.assertEqual(recommended["strategy"], "compose-to-apple-container-explicit-plan")
        self.assertIn("approval_text", recommended)
        self.assertEqual(recommended["data_migration"]["strategy"], "fresh-empty-volumes")
        self.assertFalse(recommended["data_migration"]["included_in_shell_script"])
        self.assertEqual(recommended["resource_names"]["network"], "sample-repo-net")
        self.assertEqual(recommended["resource_names"]["containers"]["postgres"], "sample-repo-postgres")
        self.assertEqual(recommended["resource_names"]["containers"]["web"], "sample-repo-web")
        self.assertEqual(recommended["resource_names"]["volumes"]["postgres_data"], "sample-repo-postgres-data")
        self.assertIn("web", recommended["ports"])
        self.assertEqual(recommended["ports"]["web"][0]["detected_host"], "8080")
        self.assertEqual(recommended["ports"]["web"][0]["container"], "3000")

        commands = {command["id"]: command for command in recommended["commands"]}
        self.assertIn("create-network", commands)
        self.assertIn("create-volume-postgres-data", commands)
        self.assertIn("build-web", commands)
        self.assertIn("run-postgres", commands)
        self.assertIn("wait-postgres", commands)
        self.assertIn("resolve-postgres-ip-for-web", commands)
        self.assertIn("run-web", commands)
        self.assertIn("pg_isready", commands["wait-postgres"]["command"])
        self.assertIn("SAMPLE_REPO_POSTGRES_IP=$(container inspect sample-repo-postgres", commands["resolve-postgres-ip-for-web"]["command"])
        self.assertIn('"DATABASE_URL=postgres://dev:dev@${SAMPLE_REPO_POSTGRES_IP}:5432/dev"', commands["run-web"]["command"])
        self.assertIn("set -euo pipefail", recommended["shell_script"])
        self.assertIn("curl -fsS -I", recommended["shell_script"])
        self.assertIn("container list --all", recommended["shell_script"])


if __name__ == "__main__":
    unittest.main()
