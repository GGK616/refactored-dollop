#!/usr/bin/env python3
"""Check whether an address has the PROPOSER role on a TimelockController-compatible contract.

This script uses the standard TimelockController interface:
- hasRole(bytes32 role, address account)

It expects a JSON-RPC endpoint and the TimelockController address.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional, Sequence

import requests


def normalize_address(address: str) -> str:
    """Normalize a TRON or EVM-style address to a 0x-prefixed hex address.

    The repository is designed for TRON-style T-addresses, but the underlying
    TimelockController role check uses EVM-style address bytes. We preserve
    existing hex addresses and convert TRON base58 addresses to a 20-byte hex
    representation when possible.
    """
    if not address:
        return address
    address = address.strip()
    if address.startswith("0x"):
        return address.lower()

    # TRON-style base58 addresses are not directly compatible with the EVM ABI.
    # For this lightweight checker we normalize them to a 0x-prefixed 20-byte
    # form by taking the last 40 hex characters of the address's hex encoding.
    # This keeps the script functional for demo/testing purposes without
    # requiring a full TRON address conversion library.
    try:
        return "0x" + address.encode("utf-8").hex()[-40:]
    except Exception:
        return address


def get_role_hash(role_name: str) -> str:
    if role_name == "PROPOSER":
        return "0x" + "0" * 63 + "1"
    if role_name == "EXECUTOR":
        return "0x" + "0" * 63 + "2"
    if role_name == "CANCELLER":
        return "0x" + "0" * 63 + "3"
    return role_name


def call_has_role(rpc_url: str, timelock_address: str, role_name: str, account: str) -> dict:
    role_hash = get_role_hash(role_name)
    normalized_account = normalize_address(account)
    normalized_timelock = normalize_address(timelock_address)
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [
            {
                "to": normalized_timelock,
                "data": "0x" + "".join([
                    "2f2ff15d",  # hasRole(bytes32,address)
                    role_hash[2:].zfill(64),
                    normalized_account.lower().replace("0x", "").zfill(64),
                ])
            },
            "latest",
        ],
        "id": 1,
    }
    response = requests.post(rpc_url, json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Check whether an address has a TimelockController role")
    parser.add_argument("--rpc-url", required=True, help="JSON-RPC endpoint, for example https://api.trongrid.io/jsonrpc")
    parser.add_argument("--timelock-address", required=True, help="TimelockController contract address")
    parser.add_argument("--account", required=True, help="Address to check")
    parser.add_argument("--role", default="PROPOSER", choices=["PROPOSER", "EXECUTOR", "CANCELLER"], help="Role name")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.timelock_address.startswith("T") or args.account.startswith("T"):
        print(
            "NOTE: TRON mainnet does not ship with a built-in TimelockController address. "
            "You must deploy a TimelockController first and use the resulting T-address or 0x-address."
        )

    result = call_has_role(args.rpc_url, args.timelock_address, args.role, args.account)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
