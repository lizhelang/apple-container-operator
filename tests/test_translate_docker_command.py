import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "apple-container" / "scripts" / "translate-docker-command.py"
INSTALL_SCRIPT = ROOT / "skills" / "apple-container" / "scripts" / "install-container.sh"


def translate(command):
    result = subprocess.run(
        [sys.executable, str(SCRIPT), command],
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


if __name__ == "__main__":
    unittest.main()
