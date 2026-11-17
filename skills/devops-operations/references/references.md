# Design and operational references

These links informed the workflow design. The harness instructions are original prose; they do not embed vendor code or require a hosted agent, paid service, model account, or MCP server. Product capabilities and access requirements can change. Consult the source relevant to the current task instead of treating an example or product default as local policy.

## Investigation and coordination

- [AWS DevOps Agent skills](https://docs.aws.amazon.com/devopsagent/latest/userguide/about-aws-devops-agent-devops-agent-skills-index.html): focused operational procedures, supporting references, and clear activation criteria. AWS Agent Spaces are a separate runtime, not a prerequisite for this skill.
- [Google Cloud Assist investigations](https://docs.cloud.google.com/cloud-assist/investigations): evidence, alternative hypotheses, and iterative investigation revisions. Use the method as a reference; service access is subject to Google's current requirements.
- [Azure SRE Agent run modes](https://learn.microsoft.com/en-us/azure/sre-agent/run-modes): distinguish permission to reach a resource from approval to execute an action. This harness follows the user's current authorization, not Azure's product defaults.
- [Google SRE: Effective Troubleshooting](https://sre.google/sre-book/effective-troubleshooting/): form and test explanations rather than collecting unrelated observations.

## Reliability and verification

- [Google SRE: Monitoring Distributed Systems](https://sre.google/sre-book/monitoring-distributed-systems/): user-facing health and the golden signals.
- [Google SRE Workbook: Implementing SLOs](https://sre.google/workbook/implementing-slos/): choose service objectives from user needs and validate their implementation.
- [ECS rolling deployments](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/deployment-type-ecs.html): service deployment mechanics; inspect the actual service strategy before applying them.
- [Terraform plan](https://developer.hashicorp.com/terraform/cli/commands/plan): planning behavior and sensitive plan artifacts. [State locking](https://developer.hashicorp.com/terraform/language/state/locking) explains why a lock is not an invitation to force-unlock.

## Proactive monitoring versus interactive work

- [Versus SRE agent](https://docs.versusincident.com/#/agent/agent-introduction): separate baseline learning, shadow review, and incident detection.
- [Versus Analyze](https://docs.versusincident.com/#/agent/ai-analyze-mode) and [tools](https://docs.versusincident.com/#/agent/tools/overview): bounded evidence gathering, retained analyses, and a clear distinction between recommendations and executed changes.
- [Versus source and license](https://github.com/VersusControl/versus-incident): implementation reference for a continuously running service. The portable skill does not reproduce its detector or imply monitoring continues when an interactive session ends.

Borrowing a design principle does not install the referenced system. If future work copies code or substantial text, review that source's license and retain the required notices in the contribution.
