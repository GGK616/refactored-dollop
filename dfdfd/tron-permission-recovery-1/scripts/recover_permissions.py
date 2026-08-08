#!/usr/bin/env python3
"""Generate a TRON permission recovery execution plan.

This script does not directly call a TRON node because the runtime environment may
not have the required Tron JSON-RPC or tronpy support installed. Instead, it
produces the exact payload and command sequence that an operator should use with
an authenticated TRON node endpoint.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from agent.config_loader import load_config


def build_tron_update_payload(config: Dict[str, Any]) -> Dict[str, Any]:
    """Build an updateAccountPermission payload for a TRON node.

    The payload structure is based on the TRON account permission model where the
    owner permission is updated to point to an active permission with the desired
    threshold and keys.
    """
    owner_address = config.get("ownerPermissionAddress", config["originalOwner"])
    owner_weight = int(config.get("ownerPermissionWeight", 1))
    owner_threshold = int(config.get("ownerPermissionThreshold", 1))
    active_addresses = config.get("activePermissionAddresses", [config.get("activePermissionAddress", config["targetActive"])])
    active_weight = int(config.get("activePermissionWeight", 1))
    active_threshold = int(config.get("activePermissionThreshold", 1))

    return {
        "owner_address": config["originalOwner"],
        "owner": {
            "type": 2,
            "permission_name": "owner",
            "threshold": owner_threshold,
            "keys": [
                {
                    "address": owner_address,
                    "weight": owner_weight,
                }
            ],
        },
        "active": {
            "type": 2,
            "permission_name": "active",
            "threshold": active_threshold,
            "keys": [
                {
                    "address": address,
                    "weight": active_weight,
                }
                for address in active_addresses
            ],
        },
        "permission_name": "active",
        "visible": True,
    }


def build_execution_plan(config: Dict[str, Any]) -> Dict[str, Any]:
    payload = build_tron_update_payload(config)
    return {
        "summary": "Use the original owner private key and multisig approvals to update account permissions on a TRON node after the timelock expires; the emergency recovery address can trigger a fallback path if configured.",
        "rpc_endpoint": "http://127.0.0.1:8090",
        "payload": payload,
        "command": (
            "curl -X POST http://127.0.0.1:8090/wallet/updateaccountpermission "
            "-H 'Content-Type: application/json' "
            "-d '{\"owner_address\":\"<owner-address>\",\"owner\":{\"type\":2,\"permission_name\":\"owner\",\"threshold\":1,\"keys\":[{\"address\":\"<target-active>\",\"weight\":1}]},\"active\":{\"type\":2,\"permission_name\":\"active\",\"threshold\":1,\"keys\":[{\"address\":\"<target-active>\",\"weight\":1}]},\"permission_name\":\"active\",\"visible\":true}'"
        ),
        "multisig": {
            "approver_threshold": config.get("approverThreshold", 1),
            "emergency_recovery_address": config.get("emergencyRecoveryAddress", ""),
            "required_approvals": [
                "approveRecovery"
            ],
        },
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Generate a TRON permission recovery execution plan")
    parser.add_argument("--config", default=str(Path(__file__).resolve().parents[1] / "deployment" / "config.json"))
    parser.add_argument("--output", help="Optional path to write the execution plan JSON")
    args = parser.parse_args(list(argv) if argv is not None else None)

    config = load_config(args.config)
    plan = build_execution_plan(config)
    if args.output:
        Path(args.output).write_text(json.dumps(plan, indent=2), encoding="utf-8")
        print(f"Execution plan written to {args.output}")
    else:
        print(json.dumps(plan, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
