# CLAUDE.md — vincentory repository rules

## Repository purpose

`vincentory` is a personal Agent Skills repository. It is simultaneously:

- A **Claude Code Plugin** installable via `.claude-plugin/plugin.json`
- A **single-plugin Claude Code Marketplace** defined in `.claude-plugin/marketplace.json`
- The source of truth for skill development, versioned via Git

The repository root is the plugin root. Do not create nested plugin directories.

## Directory layout

```text
skills/
└── <skill-name>/
    └── SKILL.md
```

Each skill sits **directly** under `skills/`, one directory per skill. There is no category layer: `skills/engineering/foo/` is not a Claude Code concept and must not be reintroduced.

**Why:** Claude Code auto-discovers `skills/<name>/SKILL.md` at exactly one level. Nested skills are only loaded when their path is listed in `plugin.json`, and an omission there fails silently — the skill simply never appears. A flat namespace also matches every official plugin (`superpowers`, `claude-md-management`, …), whose manifests carry no `skills` field at all.

> A category layer is not a valid "not published" mechanism either. Everything under `skills/` ships with the plugin, whether or not it is listed in `plugin.json`. Work-in-progress skills belong outside this repository or on a branch.

## Publishing invariants

For every skill in `skills/`, both must hold:

1. The skill is listed in the root `README.md` published skills list
2. The skill path is present in the `skills` array of `.claude-plugin/plugin.json`

Violating these invariants is a bug. The validation step should catch it.

## Skill conventions

- Each skill lives in its own directory named in kebab-case.
- The entry file is `SKILL.md`.
- The directory name must match the `name` field in the YAML frontmatter.
- `description` must describe both the trigger situation and the specific capability.
- Skills must declare whether they are user-invoked (`disable-model-invocation: true`) or model-invoked. If unset, the model may invoke the skill automatically.
- Skills should be small, focused, composable, and independently testable.
- Use the built-in `skill-creator` skill for authoring; do not ship a repository-local skill whose only job is to create other skills.
- Do not write secrets, tokens, API keys, emails, or environment-specific values into any skill file.
- Do not execute destructive operations unless the user has explicitly authorized them.

## Manifest synchronization

When adding, moving, renaming, or deleting a skill, update both of:

- `.claude-plugin/plugin.json` (`skills` array)
- Root `README.md` (published skills list)

When changing the version, update all three of:

- `.claude-plugin/plugin.json` (`version`)
- `package.json` (`version`)
- `CHANGELOG.md` (new section)

## Validation

After modifying `.claude-plugin/plugin.json`, run:

```bash
claude plugin validate . --strict
```

If the `claude` CLI is unavailable or the command is unsupported in the installed version, record the reason and the raw error. Do not fabricate a success result.

> `claude plugin validate` checks that every path in the `skills` array exists, but it does **not** validate the frontmatter of skills reached through that path. Check `name`/`description` by reading the file.
