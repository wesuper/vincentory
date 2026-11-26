---
name: presentation-content-architect
description: Use when a user brings a vague idea, outline, meeting notes, chat transcript, or reference material and needs a defensible presentation script, argument structure, speaker notes, or renderer-neutral content handoff; use before HTML/PPT rendering, when a claim lacks evidence, or when a revision must preserve prior decisions and slide IDs. Not for layout or CSS.
---

# Presentation Content Architect

## Overview

把原始输入变成**可被任何渲染器消费的内容真源**：完整演示稿、讲者备注、证据台账和交接索引。核心原则：内容结构与展示模板分离；先明确问题和主张，再扩写正文；每个结论都能追溯到事实、推断或显式假设。

**适用信号**：用户说“讲清楚 / 汇报 / 说服 / 做个汇报 / 帮我搭结构 / 逐页写稿 / 补演讲备注 / 换角度改稿”，或手上有提纲、对话记录、材料却不知道怎么组织。用户只要一份简单提纲且没有论证或证据要求时，直接写即可，不必启动完整状态机。

## 硬边界

- 本 Skill 生产 **Markdown 内容**，不生产 HTML、CSS、主题色、模板类名或图表实现代码。用户同时要求投屏页面时，把最终 `presentation.md` 和 `handoff.json` 的本地路径交给渲染 Skill，不自行拼页面。报告交接前先确认这两个文件存在；不要承诺已生成任何未创建的文件。
- 不得把 `hypothesis / unverified / disputed` 写成事实，不得编造来源、数字、客户案例或专家观点。无来源时保留限定条件；用户要求“别写待核实”时，改写为正向的稳健表述（如“不承诺效益数字，用基线验证”），并在 `Evidence` 和 `sources.md` 中保留真实状态。
- `Visual Intent` 只是卡片、对比、时间轴等语义建议，不绑定任何主题的组件名或样式。

## 工作流（复制为任务清单逐项推进）

```
Content Progress:
- [ ] 1. 归档输入：区分用户明确事实、用户观点、待验证假设、未知信息
- [ ] 2. 问题定义：展示第一版骨架；只问 1 个最能改变结论的问题
- [ ] 3. 建 claim-map.json 与 outline.md：每页一个独立主张
- [ ] 4. 扩写 presentation.md 与 sources.md：逐页填写契约字段
- [ ] 5. 生成 handoff.json 与 working-state.json：顺序、状态、未决问题一致
- [ ] 6. 运行 scripts/validate_content.py；按错误回改，直到通过
```

**Step 1 — 归档输入**
读取用户输入及已有工作目录；把每句话归入：明确事实 / 用户观点 / 待验证假设 / 未知信息。冲突时以用户当前指令优先，旧材料与本次指令的差异记入 `working-state.json`。不要从随口猜测中制造已确认决策。

**Step 2 — 问题定义与唯一提问**
先给用户可编辑的骨架，再问**一个**最能改变结论的问题；根据回答更新判断，必要时再问下一个，最多 6 个有意义的问题，信息足够立即停止。以下情形可跳过提问，直接用显式假设继续：用户明确说“直接生成 / 先出稿 / 时间紧”；输入已包含受众、目标、时长与决策事项；用户要求继续上一轮且已有工作文件。跳过时把假设写入 `working-state.json.assumptions`，并在 `outline.md` 标出尚待确认项。不得用“问题看起来很小”作为跳过理由。

**Step 3 — 骨架**
先写 `claim-map.json`（主张、分论点、证据 ID、状态、对应页），再写 `outline.md`（章节、每页唯一结论、需要补强的证据）。每轮只更新受影响的论点或页面，保留已确认结论。方法按需选择，不为凑数全用：读取 [references/method-router.md](references/method-router.md) 按“真实缺口 → 方法 → 停止条件”选择，在每轮“更新摘要”中写出确认事实、改变的判断、待验证问题、下一步建议。专家会诊只是角色模拟，纵横研究只有在有来源时才可做事实结论，跨领域类比不等于证据。

**Step 4 — 扩写**
按 [references/presentation-contract.md](references/presentation-contract.md) 写 `presentation.md`：`#` 结论标题、`> Takeaway:`、`## Visible`、`## Evidence`、`## Visual Intent`、`## Speaker Notes`（Purpose / 2–4 条 Talk，每条 ≤40 字 / Transition / Minutes）。封面、目录、收尾同样有 slide_id 和备注。正文必须独立可理解；备注补充背景、故事、异议和转场，不照读正文。重要数字和引文写入 `sources.md`，逐条标来源与事实状态。

**Step 5 — 交接与进度**
`handoff.json` 的 `slides[]` 顺序必须与 `presentation.md` 完全一致，含 slide_id、role、title、visual_intent、speaker_notes_present；`readiness` 取 `ready / needs_review / blocked`。`working-state.json` 记录 stage、revision、confirmed、assumptions、open_questions、decision_log 和 slide_maturity。提供 h5-report-generator 时读取 [references/h5-adapter.md](references/h5-adapter.md) 做语义适配；主题只写在 adapter 区，不改变正文。未提供模板时照常独立交付。

**Step 6 — 校验与循环**
在六个交付文件所在目录运行；`<skill-root>` 替换为包含本 `SKILL.md` 的目录绝对路径，三个产物路径相对当前输出目录（产物在其他目录时改为对应路径）：

```bash
python3 "<skill-root>/scripts/validate_content.py" presentation.md handoff.json working-state.json
```

脚本检查 slide_id 唯一且有序、契约字段齐全、Talk 2–4 条且每条 ≤40 字、每页恰好一个 `Minutes:` 且合计不超过用户上限的 90%，以及机器可判定的 READY 条件：`status / readiness / stage` 一致、`open_questions` 与 `unresolved` 为空、字段枚举合法。脚本的 `ok: true` **只代表这些机械检查通过**，不证明证据质量、下游渲染或其他人工门禁。脚本失败时按错误定位到具体页面或状态文件修订后重跑；脚本通过也需人工核对 [references/quality-gates.md](references/quality-gates.md)。

## 状态机与 READY 门禁

`INTAKE → QUESTION_DEFINED → SKELETON → ENRICHED → REVIEW → READY`，用户可要求回到任意阶段。每轮把进度写入 `working-state.json`，不是只在聊天里说明。

只有同时满足以下条件才把 `presentation.md.status` 和 `handoff.json.readiness` 标为 READY / ready：

1. 受众、目标、期望行动明确，或在 assumption 中显式记录；
2. 校验脚本通过（脚本只覆盖其中可机械检查的部分）；
3. 所有关键主张有证据或显式的 `hypothesis / unverified` 标记；
4. `open_questions` 和 `unresolved` 都为空；有未决问题一律先标 `needs_review`；
5. 下游只需排版，无需再改论证或事实。

脚本的 `ok: true` 只覆盖第 2 条中可机械检查的部分，并检查第 4 条和状态一致性；第 1、3、5 条必须人工核对，不得用脚本结果替代。

任一条件不满足时为 `needs_review`；材料相互矛盾或关键事实无法得到时为 `blocked`。非 ready 状态只能预览，不得宣称可自动发布。

三个进度字段采用不同词表，不要混写：`presentation.md.status` 用 `DRAFT / REVIEW / READY`，`handoff.json.readiness` 用 `needs_review / blocked / ready`，`working-state.json.stage` 用状态机中的 `INTAKE / QUESTION_DEFINED / SKELETON / ENRICHED / REVIEW / READY`；三者表达同一进度。

## 常见错误

| 错误 | 修正 |
|---|---|
| 时间紧就一次问完问卷，或直接跳过提问且不记录假设 | 展示骨架后只问一个改变结论的问题；跳过时把假设落盘 |
| 用 `[待填]` 占位却从未生成可交接的工作文件 | 六个文件写齐；占位内容在 `working-state.json` 中对应到未决问题 |
| 有未决问题仍标 `READY / ready`，或把未决项说成“不阻塞” | 清空未决问题或把状态降为 `needs_review` |
| 把未核实的行业数字写成事实，或只在备注中提示 | 从 Visible 移除；写入 `sources.md`，Visible 用稳健表述 |
| 改稿时重编号、丢掉旧证据或未决问题 | 保留 slide_id 和证据状态；只更新受影响页面并追加 decision_log |
| 直接输出 HTML/CSS 或声称已生成并未创建的投屏文件 | 只交接本地路径给渲染 Skill；核对文件存在后再报告 |
| 用一堆方法名字堆砌流程 | 按 `method-router.md` 的真实缺口选 1–3 种，在更新摘要中给出停止条件 |

## 压力下的自我检查

时间紧、用户要求“看起来专业”、已有旧稿可照抄时，最容易发生以下误判。看到这些说法就按右栏执行；不要让“精神病态式走捷径”凌驾于内容真源：

| 常见说法 | 实际后果 / 处理 |
|---|---|
| “时间紧，跳过提问就行” | 跳过提问本身允许，但必须把受众、时长、目标和决策假设写入 `working-state.json.assumptions`，并在 `outline.md` 标出未决项。 |
| “把假设写在正文里就够了” | 正文里的假设无法追踪。必须落盘到 `working-state.json`，并映射到 `open_questions`。 |
| “现场要确认的假设只是执行提示，不阻塞 ready” | READY 有五条门禁；只要 `open_questions` / `unresolved` 非空，就只能是 `needs_review`。 |
| “用户说别写待核实，那就把无来源数字写成正面结论” | 改为稳健表述（如“用基线验证收益”），真实状态写入 `Evidence` 和 `sources.md`，不是改写事实。 |
| “用户说直接能投屏，顺手给个 HTML” | 本 Skill 的交付物是内容真源；只交接路径给渲染 Skill，并确认文件真实存在后再报告。 |
| “沿用旧六页结构就行” | 结构可以保留，但结论、证据状态、slide_id 和未决问题必须逐项复核；修改写进 `decision_log`。 |

## 文件索引

| 文件 | 何时读取 |
|---|---|
| [references/presentation-contract.md](references/presentation-contract.md) | 写或检查 `presentation.md` / `handoff.json` 时 |
| [references/method-router.md](references/method-router.md) | 选择分析方法、设计提问路径时 |
| [references/quality-gates.md](references/quality-gates.md) | Step 6 人工复核时 |
| [references/h5-adapter.md](references/h5-adapter.md) | 用户提供 h5-report-generator 作为下游渲染器时 |
| [examples/](examples/) | 首次使用或需要看六个文件长什么样时；以契约和脚本为准 |
| [schemas/handoff.schema.json](schemas/handoff.schema.json) | 手工检查 handoff 字段时 |
| [scripts/validate_content.py](scripts/validate_content.py) | 每次生成或改稿后运行，命令见 Step 6；只覆盖机械检查，不替代人工门禁 |
| [scripts/test_validate_content.py](scripts/test_validate_content.py) | 修改校验器或 READY 门禁后运行：`python3 -m unittest scripts/test_validate_content.py`（从 Skill 根目录） |

## 输出位置

默认写到当前项目的 `presentations/<slug>/`：`outline.md`、`claim-map.json`、`working-state.json`、`presentation.md`、`sources.md`、`handoff.json`；用户指定路径优先。逐轮更新对应文件，不只把结果写在聊天里。
