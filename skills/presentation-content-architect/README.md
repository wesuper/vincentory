# Presentation Content Architect

独立 Skill，入口 `SKILL.md`。把零散想法、提纲、访谈纪要或已有稿转换为面向特定听众的论证结构、精炼页面内容、详细口述备注、证据台账与交接状态。只产出 Markdown/JSON 内容真源，不负责 HTML/CSS 排版。

## 输入与产物

- **输入**：一句话想法、会议/访谈记录、参考材料、旧稿，或需要重构主线的演示。
- **独立交付六文件**：`presentation.md`（内容真源）、`outline.md`（目标与标题串）、`claim-map.json`（主张—证据映射）、`sources.md`（证据台账）、`handoff.json`（交接索引）、`working-state.json`（状态与评审）。
- **正式稿使用契约 1.1**：新增 `revision` / `content_sha256` / `intent` 与逐页 `slide_quality`（`quality_profile: presentation-v2.1`）；旧 1.0/1.1 仍可读取，未补评审的稿在 H5 中只能作预览。

## 使用

```
使用 presentation-content-architect。我要面向<听众>做<场景>汇报：先从听众的决策标准反推主线，澄清关键缺口；每页要带来新的、可核查的判断依据。优先结构化视觉关系，画面文字提炼，详细推理和异议放备注。输出完整内容真源。
```

任务能被单个 Skill 覆盖时直接使用，不必串联渲染 Skill。材料已成熟、只需要排版时交给 `h5-report-generator`。

## 工作流程

`INTAKE → QUESTION_DEFINED → SKELETON → ENRICHED → REVIEW → READY`，可回退。

1. **定义结果**：听众是谁、有什么权限、现在相信什么、听完应理解/行动什么、如何观察达成、主讲时长。
2. **澄清与诊断**：区分事实/推断/假设，问最改变结论的一问；足够即停，不凑轮次。
3. **构建主线**：先 `claim-map.json` 再 `outline.md`，每页一个信息任务，标题给准确判断。
4. **完整稿**：按契约写 `presentation.md` 与 `sources.md`；Visible 放结论/数据/限制，Talk 与 Delivery 展开口述。
5. **反方预演**：按 `references/quality-gates.md` 与 `references/slide-quality.md` 逐项评审并写入 `working-state.json`，不能成立的主张先修订。
6. **交接**：生成 `handoff.json`、`working-state.json`，封存 revision 对应的 SHA-256 并校验。

## 质量门禁

- 逐页必须回答一个具体听众问题，并给出可核查的信息增量；只有口号、背景复述或泛用三点的页面应合并或删除。
- 每页至少一种具体支撑：事实与来源、真实数据/对照、可核查机制、带边界的案例、明确取舍，或具体步骤与验收逻辑。缺材料时降级为标注清楚的假设/验证设计，不编造数字与承诺。
- 视觉关系优先：数量/趋势用数据图，过程/机制用关系图，精确对比用矩阵；无数据不画虚假定量图，无顺序不加箭头。
- 关键限制、比较口径和决策条件必须留在 Visible，不能只藏在备注；备注也不放未获许可的信息。
- `review` 与 `slide_quality` 的 pass 是自检/角色模拟，不是真实听众认可；有实际审批或披露授权未定时应 `blocked` / `needs_review`。

## 运行

在 Skill 根目录运行：

```bash
python3 scripts/validate_content.py examples/presentation.md examples/handoff.json examples/working-state.json --seal
python3 scripts/validate_content.py examples/presentation.md examples/handoff.json examples/working-state.json
python3 -m unittest discover -s scripts -p 'test*.py'
```

修改内容后必须重新 `--seal`，否则 hash 过期会被预检拒绝。测试套件包含 `test_contract_parity.py`，在两份 Skill 同时安装时比对共享契约、schema、解析器与 `examples/` 副本，漂移即失败。

## 边界

- 不生成 HTML/CSS，不绑定主题或渲染器；H5 联用见 `references/h5-adapter.md`，把六文件交给 `h5-report-generator`。
- 内容 READY 只表示具备正式渲染资格，不等于 H5 验收、用户批准公开发布或真实听众认可。
- `examples/` 是合成的售前知识助手试点（三页、五分钟），不是真实客户数据，不要照搬其中的业务结论或收益表述。
