# Assess and improve reliability

Load this reference for service health, alert quality, capacity, recurring incidents, or a request to improve reliability. Use existing service objectives and operational conventions before recommending new ones.

## Establish service health

Start with user impact and the four golden signals: latency, traffic, errors, and saturation. Use request-oriented signals for serving paths and utilization, saturation, and errors for constrained resources. Include dependency behavior, relevant changes, and telemetry coverage.

Record the target, measurement window, query provenance, result, and data freshness. Separate a healthy observed signal from an unobserved component. Low traffic, missing samples, an unreachable monitoring backend, and an empty query must remain distinguishable from zero errors.

Done when the user-facing symptom is connected to measured signals, or the record names the coverage preventing a conclusion.

## Evaluate objectives

Locate the service's SLI definition, numerator and denominator, eligible traffic, measurement window, SLO target, and error-budget policy. Check that the measurement represents the user journey and treats failed or missing measurements according to the established policy.

For a ratio SLI, allowed bad events equal `(1 - target) × eligible events`; consumed bad events must use the same population and window. Compare burn rates across the service's existing windows. Use time-based downtime calculations only when the objective is actually time-based.

Do not invent targets, paging thresholds, release freezes, or recovery objectives. If they are absent, report the gap and propose measurable candidates with their trade-offs for the service owner to decide. Historical averages alone do not define acceptable user experience.

Done when the assessment uses the actual objective and budget policy, or explicitly distinguishes a proposed policy from an existing one.

## Improve the next response

Review whether alerts identify actionable user impact, carry the correct service and environment, link a usable runbook, and have a clear owner. Look for duplicate incidents, flapping, missing recovery signals, and alerts that trigger too late or without a useful response. Propose a concrete query or routing change and a replay or shadow-validation method before enabling it.

For capacity, compare observed demand and saturation with configured limits, quotas, scaling behavior, and remaining headroom. State the units, time horizon, and uncertainty; do not extrapolate a peak into a forecast without evidence. Keep capacity pressure, quota exhaustion, and application inefficiency as separate hypotheses.

For recurring incidents, compare past evidence and corrective actions. Identify the repeated mechanism, unfinished prevention work, and a durable change whose effect can be measured. Separate immediate mitigation from that follow-up.

Done when each recommendation has evidence, expected reliability benefit, implementation cost, owner or owner-needed marker, and a verification method. Route any actual configuration change through the coordinator's authorization and post-change checks.
