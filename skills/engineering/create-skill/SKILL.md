---
name: create-skill
description: Create or update a skill in the vincentory repository while keeping manifests and documentation synchronized
argument-hint: "<skill-name> [engineering|productivity|in-progress]"
disable-model-invocation: true
---

# Create Skill

Helps maintainers create or update a skill inside the `vincentory` repository while keeping all manifests and documentation consistent.

## Arguments

- `skill-name` (required): a kebab-case identifier for the skill.
- `bucket` (optional): one of `engineering`, `productivity`, `in-progress`. Defaults to `in-progress`.

## Workflow

### 1. Validate the skill name

- Must match `^[a-z0-9]+(-[a-z0-9]+)+$` (at least two kebab-case segments).
- Reject ambiguous names, names with uppercase letters, underscores, or spaces.
- If the name is invalid, stop and ask the user to correct it before continuing.

### 2. Resolve the target bucket

- If the user supplied a bucket, verify it is one of `engineering`, `productivity`, `in-progress`.
- `deprecated` is not a valid target for new skills; reject it.
- If no bucket was supplied, default to `in-progress` and tell the user explicitly.

### 3. Collect skill intent

Before writing `SKILL.md`, confirm or derive the following. If the user has not stated any of these, ask — do not invent them:

- **Purpose**: what specific task or situation triggers this skill?
- **Invocation model**: is this user-invoked (`disable-model-invocation: true`) or model-invoked (model decides when to run it)?
- **Allowed tools**: which tools or capabilities does the skill need? Restrict to the minimum set.
- **Success criteria**: what does correct completion look like?
- **Forbidden behaviors**: what must the skill never do (destructive ops, secret leakage, guessing values)?

### 4. Create the skill directory and SKILL.md

Target path: `skills/<bucket>/<skill-name>/SKILL.md`

Frontmatter must include at minimum:

```yaml
---
name: <skill-name>
description: <one sentence describing trigger and capability>
---
```

- If user-invoked, add `disable-model-invocation: true`.
- If the skill accepts arguments, add `argument-hint: "<usage>"`.
- Keep the body focused on the concrete workflow: steps, checks, and outputs. Do not pad with generic advice.
- The skill must be understandable and usable in isolation — no implicit dependencies on other skills.

### 5. Update bucket README

Open `skills/<bucket>/README.md` and add the new skill to the appropriate list:

- `engineering` and `productivity`: split between User-invoked and Model-invoked sections.
- `in-progress`: append to the simple list.

### 6. Handle publishing manifests

If the bucket is `engineering` or `productivity` (a published bucket):

- Add the skill path to the `skills` array in `.claude-plugin/plugin.json`. The path must be `"./skills/<bucket>/<skill-name>"`.
- Add an entry for the skill in the root `README.md` under the published skills list, linking to the `SKILL.md`.

If the bucket is `in-progress` (or `deprecated`):

- Do **not** modify `.claude-plugin/plugin.json`.
- Do **not** add the skill to the root `README.md` published list.
- Make this explicit to the user.

### 7. Validate

After modifying `.claude-plugin/plugin.json`, run:

```bash
claude plugin validate . --strict
```

If the `claude` command is unavailable or validation fails, show the real error — do not fabricate success.

### 8. Post-creation checklist

Before reporting completion, verify:

- [ ] Directory name matches `name` in frontmatter.
- [ ] `SKILL.md` frontmatter is valid YAML.
- [ ] The skill appears in the bucket README.
- [ ] If published: the skill appears in `.claude-plugin/plugin.json` `skills` array.
- [ ] If published: the skill appears in the root `README.md` list.
- [ ] If not published: the skill does NOT appear in `plugin.json` or root README.

Do **not** run `git commit` unless the user explicitly asks.

## Notes

- Prefer small, composable skills. If the new skill overlaps significantly with an existing one, flag this before proceeding.
- Avoid encoding project-specific conventions into a skill unless the skill is explicitly scoped to that project.
- Do not write secrets, tokens, emails, or environment-specific values into any skill file.
