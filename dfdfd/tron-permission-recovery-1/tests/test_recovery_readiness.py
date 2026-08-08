import unittest
from pathlib import Path

from agent.config_loader import load_config
from agent.recovery_readiness import assess_recovery_readiness


class RecoveryReadinessTests(unittest.TestCase):
    def test_assess_recovery_readiness_reports_key_controls(self) -> None:
        config = load_config(str(Path("deployment/config.json")))
        readiness = assess_recovery_readiness(config)
        self.assertTrue(readiness["has_recovery_entry"])
        self.assertTrue(readiness["has_emergency_recovery_address"])
        self.assertTrue(readiness["has_multisig"])
        self.assertTrue(readiness["has_timelock"])


if __name__ == "__main__":
    unittest.main()
