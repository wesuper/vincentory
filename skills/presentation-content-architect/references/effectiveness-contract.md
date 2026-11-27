# 独立效果记录协议

六文件及 READY 门禁为基础。用户需要正式效果评估、会后复盘或有重复演讲任务时，可额外生成内部 effectiveness-plan.json；其余任务在 intent 写观察信号即可。轻量提纲可只给口头效果建议。会后按需创建 effectiveness-observations.json。它们不进入 HTML、handoff、听众旅程哈希 或渲染输入，不参与渲染验收；计划与观察由独立工具校验。未创建计划时效果状态为未评估，而非失败。

计划对象：profile="communication-effectiveness"，content_sha256（presentation.md 原始字节 SHA256），revision（已封存 handoff revision），dimensions（五个固定键 insight/understanding/credibility/transfer/action）。每项包含 applicable（布尔）、reason（非空）；适用项另有 baseline, criterion, method, window, owner（非空字符串），slide_ids（非空真实页 ID 数组）。至少一个适用项。
观察对象：profile 同上，plan_sha256（计划文件原始字节 SHA256），mode="actual" 或 "rehearsal"，records 数组，每条 dimension（适用维度）、result（met/partial/not_met/unknown）、observed_at（ISO 日期）、source、observation、limitations（非空字符串）。每维最多一条汇总观察，原始记录由用户另存；缺项自动 unknown。mode=actual 仅允许真实观察，机器无法验证真实性。演练结果单列，不计入实际效果。
工具输出逐维状态、覆盖数、模式及缺失项，不生成综合分数，不推断因果。观察与计划版本不匹配直接拒绝。计划变更后旧观察仍与原计划绑定。效果记录不是签名、事实证明、自动追踪或真人审查。

使用听众旅程扩展时计划必须包含 `experience_sha256`，与已封存 handoff 一致；基础正式稿改为必填 `handoff_sha256` 和 `state_sha256`（各原始文件字节 SHA256），不填写 experience_sha256。两种模式均要求同目录 working-state.json、正式封存的 content_sha256 和 revision，并校验原契约。命令：`python3 scripts/evaluate_effectiveness.py presentation.md handoff.json effectiveness-plan.json [--observations effectiveness-observations.json]`。

基础模式示例位于 `examples/base-effectiveness/effectiveness-plan.json`，源是 `examples/` 中的原六文件；扩展示例位于 `examples/risk-change/`。两个模式不需要互相转换。
