from typing import Any, Dict


def assess_recovery_readiness(config: Dict[str, Any]) -> Dict[str, Any]:
    """Assess how well the current setup supports recovery execution."""
    timelock_duration = int(config.get("timeLockDuration", 0))
    approver_threshold = int(config.get("approverThreshold", 1))
    emergency_address = str(config.get("emergencyRecoveryAddress", "")).strip()

    return {
        "has_recovery_entry": True,
        "has_emergency_recovery_address": bool(emergency_address),
        "has_multisig": approver_threshold > 1,
        "has_timelock": timelock_duration > 0,
        "timelock_duration_seconds": timelock_duration,
        "approver_threshold": approver_threshold,
        "emergency_recovery_address": emergency_address,
        "recovery_success_score": min(100, 30 + (15 if bool(emergency_address) else 0) + (20 if approver_threshold > 1 else 0) + (15 if timelock_duration >= 86400 else 5)),
        "notes": [
            "Recovery entry is available through the contract and the recovery plan generator.",
            "A dedicated emergency recovery address increases operational resilience.",
            "A higher approver threshold improves protection against unilateral changes.",
            "A longer timelock gives more time for review and intervention.",
        ],
    }
