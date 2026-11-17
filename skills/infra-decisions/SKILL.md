---
name: infra-decisions
description: Compare AWS infrastructure architectures or audit a workload against the six Well-Architected pillars, and record the decision. Use for lasting service-selection and infrastructure design choices. For a failing deployment, Terraform error, or live service incident, start with devops-operations.
---

# Infra Decisions

AWS infrastructure choices can trade reliability, security, performance, cost, sustainability, and operational effort against each other. This skill evaluates the evidence for those trade-offs and leaves behind a record of the decision.

## Scope and handoff

Use this skill for infrastructure architecture decisions and Well-Architected audits. Pipeline design belongs to `devops-decisions`; incident investigation, operational Terraform work, recovery checks, and SRE reliability reviews belong to `devops-operations`. If a request combines an incident and a redesign, let operations establish the incident facts first, then evaluate the lasting infrastructure choice here. An incident alone does not require an architecture decision record.

## Steps

1. **Frame the engagement** — name comparison or audit mode, the workload, the question, and the hard constraints (budget, compliance, existing architecture, deadline). For a comparison, name realistic options, including keeping the current design when viable, and the baseline used to judge them. For an audit, establish the current design and available evidence before proposing changes; an audit does not require invented alternatives. Done when the mode, scope, and evaluation baseline are explicit.

2. **Score every pillar** — for a comparison, assess each option against the stated baseline: up, down, neutral, or unknown, with evidence and a short reason. For an audit, mark each pillar pass, risk, gap, or unknown. Use unknown for missing evidence; neutral means evidence supports no material difference. Address every pillar, explaining any non-applicable area. Consult [`PILLARS.md`](PILLARS.md) when interpreting a pillar. Done when all six pillars have an evidence-backed assessment or an explicit evidence gap.

   - **Operational Excellence** — running and monitoring systems, and continually improving process: automating changes, responding to events, defining standards for daily operations.
   - **Security** — protecting data and systems: confidentiality and integrity of data, managing permissions, detecting security events.
   - **Reliability** — a workload performing its function and recovering quickly from failure: distributed system design, recovery planning, adapting to changing demand.
   - **Performance Efficiency** — structured, streamlined use of compute resources: picking resource types and sizes for the workload, monitoring performance, staying efficient as demand and technology evolve.
   - **Cost Optimization** — avoiding unnecessary spend: understanding spend over time, controlling fund allocation, right-sizing and right-quantity resources, scaling to match business need.
   - **Sustainability** — minimizing the environmental impact of running workloads: the shared responsibility model for sustainability, understanding impact, maximizing utilization per unit of work.

3. **State the trade-off** — identify the priorities, evidenced downsides, and remaining uncertainty. A change can improve several pillars without a demonstrated regression; say so rather than inventing a sacrificed pillar. For an audit, prioritize the findings and state which risks remain accepted or unresolved. Done when the recommendation and its known limits are explicit.

4. **Record it** — write a short markdown file with mode, scope, evidence, six-pillar assessment, recommendation or chosen option, and accepted trade-offs. Reuse an existing decisions location in the repo if one exists (e.g. `docs/infrastructure/`, `docs/adr/`, `docs/decisions/`); otherwise create `docs/architecture-decisions/` and name the file `YYYY-MM-DD-<slug>.md`. Distinguish a proposed recommendation from an accepted decision; if evidence is insufficient, record the unresolved question and next evidence needed. Done when the record accurately states the decision status and concrete next actions. Recording a decision does not authorize provisioning or changing live infrastructure.
