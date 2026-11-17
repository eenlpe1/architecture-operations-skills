# Investigate an operational failure

Load this reference for an outage, error, latency regression, failed job, or unexplained resource behavior. Use installed CLIs and existing telemetry APIs; no hosted agent or MCP connection is required.

## Establish the failure

Identify the affected service, exact target environment, customer impact, expected behavior, observed symptom, and absolute incident window with timezone. Read repository context and runbooks before selecting commands. Record the last known healthy point and any gaps in access or telemetry. Done when every observation belongs to a named target and time window.

## Collect evidence

Start with the failing request or job and follow its dependency path. Compare a healthy cohort or earlier window when available. Correlate deployment and configuration history with symptoms, then test whether the timing explains the mechanism.

Use narrow CLI queries: select the service, account, region or namespace explicitly; set time bounds, result limits, pagination bounds, and a timeout. Retrieve summaries before raw payloads. Keep sensitive log samples in the private case location and redact excerpts before sharing them. An empty result means only that this query found nothing within its coverage; denied access or missing telemetry does not establish health.

Independent collectors may inspect logs, metrics, deployment history, or dependencies in parallel. Give each collector the target, window, hypothesis, evidence limits, and expected output. Collectors return timestamped observations, query provenance, counterevidence, and gaps. They remain read-only; the coordinator owns changes and resolves conflicting findings.

Done when evidence separates the failing component from affected downstream components, or the record identifies the specific missing source preventing that distinction.

## Test hypotheses

Keep a short working list rather than issuing unrelated queries:

| Hypothesis | Supporting observation | Counterevidence or falsifying test | Next check |
|---|---|---|---|
| A recent change caused the failure | Relevant change precedes symptom | Same failure before change, or unaffected cohort using the change | Compare cohorts and inspect the changed path |

Replace the example with case-specific hypotheses. Distinguish observed facts, plausible causes, and confirmed mechanisms. Prefer the next check that most reduces uncertainty. If evidence contradicts a hypothesis, revise it; a rollback restoring health is evidence of a change relationship, not proof of the exact defect.

Stop repetitive querying when evidence no longer changes. Record what was tested, what remains uncertain, and which access, artifact, or operator action would unblock progress. Do not fabricate a numerical confidence score.

## Conclude or hand off

Present the affected target, impact, timeline, evidence, leading explanation and alternatives, and the smallest proposed corrective action. For a change, state its blast radius, verification signal, and rollback limitations before execution under the coordinator's action policy.

Done when the case has an evidence-backed conclusion or an explicit unresolved blocker. A fix is complete only after fresh checks show the original symptom has cleared; otherwise retain the unresolved status and next check.
