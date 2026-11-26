# h5-report-generator 适配约定（已核对用户上传的 ZIP）
## 真实能力
- 单文件 HTML、PC 16:9、四主题 light-gradient/kraft-paper/dune/ink-classic；默认 light-gradient
- 封面2–3个结论胶囊；目录每章结论+2–3要点（一般3–4章，少于3章可省略目录）
- 内容页 `.content-header` + `.content-body`，其首元素 `.lead-bar`；标题即结论
- 支持卡片、表格、指标、因果链、阶段节奏、双卡对比、折叠、风险、时间轴、ECharts/Mermaid、图片等
- 每页（含封面/目录/收尾） `data-slide-id` 唯一，与 `SPEAKER_NOTES.id` 对齐
- `SPEAKER_NOTES`: 必填 id,title,purpose,talk(2–4条每条≤40字),transition；选填 section,minutes,cue,delivery,advance,interaction,fallback,pronunciation
- 时间预算：计划时长≤总时长90%；默认页数建议每页约2分钟，用户指定优先
- `validate_deck.py` 检查最终HTML结构、备注和时间
## 前置输出映射
- main_claim → cover chips + close lines（仅真实结论）
- chapter claim → toc-concl；chapter bullets → toc-points
- slide.title → content-title；slide.takeaway → lead-bar；Visible → 证据区
- Speaker Notes → SPEAKER_NOTES，原样保留已核实数字与讲述逻辑
- Visual Intent → 组件建议，允许渲染器选择更合适的已支持组件
- slide_id → data-slide-id，保持不变
## 解耦原则
前置 Markdown 不含 `div`/CSS 类名。h5 Agent 可以单独接受用户现成内容直接美化，也可消费前置输出。四主题仅在 adapter.theme 中选，不改变正文。
## 建议的小幅修改
在 h5 SKILL.md 新增“结构化内容输入模式”，优先读取 presentation.md/handoff.json；不强制重做 Step0 的内容策划；只做格式适配和版式修订；如缺备注，可单独补充。新增适配器脚本可自动抽取 JSON，但不是当前仓库既有能力。
