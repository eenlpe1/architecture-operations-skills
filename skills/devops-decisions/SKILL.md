---
name: devops-decisions
description: Design, audit, or improve a CI/CD delivery system using CALMS and DORA metrics, and record its design decisions. Use for pipeline architecture, release strategy, and delivery-process improvements. For a failed or skipped workflow run, deployment incident, or recovery check, start with devops-operations.
---

# DevOps Decisions

CI/CD pipeline choices affect the five CALMS principles — for example, more automation can require setup effort and tighter gates can affect lead time. This skill evaluates those effects across building, auditing, and improving pipelines, and records the resulting design decisions.

## Scope and handoff

Use this skill for the delivery system's design and improvement. Infrastructure service-selection and Well-Architected choices belong to `infra-decisions`; failed runs, operational Terraform work, incidents, recovery checks, and SRE reliability reviews belong to `devops-operations`. For a failed workflow plus a request to redesign promotion, let operations establish the failure evidence first, then evaluate the lasting pipeline change here. A routine operational repair does not require CALMS scoring or a decision record.

## Steps

1. **Frame the engagement** — name the mode (build / audit / optimize), the application or service in scope, its deployment target(s), and the hard constraints (compliance, existing tooling, org maturity, deadline). Done when someone who wasn't in the conversation could tell which mode this is and what's being decided.

2. **Do the mode's legwork** — before recommending anything, gather what the mode needs:
   - **Build** — the application's architecture, tech stack, deployment targets, security/compliance requirements, and the org's existing workflows.
   - **Audit** — walk every dimension in [`AUDIT-DIMENSIONS.md`](AUDIT-DIMENSIONS.md); mark each pass / risk / gap / unknown with evidence. Unknown means required evidence is unavailable.
   - **Optimize** — gather the specific complaint and available DORA baseline for the application or service: change lead time, deployment frequency, failed deployment recovery time, change fail rate, and deployment rework rate. Record the measurement window and missing measurements; do not invent values or equate general incident MTTR with recovery from a failed deployment. See [DORA's metric definitions](https://dora.dev/guides/dora-metrics/).

   Done when every item for the active mode carries an explicit finding or a named evidence gap.

3. **Score against CALMS** — state the baseline, then assess each principle as up, down, neutral, or unknown with evidence and a short reason. Neutral means no material difference; unknown means evidence is missing. Address all five, explaining any non-applicable area. For an audit of the current system, assess the recommendation against the current design and keep the dimension findings separate. Consult [`CALMS.md`](CALMS.md) when interpreting a principle. Done when all five have a supported assessment or an explicit evidence gap.

   - **Culture** — shared ownership of the pipeline and blameless response to failure, versus a single gatekeeper team.
   - **Automation** — pipeline, infrastructure, and policy as code; how much still needs a human hand.
   - **Lean** — change size and frequency; how much waste sits between a commit and production.
   - **Measurement** — visibility into the DORA metrics baseline and pipeline health.
   - **Sharing** — how legible the pipeline's standards and decisions are to the next engineer.

4. **Prioritize the recommendation** — order findings or recommendations by business value against engineering effort, and name which CALMS principle each serves. State the accepted costs, risks, and any deferred work. If no material downside or deferral is supported by the evidence, say so; prioritization does not require inventing one.

5. **Record it** — write a short markdown file with mode, scope, evidence, CALMS assessment, prioritized recommendations, and accepted trade-offs. Reuse an existing decisions location in the repo if one exists (e.g. `docs/adr/`, `docs/decisions/`, `docs/architecture-decisions/`, `docs/pipeline-decisions/`); otherwise create `docs/pipeline-decisions/` and name the file `YYYY-MM-DD-<slug>.md`. Distinguish proposed recommendations from accepted decisions, and record evidence gaps with next actions. Done when decision status and concrete next actions are clear. Recording a pipeline decision does not authorize workflow reruns, deployments, or live infrastructure changes.
