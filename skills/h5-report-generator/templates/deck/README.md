# Deck Theme — 一套结构，四种气质

企业级 H5 汇报主题系统，面向 **PC 端 16:9 投屏**。四个主题共用同一份 HTML 结构与交互引擎，**只切换 `<html data-theme>`** 一个属性即可换肤。

## 主题清单

| `data-theme` | 气质 | 主色 / 背景 | 显示字体 | 适用场景 |
|--------------|------|------------|---------|---------|
| `light-gradient`（默认） | 清爽现代 | `#0066cc` / 浅蓝渐变 | 系统无衬线 | 技术分享、产品介绍、项目/季度汇报 |
| `kraft-paper` | 牛皮纸 · 杂志 | `#9b5a2e` / `#eedfc7` | Songti SC / Noto Serif SC | 复盘、总结、内部分享 |
| `dune` | 沙丘 · 克制 | `#8f7650` / `#f0e6d2` | Songti SC / Noto Serif SC | 战略、年度、对外汇报 |
| `ink-classic` | 墨水经典 · 印刷 | `#111111` / `#f1efea` | Playfair Display / Noto Serif SC | 观点表达、评审、设计稿 |

```html
<html lang="zh-CN" data-theme="light-gradient">   <!-- 默认，不填也是它 -->
<html lang="zh-CN" data-theme="kraft-paper">
<html lang="zh-CN" data-theme="dune">
<html lang="zh-CN" data-theme="ink-classic">
```

**主题只由 CSS 变量实现**：每个皮肤文件定义一个 `[data-theme="…"]` 块覆盖同名皮肤令牌（`light-gradient` 用 `:root`，因为它要作为无 JS 时的兜底）。所以页面里**不允许**出现硬编码色值或 `font-family`——写死就换不干净。

## 文件清单

| 文件 | 用途 |
|------|------|
| `style.css` | **只放结构**：结构令牌（`--fs-*` / `--gap-*` / `--radius-*` / `--pad-*` / `--page-min-h`）+ 全部组件样式 + 演讲者视图样式 |
| `themes/light-gradient.css` | 默认皮肤：浅蓝渐变 |
| `themes/kraft-paper.css` | 牛皮纸皮肤 |
| `themes/dune.css` | 沙丘皮肤 |
| `themes/ink-classic.css` | 墨水经典皮肤 |
| `script.js` | 幻灯片引擎、进度条、页码、ECharts/Mermaid、Lightbox、折叠、**演讲者视图与双屏同步** |
| `skeleton.html` | HTML 骨架模板（进度条 / 封面 / 目录 / 收尾 / 导航 / 三个样式脚本槽位 / `SPEAKER_NOTES` 占位） |
| `page-templates.md` | 页面类型 HTML 结构契约 + 备注契约（必读） |

### 分层规则

| 层 | 文件 | 允许出现 | 禁止出现 |
|----|------|---------|---------|
| 结构 | `style.css` | 字号、间距、圆角、页内边距、布局、动画 | 任何颜色值、`font-family` |
| 皮肤 | `themes/<id>.css` | 颜色、字体、阴影 | 字号、间距、布局声明 |

**为什么这么分**：四个主题的差异只在颜色和字体。把皮肤抽出来后，换主题不可能让布局漂移，改布局也不可能只改到一个主题。一个主题文件 44 个令牌，四个主题缺任何一个都会掉回浏览器默认值。

**装配顺序固定**：`style.css` → `themes/<id>.css`。`skeleton.html` 的 `<style>` 里就是两个槽位，顺序写死。

### 已知的 CSS 书写陷阱

CSS **不支持嵌套注释**。在块注释里写路径通配（如 `themes/*.css`）会提前开启一个新注释，把后面的样式全部吞掉。写路径时用 `themes/ 下的皮肤文件` 这种措辞。

另外，注释必须整行闭合：`/* === THEME_CSS === */ （当前：x）` 会让括号里的文字落到注释外，被浏览器当成选择器前缀，导致该规则之后的所有样式失效。

## 设计特点（v6）

- **结论先行结构**：封面结论胶囊 → 目录每章结论 + 要点 → 内容页标题即结论 + 结论条
- **语义令牌主题系统**：`--accent` / `--ink` / `--surface` / `--tint` / `--line` / `--danger` / `--ok` / `--warn` / `--font-display`，换主题 = 换一组值
- **演讲者视图**（`P` 键）：16:9 当前页 + 下一页真实预览、结构化备注、总计时/本页计时、键盘全操作
- **双屏同步**：`postMessage` + `BroadcastChannel` + 打开者握手，观众屏自动跟随翻页，支持黑屏/白屏/冻结
- **顶部进度条**：随翻页增长；右下胶囊导航 + `当前 / 总数` 页码
- 组件：卡片、明细表（分段/风险着色）、指标行、因果链、周节奏（冻结高亮）、双卡对比、TOP 风险卡、折叠分组、时间轴、Lightbox
- 响应式：`max-height:820px`（1366×768 投屏）/ 1200px / 768px 三组断点；打印时逐页分页、隐藏导航
- **PC 投屏流体排版**：`--fs-cover` / `--fs-h1` / `--fs-h2` / `--fs-body` / `--fs-small` / `--fs-number` 用 `clamp()`，1440 宽为基准，1080p/2K 自动放大，1366 收敛到下限

## 占位变量

| 变量 | 位置 | 含义 |
|------|------|------|
| `{{THEME}}` | `<html data-theme>` | `light-gradient` / `kraft-paper` / `dune` / `ink-classic` |
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
| `window.SPEAKER_NOTES = [ … ]` | 末尾 `<script>` | 每页一条，`id` 对齐 `data-slide-id` |

## 装配槽位

`skeleton.html` 里有三个槽位，生成时按序把源文件整段填进去：

| 槽位 | 来源 | 说明 |
|------|------|------|
| `/* === STYLE_CSS === */` | `style.css` | 结构，必填 |
| `/* === THEME_CSS === */` | `themes/<选定主题>.css` | **只放一个**，且必须在结构之后 |
| `/* === SCRIPT_JS === */` | `script.js` | 交互引擎 |

末尾还有一个独立的 `<script>` 放 `window.SPEAKER_NOTES = [ … ]`，不归槽位管，按页面内容手写。

> 示例文件 `../h5-report-template.html` 用 `scripts/sync-template.py` 生成，不要手改。

## 必须保留的结构

`.progress-bar`、`.navigation`（含 `#prevBtn` `#nextBtn` `.page-indicator`）、`.toc-cell > .toc-concl + .toc-points`、`.lead-bar`、每页的 `data-slide-id`、末尾的 `SPEAKER_NOTES` 脚本块。删改后将丢失进度条、翻页、结论先行结构或演讲者视图。

## 演讲者视图要点

- 备注栏只显示 `SPEAKER_NOTES`，**不读页面正文**；缺条目时显示中性占位而不是编内容
- 页面与备注靠 `data-slide-id` ↔ `id` 对齐，改名必须两边同时改
- 演讲者视图固定深色，不受主题影响；不要在其中引用浅色令牌
- 预览 iframe 以 1600×900 渲染后等比缩放，切换页面只发 `postMessage`，不重载 iframe
- 结构分三层：`.pr-stage`（当前页 + 下一页 + 宫格）/ `.pr-side`（备注 + 固定草稿）/ `.pr-bottom`（计时 + 控制 + 页码）。宫格**只替换 `.pr-stage` 内的卡片**，不要挪进 `.pr-side`，否则备注会被一起藏掉
- 备注正文在 `.pr-notes` 里滚动，现场草稿在它**外面**——讲者补一句话的入口必须永远在同一位置
- 观众屏同步状态有六种：连接中 / 已同步 / 未同步 / 未连接 / 弹窗被拦截 / 已冻结。心跳超时要落到「未连接」，不能永久停在「未同步」
- 标注（激光 / 圈选）坐标归一化后随 `postMessage` 同步到观众屏的 `.audience-ink` 画布；翻页时清空

### 存储键

`localStorage` 前缀 `h5-report-presenter:<页面路径>`，键分别为 `:note:<data-slide-id>`（现场草稿）、
`:rehearsals`（最近 5 次排练）、`:size`（备注字号）、`:layout`（布局模式）。按页面 ID 而不是页码
存储，页面重排不会串页。

详细键位与备注写法见 `page-templates.md` 第 0、16 节。
