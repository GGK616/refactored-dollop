import json
import tempfile
import unittest
from pathlib import Path

from agent.config_loader import ConfigError, load_config
from agent.recovery_plan import build_recovery_plan
from agent.run import main


class AgentWorkflowTests(unittest.TestCase):
    def test_load_config_reads_valid_settings(self) -> None:
        config = load_config(str(Path("deployment/config.json")))
        self.assertEqual(config["threshold"], 1)
        self.assertEqual(config["timeLockDuration"], 86400)

    def test_load_config_rejects_invalid_values(self) -> None:
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as handle:
            json.dump({"originalOwner": "T123", "recoveryAddress": "T123", "targetActive": "T123", "threshold": 0, "timeLockDuration": 1}, handle)
            temp_path = handle.name

        try:
            with self.assertRaises(ConfigError):
                load_config(temp_path)
        finally:
            Path(temp_path).unlink(missing_ok=True)

    def test_build_recovery_plan_contains_steps(self) -> None:
        config = load_config(str(Path("deployment/config.json")))
        plan = build_recovery_plan(config)
        self.assertIn("steps", plan)
        self.assertGreaterEqual(len(plan["steps"]), 4)

    def test_main_writes_output_file_when_requested(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "plan.json"
            exit_code = main(["--config", "deployment/config.json", "--output", str(output_path)])
            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())
            written = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertEqual(written["threshold"], 1)


if __name__ == "__main__":
    unittest.main()
