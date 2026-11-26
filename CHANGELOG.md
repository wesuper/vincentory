# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
