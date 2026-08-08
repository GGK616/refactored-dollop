from pathlib import Path
import unittest


class PermissionRecoveryContractTests(unittest.TestCase):
    def test_contract_supports_cancellation_and_settings_update_events(self) -> None:
        source = Path("contracts/PermissionRecovery.sol").read_text(encoding="utf-8")

        self.assertIn("event RecoverySettingsUpdated", source)
        self.assertIn("function cancelRecovery", source)
        self.assertIn("emit RecoveryCancelled", source)

    def test_contract_supports_multisig_and_emergency_recovery(self) -> None:
        source = Path("contracts/PermissionRecovery.sol").read_text(encoding="utf-8")

        self.assertIn("emergencyRecoveryAddress", source)
        self.assertIn("approverThreshold", source)
        self.assertIn("function approveRecovery", source)
        self.assertIn("function triggerEmergencyRecovery", source)


if __name__ == "__main__":
    unittest.main()
