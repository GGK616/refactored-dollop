# TRON Timelock deployment helper

This folder contains a minimal deployment helper for a TimelockController-compatible contract on TRON.

## Prerequisites

1. Prepare a compiled artifact named TimelockController.json with both `abi` and `bytecode` fields.
2. Export your TRON private key and optional API key:

```bash
export TRON_PRIVATE_KEY=your_private_key
export TRON_RPC_URL=https://api.trongrid.io
export TRON_FULL_HOST=https://api.trongrid.io
export TRON_API_KEY=your_api_key_if_needed
export MIN_DELAY=3600
export PROPOSERS=TFKi76LieckzDg7jZsXfKsFwDb9twPBJVd
export EXECUTORS=TFKi76LieckzDg7jZsXfKsFwDb9twPBJVd
```

## Run

```bash
node scripts/tron/deploy_timelock.js
```

## Notes

- The script expects a TimelockController artifact from your Solidity compiler.
- TRON mainnet does not ship with a pre-deployed TimelockController address; you must deploy one yourself.
