# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.5.0] - 2026-11-27

内容与渲染之间的契约升到 1.1，并补上真正可执行的渲染链路：内容 Skill 产出可封存、可核查的六件套，H5 Skill 消费它并给出机器与人工两层验收。旧 1.0 稿仍可读。

### Added

- **内容契约 1.1**（`presentation-contract.md` + `handoff.schema.json`）：新增 `revision`、`content_sha256`（由 `--seal` 写入）、`intent` 六字段与每页 `chapter`；`speaker_notes_present` 收紧为必须为 `true`，`slide_id` 加 kebab-case 模式校验。仍兼容 1.0，旧稿不自动升级。
- **逐页内容质量记录**（`quality_profile: presentation-v2.1` + `slide_quality`）：每页记录 `audience_question` / `information_gain` / `support` / `visual_reason` / `notes_gain` / `basis`，READY 前必须全部 `pass`。缺记录时质量状态为 `not_reviewed`，仍可预览但不许正式交付。
- `presentation-content-architect` 新增 `audience-playbook`（按听众在场任务反推主线）、`slide-quality`（逐页信息增量门禁）、`evaluation`（维护期行为评估）三个参考文档。
- `h5-report-generator` 新增可运行渲染链路：`prepare_render.py`（解析真源、校验、产出 `render-input.json`）→ `render_reference.py`（基础卡片/流程/表格/列表）→ `verify_render.py`（文字保真、页序、备注与源哈希比对），并以 `test_pipeline.py` 覆盖。
- `h5-report-generator` 独立携带契约所需副本：`scripts/content_contract.py`、`schemas/handoff.schema.json`、`references/presentation-content-contract.md`，以及 `examples/` 六文件测试夹具，使其可单独安装。
- `h5-report-generator` 新增 `visual-routing`（视觉语义→组件）、`presentation-quality`（预检与逐页验收）、`render-workflow`（装配、披露与浏览器门禁）、`legacy-rendering-guide`（原 v6 详细操作档案）、`evaluation`。
- `validate_deck.py` 新增 `--profile standard|adaptive`（默认 `standard`）、`--legacy-js-notes`，并校验重复 `data-slide-id`。
- 新增 `skills/README.md`：目录约定、frontmatter 契约、独立与组合规则、增删改 Skill 的流程。
- 新增 `test_contract_parity.py`：两份 Skill 各自持有的共享契约、schema、解析器与示例夹具逐字节比对；同时安装时漂移即失败，单独安装时跳过。

### Changed

- `presentation-content-architect` 按 skill 最佳实践重构：description 改为触发条件，正文改为六步任务清单、明确的提问/跳过规则、机器可判定的 READY 门禁与压力下误判对照表；删除重复的 `references/content-contract.md`。
- `validate_content.py` 增加状态枚举、三处进度一致性、每页 `Minutes:` 完整性、Evidence 非空、READY 门禁字段与逐页质量检查，并附回归测试；`--seal` 拒绝在内容变更后直接覆盖哈希。
- `h5-report-generator` 的 `SKILL.md` 从 483 行收敛到入口式篇幅（触发、边界、五步流程、参考索引），详细操作归入 `references/legacy-rendering-guide.md`。
- `validate_deck.py` 改为按 profile 判定：`standard` 保持「最少 5 页、必须有目录结论卡、封面 2–3 个结论胶囊」，`adaptive` 不再对短稿报错。命令行默认仍是 `standard`（对既有产物最严格）；契约里 `adapter.profile` 的默认值是 `adaptive`，两者不一致时以显式传入为准。`talk` 条数不在 2–4 之间、单条超 40 字由警告升级为错误；`minutes` 增加有限数校验；`--target-minutes` 改为浮点并校验正有限。
- 右下导航改为共享透明平面样式：去掉胶囊底色与阴影，小字号页码、悬停/聚焦增强，`pointer: coarse` 下按钮放大到 44px 以满足触屏可操作性。
- 稀疏页不再用 `margin: auto` 把证据区垂直居中：短表格与单行证据改为紧邻结论，避免标题与证据在 1080p 下相隔半屏。
- 模板示例与 `page-templates.md` 的 `SPEAKER_NOTES` 改为合法 JSON，并说明可选 `--legacy-js-notes` 只用于可信旧样例。
- `scripts/generate.py` 文件模式由 `755` 归一为 `644`，与其他脚本及 `python3 <script>` 的调用方式一致。

### Fixed

- `render_visible` 在表格与普通文字混排时整段丢弃表格：改为按行分块，表格连续行渲染成表、其余仍走散文渲染，保留源顺序。
- 导航容器 `opacity: 0.6` 把文字与背景一起压暗，四个主题下 `--text-muted` 实测从 5.2:1 掉到 2.4:1，低于 WCAG AA；改为只靠字号与颜色降低存在感。
- `sync-template.py` 的备注守卫只匹配 JS 字面量 `id: '...'`，改为兼容两种引号并限定在 `SPEAKER_NOTES` 数组内，避免误抓页面里同名键。
- `--seal` 可被「删除 `content_sha256` 后重新封存」绕过「内容变更必须递增 revision」的约束；改为删除哈希在 `revision > 1` 时直接报错。
- `parse_notes` 默认只接受合法 JSON，JS 字面量需显式 `--legacy-js-notes`；随仓库发布的模板与文档示例均已改为 JSON。

## [0.4.2] - 2026-11-26

### Added

- `presentation-content-architect` 首次发布：内容契约、示例、handoff schema、校验器与 READY 门禁测试；登记进 `.claude-plugin/plugin.json` 与 README 发布列表。
- 添加 `.claude-plugin/icon.png` 插件图标，修复 `ICON_MISSING` 警告。

### Changed

- `h5-report-generator` 将常规汇报时长控制调整为两档：30 分钟会议默认 deck 讲 25 分钟（8–10 页），60 分钟会议默认讲 50 分钟（12–16 页）；剩余会议时间留给 Q&A。
- Step 0 明确用户输入的汇报时长、页数与内容要求优先于会议时长默认值；未在 deck 中明确的时间按用户要求使用，不套用旧表。`duration_minutes` 和 `validate_deck.py --target-minutes` 始终使用 deck 汇报时长，不是会议总长。
- 结构化内容模式同步采用新的时长优先级，并明确页数按“少而完整”控制，避免生成过多页面。
- `npm run validate` 改用 `scripts/validate-plugin.sh`：保留根目录 `CLAUDE.md`，只忽略已知的 root-context 警告；其他警告和错误仍会使校验失败。

## [0.4.1] - 2026-11-26

### Added

- `h5-report-generator` 新增「结构化内容模式」：除直接生成外，可消费符合 `references/presentation-content-contract.md` 的 `presentation.md`（可附 `handoff.json`），由 Agent 按语义映射到既有 HTML 骨架，不依赖旧版 `generate.py`。契约文件随 Skill 一起发布，并加入 SKILL.md 参考文档表。
- 结构化模式明确 `slide_id` 顺序核对、封面/目录/内容页/收尾字段映射、备注字段与必填 `title` 合成、`duration_minutes` 传入时间预算校验，以及溢出/不支持组件的反馈格式。

### Changed

- 结构化模式增加发布门禁：`handoff.json` 的 `readiness` 非 `ready`，或 `presentation.md` 的 `status` 非 `READY` 时只输出预览并列出未决/未核实项，不宣称可发布。
- 主题优先级明确为 `adapter.theme` > 用户指定 > 默认 `light-gradient`；该模式只跳过 Step 0 的内容规划部分，模板读取与时间预算照旧。
- `SKILL.md` 的 `description` 增加结构化内容输入的触发词。
- 移除仓库中未发布的 `skills/h5-report-generator copy/` 目录，其内容已合并进正式 Skill。

## [0.4.0] - 2026-11-26

### Added

- `h5-report-generator` v7：演讲者视图补齐「可排练、可跳页、可自查、可现场改写」四项现场能力。参考 `guizang-ppt-skill` 的演讲者模式实践，按本技能的结论先行结构与 PC 投屏定位重新实现，未复制其视觉系统。
- **宫格选页**（`G` / 点「宫格」）：问答时直接跳到任意页（「回到第 2 页那张表」）。宫格只替换预览区，右侧备注照常可见——讲者点选时往往正需要看备注判断跳哪页。
- **排练模式**（`R`）：记录每页实际用时，结束后给出「实际 vs 计划」对比表，本地保留最近 5 次。只做数据汇总，不做评分。修复了收尾页用时丢失：原先只在上一次翻页时入账，讲者停留最久的那一页反而没记录。
- **演前检查**：观众屏连接、弹窗权限、全屏、字体、图片、当前页 16:9、备注覆盖率七项；明确声明无法检测 HDMI / 转接线是否物理连接。
- **现场草稿**：演讲者视图内可直接写临时提醒，按 `data-slide-id` 存入 `localStorage`，翻页不串页。草稿固定在备注滚动区之外，补一句话的入口永远在同一位置。
- **布局三档**：均衡 / 页面优先 / 备注优先，写入本地并在下次进入时恢复。
- **同步状态细分**：连接中 / 已同步 / 未同步 / 未连接 / 弹窗被拦截 / 已冻结。心跳超时落到「未连接」，不再永久停在「连接中」。
- **标注同步到观众屏**：激光笔与圈选坐标归一化后随 `postMessage` 发送，观众屏用独立 `.audience-ink` 画布绘制；翻页时清空。此前标注只在讲者本机可见。
- 底部计时改为三段：已进行 / 本页（含本页计划）/ 剩余或超时。缺 `minutes` 的页显示 `—`，不猜。
- `scripts/validate_deck.py`：把 SKILL.md 校验清单里可机械判定的部分固化为脚本——三段式与 `lead-bar` 位置、目录逐格结论与要点、内容页编号连续、封面胶囊数量、备注条数与 `id` 对齐、必填字段、`talk` 长度、**时间预算 90% 上限**、占位符残留、重复 `id`、写死颜色。经 18 个变异测试逐项验证能捕获。
- `scripts/theme_contrast.py`：四个主题的 WCAG AA 对比度校验（正文/次要/辅助文字 vs `--paper`/`--surface`，`--on-accent` vs `--accent-fill` 最亮档）。
- SKILL.md 新增按汇报时长倒推页数的对照表（10/20/30/45 分钟）。

### Changed

- SKILL.md `description` 改为只描述触发场景，不再概述工作流（概述会让 agent 照描述行事而不读正文）。
- 演讲者视图结构分三层：`.pr-stage`（预览 + 宫格）/ `.pr-side`（备注 + 固定草稿）/ `.pr-bottom`（计时 + 控制 + 页码），并修正 `.pr-main` 未闭合导致底栏被卷入网格布局的标签错误。
- `content-number` 编号规则明确为「只编内容页」；新增「假设数据必须在页面上标注」的交付要求。
- 演讲者视图的 `onSlideChange` 去掉重复 `render()` 调用。

### Fixed

- **四个主题共 15 项对比度不达标**：`light-gradient` 的 `--text-muted`（2.42:1）、`--ink-faint`（2.19:1）、`--warn-ink`、`--ok`、`--ok-lm`、`--warn-ink-mid`；`kraft-paper` / `dune` / `ink-classic` 的 `--ink-faint`（低至 2.89:1）、`--warn`、`--ok-lm`；三个主题的 `--on-accent` 压在 `--accent-fill` 最亮档上仅 3.48–4.11:1。调整后 78 组配对全部 ≥ 4.5:1，令牌数与分层不变。
- **骨架 `{{PAGES}}` 占位符出现两次**（注释里又写了一遍）：按占位符全局替换会把内容页写两遍，产出重复 `id`。源码代理实测在 12 页报告里生成了 21 个 `<section>`。
- **稀疏页居中只覆盖四类证据区**：`.mini-table` / `.risk-cards` / `.week-panel` / `.timeline` 未参与余量均分，1080p 下表格页、风险页、周节奏页仍全堆页顶、页脚空 400–500px，生成者只能自己加包装类绕过。
- **入场动画污染溢出测量**：`.slide` 的 `fadeIn` 带 `translateY(16px)`，动画期间 `scrollHeight` 恒比 `clientHeight` 多 16px，按「每页 `scrollHeight === clientHeight`」验收会把整份 deck 误判为全页溢出。SKILL.md 补充测量时机，并新增 `prefers-reduced-motion` 下关闭入场动画。

### Removed

- 演讲者视图里无法生效的 `savedNote` 读取路径：只读 `localStorage` 却从未写入，现由现场草稿实际写入并回填。

## [0.3.0] - 2026-11-25

### Added

- `h5-report-generator` v6 演讲者视图：按 `P` 打开，右侧渲染结构化备注（本页目的 / 讲述要点 / 舞台提示 / 表达 / 翻页时机 / 转场句），左侧当前页与下一页 16:9 真实预览，底部总计时 + 本页计时 + 计划剩余。自动另开 `?mode=audience` 观众屏窗口，`postMessage` + `BroadcastChannel` 双向同步。
- 演讲者视图为键盘设计（讲者不必碰鼠标）：`←/→` 翻页、`B`/`W` 观众屏黑/白屏、`F` 冻结、`R` 计时暂停、`L`/`C`/`X` 激光与圈选、`+/-` 备注字号、`P`/`Esc` 退出。视图固定深色，不随页面主题变浅。
- `SPEAKER_NOTES` 备注契约：每页一条，`id` 对齐 `data-slide-id`；必填 `title` / `purpose` / `talk` / `transition`，选填 `section` / `minutes` / `cue` / `delivery` / `advance` / `interaction` / `fallback` / `pronunciation`。缺条目时显示中性占位，不虚构内容。
- 三个杂志风格主题并入主题系统：`kraft-paper`（牛皮纸 + 宋体）、`dune`（沙丘 + 炭黑）、`ink-classic`（纸白 + 近黑 + 衬线）。默认仍是 `light-gradient`，换主题只需改 `<html data-theme>` 并换内联的皮肤文件。
- `templates/deck/themes/`：四个主题各占一个文件，每个 44 个皮肤令牌。主题从 `style.css` 里的大段 `[data-theme]` 覆盖块拆成独立可读文件，改一个主题不必在 2400 行结构样式里翻找。
- `scripts/sync-template.py`：把 `deck/` 的样式与脚本机械同步进单文件示例，示例不再手写内联，杜绝与 `deck/` 漂移。
- 骨架新增 `{{THEME}}` 占位与 `SPEAKER_NOTES` 脚本块；页面新增 `data-slide-id` 约定。

### Changed

- 模板目录 `templates/light-gradient/` → `templates/deck/`：目录承载四个主题，主题名作目录名已不准确。
- `style.css` 全面语义令牌化（`--accent` / `--ink` / `--surface` / `--tint` / `--danger` / `--ok` / `--warn` / `--font-display` …），组件内不再出现硬编码色值，主题通过 `[data-theme]` 覆盖同名令牌实现。
- `style.css` 进一步瘦身为**纯结构层**：只保留 15 个结构令牌（`--fs-*` / `--gap-*` / `--radius-*` / `--pad-*` / `--page-min-h`）、组件布局与演讲者视图。皮肤令牌全部移入 `themes/<id>.css`。分层后换主题不可能带动布局漂移，改布局也不会只影响某一个主题。
- 装配方式改为两段内联：`style.css` → `/* === STYLE_CSS === */`，选定主题 → `/* === THEME_CSS === */`，顺序固定。`skeleton.html` 与 `SKILL.md` Step 1 同步更新。
- 稀疏页证据区改为在剩余空间内上下留白均分，修复 1366×768 / 1920×1080 下内容全堆页顶、页脚留大片空白的问题。
- `SKILL.md` 工作流扩为 5 步：新增主题确认步骤与演讲备注撰写步骤；校验清单补充备注覆盖率、`data-slide-id` 对齐、演讲者视图可用性、换主题不破样。
- `skills/` 扁平化：`skills/productivity/h5-report-generator` → `skills/h5-report-generator`。删除 `engineering/` / `productivity/` / `in-progress/` / `deprecated/` 分类层——Claude Code 只自动发现一层深度，嵌套 skill 必须靠 `plugin.json` 声明且漏声明会静默失效；分类层也无法起到"不发布"作用，`skills/` 下的一切都会随插件发布。
- `scripts/link-skills.sh` 改为遍历 `skills/*/`；`README.md` / `CLAUDE.md` 的目录约定与发布不变量同步改为单层结构。

### Fixed

- 修复 `:root` 中约 20 个语义令牌被写成自引用（`--accent-2: var(--accent-2)` 等）导致取值失效、三个杂志主题部分元素掉回默认色的问题。
- 修复演讲者视图内按 `P` 无法退出/重进：演示层与演讲者层同时响应同一次按键造成双次切换。
- 修复示例中目录页每格 `.toc-points` 后多出一个 `</ul>` 的标签错配。
- 修复 `style.css` 头部注释里写作 `themes/*.css`：CSS 不支持嵌套注释，这一处 `/*` 会吞掉其后全部样式，导致四个主题的皮肤令牌全部解析为空（页面掉回无样式）。
- 修复 `sync-template.py` 用 `window.SPEAKER_NOTES` 作锚点定位引擎脚本：该字符串在 `script.js` 内部也出现，锚点落在引擎中间，会把示例文件写出重复块与错配标签。改为按 `/* === STYLE_CSS === */`、`/* === THEME_CSS === */`、`/* === SCRIPT_JS === */` 三个槽位注释定位。
- 修复同步脚本把主题名写在 `/* === THEME_CSS === */` 注释**之外**（`… */ （当前：x）`），括号内容被浏览器当成选择器前缀，使其后所有规则失效。

### Removed

- 删除 `create-skill` skill：原生 `skill-creator` 已覆盖 skill 创作流程，仓库内版本的价值仅剩 manifest 同步，而这属于校验环节的职责。

## [0.2.0] - 2026-11-25

### Changed

- `h5-report-generator` v5：结论先行信息架构。封面新增结论胶囊（`.cover-chips`）；目录页每章升级为结论卡（一句话结论 `.toc-concl` + 2–3 条要点 `.toc-points`）；每个内容页强制三段式（`.content-header` 标题即结论 + `.lead-bar` 结论条 + `.content-body`）。
- `light-gradient` 主题重写样式系统与交互引擎：顶部进度指示条、可见页码、折叠分组、无 CDN 容错、打印分页；按 DOM 顺序翻页替代 `slideOrder` 数组。
- `light-gradient` 面向 PC 端 16:9 投屏重做排版：`clamp()` 流体字号与间距令牌，修复 1366×768 目录页溢出、收尾页装饰越界、目录卡空白与大屏稀疏页留白。
- `scripts/generate.py` 标注为 v4 兼容参考，不再作为主流程。

### Removed

- `h5-report-generator` 的 `blue-business` 主题目录（style / script / skeleton / 页面结构文档 / README）。风格与产品定位不符，模板收敛为单一 PC 端主题 `light-gradient`。

### Breaking

- `h5-report-generator` 移除 `slideOrder` 数组机制：翻页顺序改由 `<section class="slide">` 的 DOM 顺序决定，已生成的历史产物需删除该数组。

## [0.1.0] - 2026-08-05

### Added

- Initialized the vincentory skill repository.
- Added the create-skill engineering skill.
- Added Claude Code plugin and marketplace manifests.
