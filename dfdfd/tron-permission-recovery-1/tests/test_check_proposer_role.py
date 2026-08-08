import unittest
from scripts.check_proposer_role import get_role_hash, normalize_address


class CheckProposerRoleTests(unittest.TestCase):
    def test_role_hashes_are_defined(self) -> None:
        self.assertEqual(get_role_hash("PROPOSER"), "0x" + "0" * 63 + "1")
        self.assertEqual(get_role_hash("EXECUTOR"), "0x" + "0" * 63 + "2")
        self.assertEqual(get_role_hash("CANCELLER"), "0x" + "0" * 63 + "3")

    def test_normalize_address_accepts_hex_addresses(self) -> None:
        self.assertEqual(normalize_address("0x1234"), "0x1234")

    def test_normalize_address_converts_tron_base58_address(self) -> None:
        # A known TRON-style base58 address should normalize to a 20-byte hex address.
        tron_address = "TFKi76LieckzDg7jZsXfKsFwDb9twPBJVd"
        normalized = normalize_address(tron_address)
        self.assertTrue(normalized.startswith("0x"))
        self.assertEqual(len(normalized), 42)


if __name__ == "__main__":
    unittest.main()
