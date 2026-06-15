import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CANONICAL = ROOT / "skills" / "apple-container"
DISCOVERABLE = ROOT / "skills" / "apple-container-operator"


def frontmatter_value(text, key):
    match = re.search(rf"^{re.escape(key)}:\s*(.+)$", text, re.MULTILINE)
    return match.group(1).strip() if match else None


class SkillMetadataTests(unittest.TestCase):
    def test_discoverable_alias_has_searchable_name(self):
        skill_text = (DISCOVERABLE / "SKILL.md").read_text()
        self.assertEqual(frontmatter_value(skill_text, "name"), "apple-container-operator")
        self.assertIn("Apple Container Operator", frontmatter_value(skill_text, "description"))

    def test_alias_keeps_supporting_files_in_sync(self):
        ignored = {"SKILL.md"}
        canonical_files = {
            path.relative_to(CANONICAL)
            for path in CANONICAL.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        } - {Path(name) for name in ignored}
        alias_files = {
            path.relative_to(DISCOVERABLE)
            for path in DISCOVERABLE.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        } - {Path(name) for name in ignored}

        self.assertEqual(canonical_files, alias_files)
        for relative in canonical_files:
            with self.subTest(file=str(relative)):
                self.assertEqual(
                    (CANONICAL / relative).read_bytes(),
                    (DISCOVERABLE / relative).read_bytes(),
                )


if __name__ == "__main__":
    unittest.main()
