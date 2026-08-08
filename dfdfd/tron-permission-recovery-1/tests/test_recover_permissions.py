import json
import tempfile
import unittest
from pathlib import Path

from scripts.recover_permissions import build_execution_plan, build_tron_update_payload
from agent.config_loader import load_config


class RecoverPermissionsTests(unittest.TestCase):
    def test_payload_contains_target_active_and_threshold(self) -> None:
        config = load_config(str(Path("deployment/config.json")))
        payload = build_tron_update_payload(config)
        self.assertEqual(payload["active"]["threshold"], 1)
        self.assertEqual(payload["active"]["keys"][0]["address"], config["activePermissionAddresses"][0])

    def test_execution_plan_contains_command(self) -> None:
        config = load_config(str(Path("deployment/config.json")))
        plan = build_execution_plan(config)
        self.assertIn("wallet/updateaccountpermission", plan["command"])

    def test_payload_uses_owner_and_active_permission_settings(self) -> None:
        config = load_config(str(Path("deployment/config.json")))
        payload = build_tron_update_payload(config)
        self.assertEqual(payload["owner"]["threshold"], 3)
        self.assertEqual(payload["active"]["threshold"], 1)
        self.assertEqual(payload["owner"]["keys"][0]["address"], config.get("ownerPermissionAddress", config["originalOwner"]))
        self.assertEqual(payload["active"]["keys"][0]["address"], config["activePermissionAddresses"][0])

    def test_main_writes_output_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "plan.json"
            from scripts.recover_permissions import main

            exit_code = main(["--config", "deployment/config.json", "--output", str(output_path)])
            self.assertEqual(exit_code, 0)
            self.assertTrue(output_path.exists())
            written = json.loads(output_path.read_text(encoding="utf-8"))
            self.assertIn("payload", written)


if __name__ == "__main__":
    unittest.main()
