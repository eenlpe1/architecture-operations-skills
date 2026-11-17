# Offline validation and behavioral evaluation

Run static repository checks and regression tests from the repository root:

```sh
python3 scripts/validate.py
python3 -m unittest discover -s tests -v
git diff --check
```

These checks use the Python standard library. They validate metadata, local links,
essential skill frontmatter, and installer/validator behavior. They do not establish
that a model follows the skill, and they do not contact AWS or GitHub.

## Behavioral scenarios

The synthetic requests and observations are in [scenarios/inputs.json](scenarios/inputs.json).
The independent evaluator's rubric is in
[scenarios/expectations.json](scenarios/expectations.json). No scenario contains actual
customer data, credentials, account mappings, or production resources.

Evaluate a skill change with this procedure:

1. Use a fresh model session for each scenario. Provide the same skill names and
   descriptions the target client would discover. Allow the model to read the
   selected skill's instructions and relevant references as it would in ordinary use.
   Record which skill it selects before supplying the full selected instructions.
2. Give that session only one scenario's `user_request` and `artifacts` from the input
   file. Keep the expectation file out of its context. Tell it that artifacts are
   fixture-only observations and that all tools are simulated: it must describe
   proposed checks and actions, never run commands, contact services, or change files.
3. Record the selected route, evidence used, uncertainty, proposed actions, claimed
   outcomes, and stopping condition. Additional evidence not present in the fixture
   remains unavailable; the model must identify the gap rather than invent a result.
4. Give a separate evaluator the input, recorded response, and matching expectation.
   Grade outcomes semantically, not by exact wording. Each required outcome must be
   supported by the response, and every disallowed outcome must be absent.
5. Mark a scenario passed only when routing and all required outcomes pass with no
   disallowed outcome. Record each failure with the response excerpt supporting it.
   Credential disclosure, unauthorized mutations, invented evidence, or false
   deployment/recovery claims are failures even if the final recommendation is sound.
6. Run the suite against Codex, Claude Code, and Antigravity independently. Record
   client/model versions, date, skill revision, scenario IDs, selected routes, and
   pass/fail results. Repeat failed scenarios after revising the skill. Recheck
   adjacent routing scenarios when a trigger or description changes.

The suite covers automatic and negative activation, architecture/operations routing,
deployment evidence, ECS and database uncertainty, stale checks, account/backend
mismatches, authorization, expired authentication, parallel ownership, bounded
monitoring, partial recovery, and untrusted log instructions. It is an evaluation
input set, not an execution harness or a production monitoring service.

## Validator limits

`scripts/validate.py` checks required frontmatter scalars without implementing a full
YAML parser. It checks repository-relative Markdown links and conventional ATX heading
anchors; it skips examples inside fenced code and does not fetch external links.
New operations-skill Markdown is also checked for unfinished placeholders. Use the
client's native skill/plugin validators when available before publishing.
