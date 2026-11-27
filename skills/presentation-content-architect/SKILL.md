---
name: presentation-content-architect
description: 将模糊想法、提纲、访谈纪要和参考材料转化为面向领导、客户、同行或晋升评委的可论证演示内容、逐页讲稿、证据台账和可供渲染器消费的交接文件。适用于汇报、技术分享、售前、市场介绍、评审、晋升答辩、重构演示逻辑或与用户持续澄清；也可单独交付 Markdown。仅要求现成内容排版、HTML/CSS 或 H5 投屏时交给渲染 Skill。
---

# Presentation Content Architect

## 任务与边界
把原始材料变成**听众能理解、质疑、复述并据此行动的内容真源**。内容与展示分离。只产出 Markdown/JSON，不自行生成 HTML/CSS；不绑定主题、模板类或渲染器。事实、用户陈述、推断、建议、假设分开；不得杜撰数字、案例、来源、个人贡献、产品承诺。角色会诊只是模拟，不证明听众真实认可。

## 入口分流
- 快速提纲/单页：直接给结论骨架及关键假设，不强制落盘六件套；需要正式稿或交接时走完整流程。
- 探索共创（目标或证据不明）：先给可编辑的初步叙事，一轮问一个最改变判断的问题；答后更新。默认最多六个有效问题再给当前可用稿；用户继续深挖则继续，不凑轮次。
- 直接出稿（用户明确要求/材料充分）：用已知事实，标记缺口，能做则做；只在关键目标、权限或证据矛盾会改变主线时提问。未知不得写成用户已确认。
- 修订：先读取旧产物，定位影响页；保持原 slide_id、证据 ID、未改变的结论。新增/删页显式记录映射，更新 revision；不复问已确认项。

## 完整工作流（按阶段落盘）
1. **定义结果**：读取 [audience-playbook](references/audience-playbook.md) 对应场景。先写听众是谁/权限、现在相信什么、听后应理解什么、期望行动或应用、如何观察达成、主讲时长（区分会议/Q&A）。用户未说的记 assumptions。用这组目标反推内容，不用固定汇报模板。
2. **澄清与诊断**：区分事实/用户报告/观点/待证假设，冲突保留来源。给用户初版「听众问题 → 主张 → 证据缺口 → 预计行动」，然后问最改变结论的一问。读取 [method-router](references/method-router.md)，只选与缺口相关的方法：苏格拉底定义问题、第一性原理检验因果、金字塔组织论点、SCQA 建立背景；行业研究/核查/双层解释/专家会诊/反向拆解/跨域类比按需。研究优先原始来源，无法查证则标记。每轮记录确认、变化、剩余关键问题；足够即停。
3. **构建主线**：先写 claim-map.json，再写 outline.md。每页一个独立的信息任务，标题是准确判断/待验证问题；证据强度匹配结论。根据听众和时长决定是否需要封面/目录/附录，不设固定页数。列最强异议、反例、替代方案和停止条件；混合受众分主线/备注/附录。先解决主张是否成立，再扩写。逐页执行 [内容信息增量门禁](references/slide-quality.md)：回答一个具体听众问题，给出独立、可核查的信息增量，确定证据/机制/案例/比较/执行方案和视觉关系；不能以空泛观点撑页。缺材料先定向澄清，或明确降为拟议验证方案/草案，不编造数据。
4. **完整稿**：按 [presentation-contract](references/presentation-contract.md) 写 presentation.md、sources.md；正文以听众能看懂的结论和可核对的证据为主，关键限定和公开来源提示必须在 Visible；Evidence 放内部追溯信息。Notes 的 Purpose 是本页改变的判断，Talk 2–4 条每条≤40字，Transition 与下一页有逻辑；Minutes 按实际讲述时间，留缓冲；Cue/Fallback/Interaction 可加入异议与答疑跳转。优先图表与结构化图示（有真实关系才画），Visible 仅保留短标签、关键数字、比较维度、结论与必要限定；解释、推理、口述案例、计算口径与反方回答放入 Talk/Delivery/Fallback，不能把关键证据或风险只藏在备注。Delivery 可写完整单行口述展开；Talk 仍为现场提示，不复读画面。需要更长讲稿可另写。
5. **反方预演**：读取 [quality-gates](references/quality-gates.md)。模拟主要听众、怀疑者、执行者各自提问，修订不能成立的主张；每项门禁记录依据，不能用总分抵消致命问题。另逐页填写 working-state.quality_profile= presentation-v2.1 与 slide_quality（见 slide-quality）；对空洞、复述、证据不支持、错误图示和画面/口播分工失败的页标 revise，修订或合并后才可 READY。用户要答辩/PoC/技术评审时尤其核对真实标准、归因、验证与边界。保留拟验证项，不冒充实际认可。
6. **交接**：生成 handoff.json、working-state.json；按契约 1.1 生成新稿，旧 1.0 可读。默认 `presentations/<slug>/`，用户指定优先。写齐后用下列命令封存 revision 对应的 SHA-256 并校验；修改后重新封存。先读错误、局部修订、重跑；通过仅表示机器门禁通过，仍要做 Step 5。

```bash
python3 "<skill-root>/scripts/validate_content.py" presentation.md handoff.json working-state.json --seal
python3 "<skill-root>/scripts/validate_content.py" presentation.md handoff.json working-state.json
```

## 状态与停问标准
- 状态机 `INTAKE → QUESTION_DEFINED → SKELETON → ENRICHED → REVIEW → READY`，可回退。
- DRAFT/REVIEW 对应 needs_review 或 blocked；READY 对应 ready。关键矛盾、披露授权未定、关键证据不足且结论不能降级时 blocked；尚需确认但能安全预览时 needs_review。
- `open_questions` 与 `handoff.unresolved` 仅记影响内容交付的阻塞项且同步。已通过有条件结论消化的非阻塞假设写 `limitations`（不能藏在备注或伪称已确认）。
- READY：意图已明确或受控假设已说明；机器通过；所有质量门禁 pass/合理不适用，新增逐页 slide_quality 全部 pass；关键事实/结论/边界可追溯；阻塞为空。内容 READY 不依赖尚未进行的 HTML 验收，也不等于获准公开发布。
- 无法继续澄清时交付可用草案和精确缺口，不无限追问，也不为了通过校验清空未决问题。

## 独立与联用
单独使用：交付六文件，用户可直接讲或交给任意渲染器。H5 联用：读取 [h5-adapter](references/h5-adapter.md)，把实际存在的 `presentation.md`、`handoff.json`、`working-state.json` 及同目录文件路径交给 h5-report-generator（仅在可用时调用）；若不可用仍交付独立稿。下游回传 `slide_id/issue/available_space/proposed_revision` 后，先检查影响主张/证据/时长；需要时重走门禁并更新 revision，未授权不可改事实。

## 文件索引
- [presentation-contract](references/presentation-contract.md)：正式字段、状态、示例格式（生成/修订必读）。
- [audience-playbook](references/audience-playbook.md)：按角色/听众/场景反推验收（定义意图时）。
- [method-router](references/method-router.md)：遇到诊断/逻辑缺口时。
- [quality-gates](references/quality-gates.md)：内容 READY 前。
- [slide-quality](references/slide-quality.md)：主线、逐页稿与评审必读，信息增量/视觉优先/讲述分工。
- [h5-adapter](references/h5-adapter.md)：仅联用时。
- [examples](examples/)：唯一维护的当前契约完整示例；旧 1.0 兼容性由测试覆盖。
- [handoff.schema.json](schemas/handoff.schema.json)：机器字段；[test_validate_content.py](scripts/test_validate_content.py)：回归测试。
- [evaluation](references/evaluation.md)：维护/迭代时的行为测试。
