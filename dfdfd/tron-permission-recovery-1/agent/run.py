import argparse
import json
from pathlib import Path
from typing import Optional, Sequence

from agent.config_loader import ConfigError, load_config
from agent.recovery_plan import build_recovery_plan


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Build a recovery plan from deployment settings")
    parser.add_argument("--config", default=str(Path(__file__).resolve().parents[1] / "deployment" / "config.json"))
    parser.add_argument("--output", help="Optional path to write the recovery plan JSON")
    args = parser.parse_args(list(argv) if argv is not None else None)

    try:
        config = load_config(args.config)
        plan = build_recovery_plan(config)
    except ConfigError as exc:
        print(f"Configuration error: {exc}")
        return 1

    if args.output:
        output_path = Path(args.output)
        output_path.write_text(json.dumps(plan, indent=2), encoding="utf-8")
        print(f"Recovery plan written to {output_path}")
    else:
        print(json.dumps(plan, indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
