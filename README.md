# vincentory

A curated collection of reusable agent skills for engineering and productivity workflows.

`vincentory` is both a **Claude Code Plugin** and a **single-plugin Marketplace**. Install it to get disciplined, composable skills that help with day-to-day development work.

## Design principles

- **Small and focused**: each skill does one thing well.
- **Composable**: skills can be combined without hidden dependencies.
- **Maintainable**: clear bucket boundaries, synchronized manifests, and explicit publishing rules.
- **Safe by default**: no destructive operations, no secret leakage, no guessing user intent.

## Installation

### From GitHub Marketplace

```text
/plugin marketplace add wesuper/vincentory
/plugin install vincentory@vincentory
```

> CLI equivalents (verify against your installed Claude Code version — command support may vary):
>
> ```bash
> claude plugin marketplace add wesuper/vincentory
> claude plugin install vincentory@vincentory
> ```

### Local installation for testing

```text
/plugin marketplace add .
/plugin install vincentory@vincentory
```

## Usage

Invoke a skill via the `/vincentory:` prefix:

```text
/vincentory:create-skill my-new-skill engineering
```

## Skill categories

| Bucket | Status |
|---|---|
| [engineering](skills/engineering/README.md) | Published |
| [productivity](skills/productivity/README.md) | Published |
| [in-progress](skills/in-progress/README.md) | Not published |
| [deprecated](skills/deprecated/README.md) | Not published |

## Published skills

### Engineering

- [create-skill](skills/engineering/create-skill/SKILL.md) — Create or update a skill in the vincentory repository while keeping manifests and documentation synchronized.

### Productivity

_No published productivity skills yet._

## Local development

### Link skills for global use

Symlink published skills into `~/.claude/skills/` so they are available outside this repository:

```bash
./scripts/link-skills.sh
```

### Edit skills directly

Skills live at `skills/<bucket>/<skill-name>/SKILL.md`. Edit the file, then re-run validation if the change affects a published skill.

## Creating a new skill

Use the `create-skill` skill itself:

```text
/vincentory:create-skill my-new-skill engineering
```

Or manually:

1. Create `skills/<bucket>/<skill-name>/SKILL.md` with valid frontmatter.
2. Update the bucket `README.md`.
3. If the bucket is `engineering` or `productivity`:
   - Add the path to `.claude-plugin/plugin.json`'s `skills` array.
   - Add the skill to the root `README.md` published skills list.
4. Run validation (see below).

## Plugin validation

```bash
claude plugin validate . --strict
# or
npm run validate
```

If the `claude` command is unavailable or the subcommand is unsupported, record the error. Do not skip publishing invariants checks manually.

## Release and version updates

1. Update `version` in both `.claude-plugin/plugin.json` and `package.json`.
2. Add a dated section in `CHANGELOG.md`.
3. Tag the release in Git.

## Contributing

This is a personal repository. If you are reading this and want to contribute, open an issue to discuss before sending a PR.

All changes to published skills must preserve the [publishing invariants](CLAUDE.md#publishing-invariants) documented in `CLAUDE.md`.

## License

MIT — see [LICENSE](LICENSE).
