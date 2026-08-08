# Tron Permission Recovery

This repository contains a simple Solidity example for a permission recovery flow and a small Python agent that turns deployment settings into a recovery plan.

## Structure
- contracts/PermissionRecovery.sol: Solidity contract for recording recovery intent and timelock state
- deployment/config.json: deployment configuration used by the agent
- agent/: Python workflow for validating and packaging recovery settings
- tests/: unit tests for the agent workflow

## Run the agent

```bash
python3 -m unittest discover -s tests -v
python3 -m agent.run --config deployment/config.json
```

You can also write the plan to a file:

```bash
python3 -m agent.run --config deployment/config.json --output recovery-plan.json
```

## TRON permission recovery execution plan

After the timelock in the recovery contract expires, the operator can use the original owner private key to update the TRON account permissions on a TRON node.

```bash
python3 scripts/recover_permissions.py --config deployment/config.json
python3 scripts/recover_permissions.py --config deployment/config.json --output tron-recovery-plan.json
```

The generated plan includes a JSON payload and a sample `curl` command for the TRON wallet RPC endpoint.

## Architecture overview

The current design follows a layered recovery model:

1. Timelock: recovery cannot be completed immediately; a waiting period is enforced.
2. Multisig approval: approved parties must confirm the recovery before it is finalized.
3. Emergency recovery address: an authorized fallback address can trigger a recovery path if the normal flow is blocked.
4. Cancellation path: the owner can cancel an in-progress recovery before it is finalized.

This makes the process more auditable and safer than a single-owner-only flow.

## Recovery readiness assessment

The repository also includes a readiness assessment helper that evaluates whether the current configuration has the core controls that improve recovery success:

- recovery entry
- emergency recovery address
- multisig approval threshold
- timelock duration

You can run it with:

```bash
python3 - <<'PY'
from agent.config_loader import load_config
from agent.recovery_readiness import assess_recovery_readiness
config = load_config('deployment/config.json')
print(assess_recovery_readiness(config))
PY
```

For the practical recovery workflow after a compromise, see [docs/recovery-playbook.md](docs/recovery-playbook.md).

## Check Proposer role on a TimelockController

You can check whether an address has the PROPOSER role by running:

```bash
python3 scripts/check_proposer_role.py --rpc-url https://api.trongrid.io/jsonrpc --timelock-address <timelock-address> --account <address-to-check>
```

The script calls the TimelockController `hasRole` interface over JSON-RPC.

## Deploy a TimelockController on TRON

If you want to deploy a TimelockController contract first and then query proposer/executor permissions, use the helper in [scripts/tron](scripts/tron):

```bash
node scripts/tron/deploy_timelock.js
```

Before running it, make sure you have a compiled artifact at [scripts/tron/TimelockController.json](scripts/tron/TimelockController.json) and set the required environment variables described in [scripts/tron/README.md](scripts/tron/README.md).
