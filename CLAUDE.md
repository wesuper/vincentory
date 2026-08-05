# CLAUDE.md — vincentory repository rules

## Repository purpose

`vincentory` is a personal Agent Skills repository. It is simultaneously:

- A **Claude Code Plugin** installable via `.claude-plugin/plugin.json`
- A **single-plugin Claude Code Marketplace** defined in `.claude-plugin/marketplace.json`
- The source of truth for skill development, versioned via Git

The repository root is the plugin root. Do not create nested plugin directories.

## Skill buckets

| Bucket | Meaning | Published to plugin |
|---|---|---|
| `skills/engineering/` | Day-to-day software engineering skills | Yes |
| `skills/productivity/` | General workflow and productivity skills | Yes |
| `skills/in-progress/` | Work in progress, experiments | No |
| `skills/deprecated/` | Retired, no longer maintained | No |

## Publishing invariants

For every skill in `engineering` or `productivity` (published buckets), all three must hold:

1. The skill is listed in the corresponding bucket's `README.md`
2. The skill is listed in the root `README.md` published skills list
3. The skill path is present in the `skills` array of `.claude-plugin/plugin.json`

For every skill in `in-progress` or `deprecated`:

- It must NOT appear in `.claude-plugin/plugin.json`'s `skills` array
- It must NOT appear in the root `README.md` published skills list

Violating these invariants is a bug. The validation step should catch it.

## Skill conventions

- Each skill lives in its own directory named in kebab-case.
- The entry file is `SKILL.md`.
- The directory name must match the `name` field in the YAML frontmatter.
- `description` must describe both the trigger situation and the specific capability.
- Skills must declare whether they are user-invoked (`disable-model-invocation: true`) or model-invoked. If unset, the model may invoke the skill automatically.
- Skills should be small, focused, composable, and independently testable.
- Do not write secrets, tokens, API keys, emails, or environment-specific values into any skill file.
- Do not execute destructive operations unless the user has explicitly authorized them.

## Manifest synchronization

When adding, moving, renaming, or deleting a published skill, update all three of:

- `.claude-plugin/plugin.json` (`skills` array)
- Root `README.md` (published skills list)
- The corresponding bucket's `README.md`

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
