# Presentation Content Contract v1
本协议为两个 Skill 共同支持的渲染器中立 Markdown 输入格式。

`presentation.md` 首部为 YAML front matter，含 title、audience、objective、duration_minutes、status；status 取 DRAFT / REVIEW / READY，与 handoff readiness 的映射为 DRAFT→needs_review、REVIEW→needs_review、READY→ready。
每页以 `<!-- slide:id=SLIDE_ID role=ROLE chapter=CHAPTER -->` 标记，按文件顺序排列。
每页有 `#` 结论标题、`> Takeaway:`、`## Visible`、`## Evidence`、`## Visual Intent`、`## Speaker Notes`。
Visible 为观众正文；Evidence 为来源与事实状态；Visual Intent 为语义布局建议而非 HTML/CSS。
Speaker Notes 含 Purpose、Talk（2–4条，每条≤40字）、Transition、Minutes；可选 Cue、Interaction、Fallback。
封面、目录、收尾也必须有 slide_id 和备注。

`handoff.json` 的 slides[] 顺序必须与 Markdown 一致，含 slide_id、role、title、visual_intent、speaker_notes_present；unresolved 为必填数组，ready 时必须为空数组。
readiness 为 ready / needs_review / blocked；仅 ready 可自动发布，其他状态只允许预览并提示风险。
未核实数字和假设必须在观众可见位置保留限定条件。
下游只做不改变语义的排版精简；无法承载时返回 slide_id、issue、available_space、proposed_revision。
