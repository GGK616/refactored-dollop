# Permission Recovery Agent

This folder contains a simple agent workflow for the permission recovery project.

## What it does
- Reads deployment configuration from deployment/config.json
- Validates the configuration values for the recovery flow
- Produces a structured recovery plan that can be used by a frontend, script, or manual operator

## Files
- config_loader.py: loads and validates deployment settings
- recovery_plan.py: builds a recovery plan from the validated configuration
- run.py: runs the workflow end to end
