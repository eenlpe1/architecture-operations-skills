# Investigate Terraform changes and drift

Load this reference for Terraform validation, unexpected plans, drift, provisioning failures, or an authorized infrastructure change. Use the repository's installed version, lock file, modules, and normal execution path, including remote runs when applicable.

## Bind the target

Establish the root module, backend/state location, workspace, variable sources, provider aliases, AWS profile or other credential identity, region, and intended account/project/subscription. Compare declared provider configuration with actual caller identity; a shell default is not proof that every provider alias targets that account.

Read the existing initialization metadata and backend configuration without exposing credentials. `terraform workspace show` reports the selected workspace only; it does not establish cloud identity. If initialization, workspace, or backend is unclear, stop target-dependent operations and resolve the discrepancy.

Done when the configuration, state, and intended cloud target refer to the same environment, with any intentional multiple-provider targets identified.

## Inspect and plan

Start with configuration, diagnostics, relevant resource addresses, recent changes, and existing run output. Use the repository's validation workflow. Run a plan only after target identity and operation scope are established; planning can contact provider APIs, acquire a state lock, run configured data lookups, and write sensitive artifacts.

Review the full intended plan for creates, updates, deletes, replacements, moved/imported resources, and output changes. Explain the cause and impact of unexpected changes rather than hiding them with targeting or lifecycle changes. A normal plan compares configuration with refreshed observations; inspect refresh-only planning separately when the question is remote drift. Saving a refresh-only plan creates a sensitive local artifact; applying that plan updates state and needs the same state-operation authorization as other writes.

Treat saved plans, state, and machine-readable plan output as sensitive. Share a redacted summary rather than raw files. Verify the workspace and provenance of an existing saved plan; do not apply an unexplained or stale artifact.

Done when each material proposed change has an understood reason, or the specific unexplained change is recorded as a blocker.

## Change and recover

The coordinator alone performs authorized mutations. Applying a plan, destroying resources, importing, removing or moving state, refreshing state, changing a backend or workspace, migrating state, and force-unlocking require explicit authorization for that operation and target. Existing authorization remains valid within its stated scope; preparation must not silently expand it.

Do not automatically reinitialize, upgrade providers, migrate a backend, unlock state, or edit state to make an error disappear. For a lock, identify the owning operation and whether it is still active before proposing recovery. Follow the backend's documented recovery path and account for concurrent operators.

A plan is reviewable evidence, not permission to apply it. Verify what was actually applied and inspect fresh resource health afterwards. For partial failures, capture the updated state of the run before proposing a second action; blindly repeating an apply can broaden or repeat side effects.

Done when the requested infrastructure state and service health are verified, or the remaining divergence and safe next operation are documented. Preserve relevant run IDs and sanitized plan/apply outcomes in the case record.
