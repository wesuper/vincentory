# 听众旅程与核心路线协议（内容协议的按需扩展）

扩展沿用六文件、Markdown、Notes 和 slide_quality 字段。高风险或复杂决策、多受众、复杂机制及需要短路线或深度预演时启用；普通稿可沿用基础协议。基础稿通过逐页质量门禁即可正式进入渲染。已声明扩展必须完整校验；补审或修订提升 revision。两 Skill 各带本文件和同一解析器/schema，保持字节一致。

## handoff.json 新增
`experience_profile: "audience-journey"`、`experience_sha256: "<64位十六进制>"`。由内容校验器 --seal 写入；第一次生成时可不填 hash，已封存后变更内容、意图或结果计划/评审均需提升 revision。`experience_sha256` 绑定 content_sha256、intent、profile、state.experience、quality_profile、slide_quality、review 的排序 JSON。不是签名、事实证明或权限授权；支持材料仍由旧契约追溯检查。封存失败不覆盖已有 handoff。

## working-state.json 新增 experience
保留既有 review/quality_profile/slide_quality。下列对象均使用 UTF-8；文本非空、具体，未知写真实未知和处理，不能仅填「通过/待补充」。例子见 examples/risk-change/（合成风险和预期管理案例）。
| 字段 | 结构与含义 |
|---|---|
| scene | 主场景枚举，见下 |
| secondary_scenes | 可选字符串数组，实际有第二目标才用，不能重复主场景 |
| audience | authority, prior_knowledge, stakes, barrier, evidence_threshold, secondary_audience, basis（字符串）；依据和假设分开 |
| outcome | recall, observable_signal, check_method, next_step, success_boundary, follow_up, non_goal（字符串）；仅计划，非实际反馈 |
| opening | why_now, promise, tension（字符串）；紧急事项可直接结论和请求 |
| scene_checks | 以 `<scene>.<key>` 为键，选定场景全部检查项；每项 `{status: covered/proposed/unresolved, basis, slide_ids: [现有页ID...], gap_action}`。proposed 必须在相关页可见为拟议、有可行验证路径、与当前目标匹配；unresolved 禁止 READY。每项至少一页属于 core；语义上要求所有关键限定和证据均在 core。若某项不适用，不捏造内容，解释为何无需该项并在核心页说明范围（例如当前不申请生产上线，因此无放行请求，明确禁止上线；可用 proposed）。不能拿单个覆盖标记冒充充分论证。|
| journey | 每个 slide_id 都有 `{beat, audience_shift, question, listen_cue, check, recovery, priority, basis}`。beat: orient/tension/explain/prove/decide/practice/close/appendix/transition；priority: core/deepening；其它非空字符串。所有核心页可独立形成必要论证。|
| short_route | `{mode: same/compressed, slide_ids: [按原顺序全部 core IDs], minutes: 核心页 Notes.Minutes 合计, basis: 跳页后逻辑/关键限制为何完整}`。same=没有安全可删页；compressed=存在可选深挖页。时间只是核心页备注预算，不保证演讲实时用时。|
| qa | 非空数组，每项 `{question,response,boundary,slide_ids:[真实页ID...]}`；真实最强异议及限制，证据追溯在对应页 Evidence 与 claim-map。内部工作材料不自动嵌入 H5。|
| rehearsal | recall, objection, compression, synchrony, action；每项 `{result:pass/revise/not_applicable,basis}`；实际听众未验证，明确为模拟/稿件审查。revise 不可 READY。|

## 场景与机器检查项（枚举稳定）
- `executive_proposal`: `decision_scope`, `business_value`, `options_tradeoff`, `validation_exit`
- `architecture_review`: `constraints`, `alternatives`, `mechanism`, `failure_modes`, `verification`
- `risk_change`: `change_trigger`, `impact_scope`, `risk_controls`, `go_no_go_rollback`, `owner_escalation`
- `expectation_management`: `baseline_commitment`, `delta_forecast`, `cause_uncertainty`, `replan_decision`, `next_update`
- `progress_outcome`: `baseline_target`, `actual_impact`, `attribution`, `remaining_gap`, `next_investment`
- `promotion_defense`: `level_criteria`, `challenge_scope`, `personal_contribution`, `impact_evidence`, `leverage_growth`
- `technical_deep_dive`: `entry_problem`, `mental_model`, `mechanism`, `reproduction`, `failure_boundary`, `transfer`
- `team_announcement`: `why_change`, `who_is_affected`, `before_after`, `execution_support`, `understanding_check`
- `cross_team_alignment`: `shared_goal`, `interest_tradeoff`, `interfaces_dependencies`, `ownership`, `disagreement_resolution`
- `incident_review`: `impact_timeline`, `causal_evidence`, `system_factors`, `corrective_actions`, `effectiveness_check`
- `technical_strategy`: `context_drivers`, `strategic_choices`, `tradeoff_non_goals`, `staged_investment`, `signals_exit`
- `customer_solution`: `customer_scenario`, `fit_gap`, `integration_security`, `validation_acceptance`, `next_step`
- `general`: `audience_problem`, `specific_value`, `support_boundary`, `appropriate_next_step`

## 渲染契约
prepare_render.py 输出 `experience_quality`（status、issues、scene、secondary_scenes、core_slide_ids、short_minutes、scope），不导出整份 audience/qa/内部画像到 HTML。reviewed 是机器检查记录完整、内部一致且自评无 revise，并非实际效果评估。正式交付仍须符合原 content_quality、静态/保真/视觉、演讲功能和披露门禁。未启用扩展时 experience_quality=not_applicable，不要求路线；已启用时必须 reviewed，否则不能正式交付，blocked 不渲染。HTML 仅当正式内容条件满足且扩展 reviewed 时嵌入 `window.PRESENTATION_ROUTE = {"core_slide_ids":[...],"short_minutes":...};`（短路线预算小数最多6位）。这是内容批准后的最小路由元数据，非自动播放列表；正常翻页不变。演讲者视图显示 core/deepening 和预算，只允许明确点击跳至下一核心页，不改变原始页序。真实舞台提示使用现有 Notes.Cue/Interaction/Advance/Fallback，勿从私密工作态自动复制。
verify_render 校验路由 JSON 与 plan 一致、未评审稿不激活；实际语义完整、可读、双屏/跳转等另做浏览器验证。基础稿不含扩展路由。人工高级装配须保留同一 JSON 与引擎。内容变更需回上游重审封存。
