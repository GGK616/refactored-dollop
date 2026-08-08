import json
from pathlib import Path
from typing import Any, Dict


class ConfigError(ValueError):
    """Raised when the deployment config is invalid."""


def load_config(config_path: str | None = None) -> Dict[str, Any]:
    """Load and validate deployment configuration from JSON."""
    if config_path is None:
        config_path = str(Path(__file__).resolve().parents[1] / "deployment" / "config.json")

    with open(config_path, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    required_fields = ["originalOwner", "recoveryAddress", "targetActive", "threshold", "timeLockDuration"]
    missing = [field for field in required_fields if field not in data]
    if missing:
        raise ConfigError(f"Missing required fields: {', '.join(missing)}")

    if not isinstance(data["originalOwner"], str) or not data["originalOwner"].startswith("T"):
        raise ConfigError("originalOwner must be a TRON address string")
    if not isinstance(data["recoveryAddress"], str) or not data["recoveryAddress"].startswith("T"):
        raise ConfigError("recoveryAddress must be a TRON address string")
    if not isinstance(data["targetActive"], str) or not data["targetActive"].startswith("T"):
        raise ConfigError("targetActive must be a TRON address string")

    if not isinstance(data["threshold"], int) or data["threshold"] <= 0:
        raise ConfigError("threshold must be a positive integer")

    if not isinstance(data["timeLockDuration"], int) or data["timeLockDuration"] <= 0:
        raise ConfigError("timeLockDuration must be a positive integer")

    if "approverThreshold" in data and (not isinstance(data["approverThreshold"], int) or data["approverThreshold"] <= 0):
        raise ConfigError("approverThreshold must be a positive integer when provided")

    if "network" in data and not isinstance(data["network"], str):
        raise ConfigError("network must be a string when provided")
    if "chainId" in data and not isinstance(data["chainId"], int):
        raise ConfigError("chainId must be an integer when provided")
    if "requiredActions" in data and not isinstance(data["requiredActions"], list):
        raise ConfigError("requiredActions must be a list when provided")

    return data
