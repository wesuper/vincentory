# vincentory

A curated collection of reusable agent skills for engineering and productivity workflows.

`vincentory` is both a **Claude Code Plugin** and a **single-plugin Marketplace**. Install it to get disciplined, composable skills that help with day-to-day development work.

## Design principles

- **Small and focused**: each skill does one thing well.
- **Composable**: skills can be combined without hidden dependencies.
- **Maintainable**: one flat directory per skill, synchronized manifests, and explicit publishing rules.
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
/vincentory:h5-report-generator
```

## Structure

Every skill lives directly under `skills/` as `skills/<skill-name>/SKILL.md` — the layout Claude Code auto-discovers, with no intermediate category level. Anything under `skills/` ships with the plugin, so work-in-progress skills belong outside this repository (or in a branch), not in an unpublished subdirectory.

## Published skills

- [h5-report-generator](skills/h5-report-generator/SKILL.md) — 企业级 HTML5 幻灯片演示系统生成器。当用户需要生成汇报材料、H5 演示文稿、网页版幻灯片，或明确要求"H5格式"、"网页版PPT"时使用。结论先行信息架构（封面结论胶囊、目录每章结论+要点、页面结论条）、顶部进度条、ECharts/Mermaid 图表、PC 端投屏优化，5-30 页幻灯片。

## Local development

### Link skills for global use

Symlink published skills into `~/.claude/skills/` so they are available outside this repository:

```bash
./scripts/link-skills.sh
```

### Edit skills directly

Skills live at `skills/<skill-name>/SKILL.md`. Edit the file, then re-run validation.

## Creating a new skill

Use the built-in `skill-creator` skill to scaffold and iterate on a new skill, then wire it into this repository:

1. Create `skills/<skill-name>/SKILL.md` with valid frontmatter (directory name must equal `name`).
2. Add the path to `.claude-plugin/plugin.json`'s `skills` array.
3. Add the skill to the published skills list above.
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
