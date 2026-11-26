# Presentation Content Architect

独立 Claude Code Skill，入口 [SKILL.md](SKILL.md)。

- 输入：一句话、提纲、对话或材料。
- 输出：渲染器中立的 `presentation.md`、讲者备注、`sources.md`、`handoff.json`，以及 `outline.md`、`claim-map.json`、`working-state.json`。
- 契约：[references/presentation-contract.md](references/presentation-contract.md)。
- 默认输出位置：当前项目 `presentations/<slug>/`。
- 校验：在交付目录运行 `python3 <skill-path>/scripts/validate_content.py presentation.md handoff.json working-state.json`；`<skill-path>` 是本 Skill 目录的绝对路径。

本 Skill 不生成 HTML/CSS；只把内容文件路径交给下游渲染 Skill。
