from typing import Any, Dict


def build_recovery_plan(config: Dict[str, Any]) -> Dict[str, Any]:
    """Build a structured recovery plan from the validated config."""
    plan = {
        "owner": config["originalOwner"],
        "recovery_address": config["recoveryAddress"],
        "target_active": config["targetActive"],
        "threshold": config["threshold"],
        "approver_threshold": config.get("approverThreshold", 1),
        "time_lock_duration": config["timeLockDuration"],
        "network": config.get("network", "tron"),
        "chain_id": config.get("chainId"),
        "contract_name": config.get("contractName", "PermissionRecovery"),
        "contract_address": config.get("contractAddress", ""),
        "recovery_mode": config.get("recoveryMode", "timelock"),
        "notes": config.get("notes", ""),
        "emergency_recovery_address": config.get("emergencyRecoveryAddress", ""),
        "required_actions": config.get("requiredActions", []),
        "steps": [
            "1. Review the original owner, recovery address, and target active account.",
            "2. Deploy or reference the PermissionRecovery contract with the provided parameters.",
            "3. Initiate recovery on-chain, gather multisig approvals, and wait for the configured timelock to elapse.",
            "4. Complete recovery or trigger the emergency recovery path if the emergency address is authorized.",
        ],
    }
    return plan
