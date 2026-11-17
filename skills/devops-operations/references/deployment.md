# Trace and verify a deployment

Load this reference for a failed release, deployment regression, or requested rollout. Follow the repository's actual release path and toolchain; do not invent a new pipeline while diagnosing an existing one.

## Trace the release

Follow **commit → workflow → image → migration → deployment → health**. At each boundary, record the identity of the input and the evidence of the output. Mark a migration step as not applicable only after checking the release process.

| Boundary | Evidence to inspect |
|---|---|
| Commit | Exact SHA, branch or release tag, intended change |
| Workflow | Trigger, run ID and attempt, selected environment, job dependencies, outcome and logs |
| Image | Registry, immutable digest, build provenance, platform and intended application version |
| Migration | Whether it ran, version applied, target database and compatibility with old/new application versions |
| Deployment | Target service, desired revision, running revision, rollout events and replacement progress |
| Health | Readiness, user-facing smoke check, errors, latency and dependency behavior after the rollout |

Done when the deployed artifact is tied to the intended source revision, or the broken boundary and its evidence are identified.

## GitHub Actions checks

Use repository-scoped `gh` commands to inspect the exact run and failed job logs. Distinguish a queued run, environment approval wait, canceled concurrency run, failed build, and a deployment that failed after a successful workflow. A green workflow is not proof that the new service is healthy.

Check workflow conditions, reusable workflow inputs, environment-specific variables, artifact names, and credential identity without printing secret values. Check what actually deployed when a workflow retry reused an earlier artifact. Re-running a workflow may publish images, rerun migrations, or deploy; treat it as an action, not a log lookup.

## ECS checks

Use explicit AWS profile and region, cluster, and service for each inspection. Compare the service deployment and task definition revision with running tasks and their actual image digests. Inspect ECS service events, stopped-task reasons, container exits, and load balancer target health.

Distinguish application failure from image pull, task startup, execution-role, task-role, networking, capacity, and health-check failures. For secret retrieval, check the configured identifier and secret existence in the intended account/region using metadata only; distinguish a missing or misaddressed secret from denied access and network timeout. Secret values are unnecessary for this diagnosis. A mutable image tag can resolve to different bytes; a task definition revision alone does not prove the running image identity. A completed waiter or steady desired count still needs application-level verification.

## Prepare and execute a change

Summarize the exact artifact and target, existing authorization, expected disruption, migration ordering, rollout checks, and rollback path. Only the coordinator executes mutations within the approved scope. Independent evidence collectors never trigger releases or alter tasks.

Do not assume rolling back the application reverses a database migration. Check backward compatibility and recovery procedures before selecting rollback. If the proposed action changes the target, artifact, migration behavior, or blast radius beyond existing authorization, obtain that decision before execution.

Done when the intended revision is serving the intended target, the original failure and agreed health checks pass on fresh evidence, and the observation window is recorded. Otherwise report the remaining failure and whether rollback was proposed, attempted, or verified.
