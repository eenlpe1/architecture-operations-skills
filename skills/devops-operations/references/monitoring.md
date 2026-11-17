# Recovery monitoring

Use for a reported issue, an in-progress deployment, or post-fix verification. This workflow operates only during the active session.

1. Define success and failure from the service's runbook, deployment criteria, existing SLO, and user-visible behavior. Track backend/frontend/migration outcomes separately. If criteria are absent, agree on an observable check; report the limited scope of that check.
2. Record the target and initial state: deployment/run/commit/image IDs, desired version, start time, affected services, and available health signals. Reconfirm account/environment before cloud queries.
3. Poll at a cadence appropriate to the provider and operation (default 30 seconds), with a default 15-minute total observation budget. Reuse existing monitoring when available; bound output and respect throttling/backoff. Give a concise progress update at least every minute during active monitoring.
4. Stop on observed success, terminal failure, user cancellation, or budget expiry. For recovery without a prescribed stabilization window, require two consecutive successful observations at least one polling interval apart; state that limited observation window. A configured runbook window takes precedence and can require a longer explicitly agreed budget.
5. On failure, collect new discriminating evidence and return to investigation. On timeout or missing telemetry, preserve current state and a resumable handoff; never convert timeout or absent errors into success. On cancellation, stop task-owned polling without canceling external deployments unless authorized.

Workflow success alone does not establish service health. Query failure or expired authentication means verification is blocked; retain the last confirmed observation and resume only after authentication is restored. A retry/rerun, restart, rollback, or schedule change is a live action, not a monitoring step.

Done when the record states recovered/failed/unresolved, the evidence and observation window, which components were checked, and any pending next check. No daemon, scheduler, notification channel, or always-on collector is installed by this skill.
