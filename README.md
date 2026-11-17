# Architecture & Operations Skills

Portable skills for architecture decisions, CI/CD, Terraform, incident response, and SRE reliability work across Codex, Claude Code, and Antigravity. Use installed CLIs and native agent tools; no hosted DevOps service or MCP connection is required.

Current plugin version: **1.1.0**. The plugin identifier remains `architecture-decisions` for compatibility; the repository is now `eenlpe1/architecture-operations-skills`.

## Skills and routing

| Skill | Use when | Outcome |
| --- | --- | --- |
| [infra-decisions](skills/infra-decisions/SKILL.md) | Compare AWS architectures or perform a Well-Architected assessment | Evidence-backed recorded decision or assessment |
| [devops-decisions](skills/devops-decisions/SKILL.md) | Design, audit, or improve a delivery pipeline | CALMS/DORA assessment and recorded proposed or accepted choices |
| [devops-operations](skills/devops-operations/SKILL.md) | Investigate failures, resolve operational issues, review Terraform, verify deployments, or assess reliability | Evidence, authorized actions, verified outcomes, and a resumable private handoff |

All three support automatic selection when their descriptions match the request. Selection depends on the host model and configuration; it is not an event listener or a guarantee. Explicit invocation remains available. Incident recovery leads a mixed request; a decision skill joins when a lasting design choice needs evaluation. Ordinary incidents do not require an ADR or framework scorecard.

## Operations coverage

- GitHub Actions failures/skips, release promotion, artifacts, migrations, ECS/ECR rollout and health verification.
- Terraform target/backend/workspace checks, validation, plan/drift review, failed runs, and authorized state/infrastructure work.
- Hypothesis-led investigation across configuration, recent changes, logs, metrics, and dependencies.
- On-demand reliability reviews: actual SLIs/SLOs and error budgets, alert quality, capacity, recurring incidents, and prevention work.
- Recovery polling during an active session: default 30-second cadence and 15-minute budget, with honest failure/timeout reporting.
- One coordinator, independent read-only collectors where native delegation exists, and one owner for changes. Sequential operation works too.

Local fixes and validation follow task scope. Cloud mutations, workflow reruns/deployments, state changes, and external messages require specific authorization; existing authorization is reused within scope. This package does not start a daemon, schedule checks, send alerts, or install cloud credentials.

## Prerequisites

Install and authenticate your chosen coding agent first. Global setup requires Python 3.10+, Git, and local `SKILL.md` discovery support. Operational tools are needed only for the workload being investigated:

| Workload | Tools and access |
| --- | --- |
| GitHub Actions and releases | `gh` authenticated to the target repository, plus local Git |
| AWS infrastructure and ECS | AWS CLI with an appropriate profile/SSO session and access to the target account |
| Terraform | The repository's Terraform version, provider configuration, backend access, and environment inputs |
| Service reliability | Access to the service's existing logs, metrics, health checks, and runbooks |

The skills discover available tools and report missing access. Installing them does not install these CLIs, authenticate accounts, or grant permissions.

## Global installation from a checkout

For one shared installation across Codex, Claude Code, and Antigravity, review the skills and installer, then run:

```sh
git clone https://github.com/eenlpe1/architecture-operations-skills.git
cd architecture-operations-skills
python3 scripts/install-global.py
python3 scripts/install-global.py --check
```

The installer links this checkout's skills into `~/.agents/skills`, shares the whole existing library with `~/.claude/skills`, and configures Antigravity's `~/.gemini/config/skills.json` with an absolute shared-library path. It preserves unrelated entries/settings and refuses conflicting skill paths. Changed manifests receive private backups beside the original. Fully redundant legacy alias-directory entries are collapsed to avoid duplicate discovery; filtered entries are retained.

Start a new agent session after installation so its skill catalog is refreshed. The skills apply across projects for the current OS user; other users and remote/cloud environments need their own installation. Keep the checkout at its installed location because global links point to its files. See [Updating a checkout installation](#updating-a-checkout-installation) after new changes merge.

To relocate a checkout, explicitly remove only its installer-created links before installing from the new path. Do not delete shared skill directories containing other skills.

The installer changes user-level skill discovery only; it does not install/remove plugins or alter AWS credentials. Rerun it after adding shared skills. `--check` is read-only; `--home` exists for isolated tests.

## Updating a checkout installation

From the checkout used for global installation, first ensure the working tree is clean. Commit or stash your own changes before switching branches. Fetch the merged code and fast-forward local `main`:

```sh
git fetch origin
git switch main
git merge --ff-only origin/main
python3 scripts/install-global.py
python3 scripts/install-global.py --check
```

The existing links immediately reference the checkout's updated files. Rerunning the installer exposes any newly added skills and refreshes discovery configuration; `--check` verifies it without changes. Start a new agent session to load the updated catalog and instructions.

Keep the globally linked checkout on `main` for normal use. Use a separate development checkout or worktree when experimenting: global links also expose uncommitted files and branch changes. If fast-forwarding fails, resolve the local divergence before retrying; this update procedure does not reset or discard work.

## Plugin installation

As an alternative to checkout links, Codex and Claude Code can use plugin packaging. Choose one installation path per client to avoid duplicate discovery.

Codex:

```sh
codex plugin marketplace add eenlpe1/architecture-operations-skills
codex plugin add architecture-decisions@eenlpe1
```

Claude Code:

```text
/plugin marketplace add eenlpe1/architecture-operations-skills
/plugin install architecture-decisions@eenlpe1
/reload-plugins
```

Start a new Codex thread. For updates, refresh the `eenlpe1` marketplace and reinstall the plugin using the client's plugin commands. If the marketplace was registered under the former repository URL, update its source to the renamed repository first. Antigravity uses the global checkout installation above.

## Example requests

- “The workflow is green but the backend was skipped. Find the broken release step.”
- “This ECS task cannot retrieve a secret. Investigate without changing infrastructure.”
- “Review this Terraform replacement plan and confirm the target environment.”
- “Monitor the deployment we authorized and verify backend and frontend health separately.”
- “Review this service's error budget and noisy alerts using its existing objectives.”
- “Compare infrastructure options and record the trade-offs.”

Explicit local skill names are `devops-operations`, `devops-decisions`, and `infra-decisions`; plugin installs namespace them with `architecture-decisions:`. Use the host's supported skill picker or invocation syntax.

## Private context

Operations creates private project mappings and case records under `~/.local/share/devops-operations/` when needed. Keep credentials, state/plan files, and raw sensitive evidence out of that record and out of public issues. A resumed session rechecks live identity and state. See [private context](skills/devops-operations/references/context.md).

## Development and validation

Canonical content lives under `skills/`; client manifests package the same files. See [CONTRIBUTING.md](CONTRIBUTING.md), [repository guidance](AGENTS.md), [offline evaluation](tests/README.md), and the [validation record](docs/validation.md).

```sh
python3 scripts/validate.py
python3 -m unittest discover -s tests
```

Run the Codex skill/plugin validators when available and `git diff --check` before opening a PR. Behavioral evaluations use sanitized fixtures; static validators do not prove model routing or live cloud correctness. No cloud deployment is part of validation.

## References and license

The new operational procedures are original, informed by [primary references](skills/devops-operations/references/references.md). Reference products are not dependencies or promises of equivalent hosted functionality. This repository is [MIT licensed](LICENSE). Preserve upstream attribution/license obligations if copying external material.
