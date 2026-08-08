# Recovery Playbook

This document summarizes the practical recovery path when a TRON account or contract permission has been compromised and the original signing authority is no longer under the user's control.

## 1. Confirm the contract architecture

Check whether the contract or upgrade path uses one of the following patterns:

- ProxyAdmin + TimelockController
- Multi-signature wallet
- Emergency recovery address
- DAO governance controls

If the architecture includes a timelock, governance path, or emergency address, these become the main recovery entry points.

## 2. Check for emergency recovery mechanisms

Review whether the contract exposes any of the following:

- emergencyRecoveryAddress
- pause/resume controls
- admin or owner change functions
- upgrade authorization paths

If a fallback recovery address exists, it may be possible to reassign ownership or admin permissions through that route.

## 3. Start a governance proposal

If the contract is governed by a DAO or community-based mechanism:

1. Prepare a proposal that explains the compromise and the intended recovery action.
2. Request community support and review.
3. Wait for the timelock delay to expire before execution.
4. Use the governance process to prevent malicious actions and restore control.

## 4. Use the timelock window

A longer timelock is helpful because it gives the community and security reviewers more time to detect and block attacks. The recovery plan should assume that the timelock can be used as a safety buffer.

## 5. Preserve the ability to cancel or pause

The recovery contract should retain a path to:

- pause the flow
- cancel an in-progress recovery
- block a malicious execution until the issue is reviewed

This significantly improves the success chance of the recovery.

## 6. Practical next step in this repository

This repository already includes a recovery contract and a recovery plan generator that model the following:

- timelock-based recovery
- multisig approval
- emergency recovery address
- cancellation path

Use the agent and execution plan scripts in this repository to prepare the recovery payload and document the required steps.
