# Validation record

This record covers the proposed 1.1.0 architecture and operations skill pack. Validation date: 2026-11-17.

## Automated checks

- `python3 scripts/validate.py`: metadata, skill frontmatter, local references, and unfinished scaffold checks passed.
- `python3 -m unittest discover -s tests`: 28 isolated tests passed, covering installer conflicts/idempotence/alias paths, configuration preservation, validator failures and containment, and fixture integrity.
- Codex `skill-creator/scripts/quick_validate.py`: all three skills passed.
- `git diff --check`: passed.
- The native Codex plugin validator was unavailable. The repository validator checked JSON structure, manifest name/version alignment, packaged skill paths, and marketplace references; it is not a replacement for a full client schema validator.

## Independent behavioral smoke evaluation

Independent evaluator agents received fixture inputs without the expected-answer file, chose routes from skill descriptions, then read selected instructions. A separate grader compared their responses with the withheld rubric. Most cases were evaluated in batches; ECS and unavailable-delegation follow-ups used new evaluator contexts.

Latest responses passed all **18** fixture rubrics: automatic/negative routing, architecture and pipeline design boundaries, mixed incident/design sequencing, skipped backend delivery, ECS secret diagnostics, migration failure, stale checks, authentication expiry, coordinated changes, Terraform target/destructive-plan checks, missing metrics/SLO, partial recovery, monitoring timeout, untrusted log content, and sequential fallback.

The initial ECS responses omitted a missing/misaddressed-secret alternative. The deployment reference was improved to require metadata-only identifier/account/region/existence checks alongside connectivity and access checks; a fresh response passed. Installer alias and validator containment/type bugs discovered during review received regression tests before activation.

## Global configuration check

The checkout installer completed, and its read-only `--check` passed from an unrelated working directory. This verifies link targets and discovery configuration for Codex, Claude, and Antigravity; it does not verify how every client/model selects skills.

## Limits

- No live cloud deployment, Terraform apply/state mutation, or remediation was tested.
- No always-on runtime or external notification integration was installed.
- Fresh isolation for every scenario and end-to-end Claude/Antigravity sessions were not tested.
- Decision-file persistence and operational case persistence were described in simulated responses, not exercised against real engagements.
- Automatic model selection remains probabilistic. Use explicit skill invocation when the host selects the wrong workflow.

Reproduce structural checks and use the [evaluation procedure](../tests/README.md) for independent client-level testing. Private environment mappings, incident history, and local plugin backups are outside this repository.
