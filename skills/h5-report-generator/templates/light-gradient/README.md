# Light Gradient Theme

浅蓝到白色渐变背景的企业级 H5 汇报主题，视觉风格轻盈现代，适合技术分享、产品介绍、项目汇报。

## 文件清单

| 文件 | 用途 |
|------|------|
| `style.css` | 主题样式系统（进度条、封面、目录、内容页、收尾页） |
| `script.js` | 幻灯片引擎、顶部进度条、页码、ECharts/Mermaid、Lightbox、折叠分组 |
| `skeleton.html` | HTML 骨架模板（含进度条 / 封面 / 目录 / 收尾 / 导航） |
| `page-templates.md` | 页面类型 HTML 结构契约（必读） |

## 设计特点（v5）

- 主色：`#0066cc` 明亮蓝；强调红 `#e63946`、橙 `#e65100`、绿 `#27ae60`
- 背景：`#f0f7ff → #ffffff → #f8fcff` 浅蓝渐变；body 纯色 `#e8f4fc`（防切换闪烁）
- **顶部进度条**：3px 蓝渐变，随翻页增长
- **结论先行结构**：封面结论胶囊 → 目录每章结论 + 要点 → 内容页标题即结论 + 结论条
- 右下胶囊导航 + `当前 / 总数` 页码；悬停增亮
- 组件：卡片、明细表（分段/风险着色）、指标行、因果链、周节奏（冻结高亮）、双卡对比、TOP 风险卡、折叠分组、时间轴、Lightbox
- 响应式：`max-height:820px`（1366×768 投屏）/ 1200px / 768px 三组断点；打印时逐页输出、隐藏导航
- 布局尺寸统一由 `--pad-top` / `--pad-bottom` / `--page-min-h` 变量控制，矮屏只调变量即可
- **PC 投屏流体排版**：`--fs-cover` / `--fs-h1` / `--fs-h2` / `--fs-body` / `--fs-small` / `--fs-number` 用 `clamp()`，1440 宽为基准，1080p/2K 自动放大，1366 收敛到下限
- 稀疏页（3 卡 / 4 指标）卡片会有最小高度并自动居中，避免大屏下半页空白

## 占位变量

| 变量 | 位置 | 含义 |
|------|------|------|
| `{{TITLE}}` | `<title>` | 页面标题 |
| `{{BADGE}}` | 封面顶部 | 徽章标签（部门 · 专项 · 时间） |
| `{{PRESENTATION_TITLE}}` | 封面 `<h1>` | 汇报主标题 |
| `{{SUBTITLE}}` | 封面 | 副标题 |
| `{{DATE}}` | 封面信息行 | 日期 |
| `{{AUTHOR}}` | 封面信息行 | 汇报人 |
| `{{DEPARTMENT}}` | 封面信息行 | 科室/部门 |
| `{{COVER_CHIPS}}` | 封面 | 2–3 个结论胶囊 HTML |
| `{{TOC_TAGLINE}}` | 目录副标题 | 如「结论先行」 |
| `{{TOC_CELLS}}` | 目录 | 每章 `.toc-cell` HTML |
| `{{PAGES}}` | 内容区 | 内容页 `<section>` 序列 |
| `{{END_ICON}}` | 收尾页 | 图标 emoji |
| `{{CLOSE_LINES}}` | 收尾页 | 3 条以内结论复述 |

## 必须保留的结构

`.progress-bar`、`.navigation`（含 `#prevBtn` `#nextBtn` `.page-indicator`）、`.toc-cell > .toc-concl + .toc-points`、`.lead-bar`。删改后将丢失进度条、翻页或结论先行信息架构。
