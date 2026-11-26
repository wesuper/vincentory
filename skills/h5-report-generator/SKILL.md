---
name: h5-report-generator
description: 用户需要生成汇报材料、H5演示文稿、网页版幻灯片、部门汇报、项目汇报、工作总结展示，或明确要求"H5格式"、"网页版PPT"、"浏览器里展示的幻灯片"、"演讲者视图/备注"时使用。PC 端投屏优化，结论先行的目录、顶部进度条、演讲者视图与双屏同步、ECharts/Mermaid 图表，内置四种主题（默认浅蓝，可选牛皮纸/沙丘/墨水经典），5-30 页幻灯片。
---

# H5 汇报材料生成工具

## 概述

企业级 HTML5 幻灯片演示系统，面向 **PC 端 16:9 投屏**。产物为**单文件 H5**（index.html 内联全部 CSS/JS），浏览器直接打开即可演示，按 `P` 进入演讲者视图。

**核心设计原则：结论先行。** 封面给结论胶囊、目录给每章结论 + 要点、内容页标题即结论 + 顶部结论条。管理层只看目录和每页标题就能带走核心信息。

**第二原则：讲者与观众看到不同的东西。** 观众看结论与证据，讲者看备注（背景、例子、判断、转场）。演讲者视图靠键盘操作，讲者全程不必碰鼠标。

## 文件结构

```
skills/h5-report-generator/
├── SKILL.md                    # 本文件：工作流程与规范
├── templates/
│   ├── README.md               # 模板注册中心与主题扩展指南
│   ├── h5-report-template.html # 单文件完整示例（6 页 + 6 条演讲备注）
│   └── deck/                   # 主题系统（一套结构，四种皮肤）
│       ├── style.css           # 只放结构：结构令牌 + 组件布局 + 演讲者视图
│       ├── themes/             # 一个主题一个文件，只含皮肤令牌
│       │   ├── light-gradient.css   # 默认：浅蓝渐变
│       │   ├── kraft-paper.css      # 牛皮纸 · 暖棕 + 宋体
│       │   ├── dune.css             # 沙丘 · 低饱和暖灰
│       │   └── ink-classic.css      # 墨水经典 · 黑白印刷感
│       ├── script.js           # 交互引擎（进度条、翻页、图表、演讲者视图、双屏同步）
│       ├── skeleton.html       # HTML 骨架模板（含 STYLE_CSS / THEME_CSS / SCRIPT_JS 槽位）
│       ├── page-templates.md   # 页面结构契约 + 备注契约 + 键位表 ★
│       └── README.md           # 主题清单与装配说明
├── scripts/
│   ├── validate_mermaid.py     # Mermaid 语法校验
│   ├── sync-template.py        # 把 deck/ 同步进单文件示例（唯一受支持的示例再生方式）
│   └── generate.py             # 旧版配置式生成脚本（参考用，主流程不依赖）
└── references/                 # 通用参考文档
```

---

## 核心工作流程（分步写入）

> **关键原则**：H5 产物文件较大（单文件可达数千行），**禁止一次性写入全部内容**。按以下 5 步分阶段写入，每步完成后验证再继续。

### Step 0: 需求分析

1. 确认页面数量与章节结构：**最少 5 页**（封面 + 目录 + ≥2 内容页 + 收尾），完整汇报通常 **8–30 页**，建议 3–4 章；用户指定的页数优先于本建议
2. **确认主题**：默认 `light-gradient`（浅蓝，不指定就用它）。用户若描述"牛皮纸/复古/杂志/手作感"→ `kraft-paper`；"沙色/克制/高级/安静"→ `dune`；"极简/黑白/印刷感/锐利"→ `ink-classic`。用户没有偏好时**不要**主动换主题，直接默认
3. **规划页面清单**：按顺序列出每页 `id`、`data-slide-id` 与标题，**每页标题先写成结论句**（如"19项变更分级收口，15项11.05前投产"），而不是话题词（如"需求变更"）
4. **规划封面 2–3 条结论胶囊**与**每章一句结论 + 2–3 条要点**（目录页要用）
5. 读取模板文件：`templates/deck/` 下的 `style.css`、`themes/<选定主题>.css`、`script.js`、`skeleton.html`、`page-templates.md`

### Step 1: 写入骨架

1. 读取 `templates/deck/skeleton.html` 作为基础骨架
2. 替换占位变量：`{{THEME}}`、`{{TITLE}}`、`{{BADGE}}`、`{{PRESENTATION_TITLE}}`、`{{SUBTITLE}}`、`{{DATE}}`、`{{AUTHOR}}`、`{{DEPARTMENT}}`、`{{TOC_TAGLINE}}`、`{{COVER_CHIPS}}`、`{{TOC_CELLS}}`、`{{END_ICON}}`、`{{CLOSE_LINES}}`
   - `{{THEME}}` 填 Step 0 选定的主题 ID（`light-gradient` / `kraft-paper` / `dune` / `ink-classic`），写在 `<html data-theme="…">` 上
   - `{{PAGES}}` **本步不要替换**，原样保留到 Step 2
   - `{{TOC_TAGLINE}}` 是目录副标题（如 `结论先行`），固定替换为本项目的实际定位
3. 将 `style.css`、`themes/<选定主题>.css` 与 `script.js` 的**完整内容**嵌入骨架，槽位一一对应：
   - `style.css` → `/* === STYLE_CSS === */`（结构，必填）
   - 选定的主题文件 → `/* === THEME_CSS === */`（**只放一个**，不要叠加多个；顺序必须在结构之后，否则皮肤会被结构覆盖）
   - `script.js` → `/* === SCRIPT_JS === */`
   - 禁止截断或改写原始样式/脚本；`<html data-theme="…">` 填的主题必须与内联的皮肤文件是同一个
4. 保留骨架末尾的 `SPEAKER_NOTES` 脚本块（`window.SPEAKER_NOTES = [ … ]`），Step 3 再写内容
5. 此时 `index.html` 应已包含：**顶部进度条 + 封面 + 目录 + 收尾页 + 右下导航 + 备注占位**，仅 `{{PAGES}}` 处留空

> 💡 为什么内联 CSS/JS：H5 需要**单文件可移植**，所有样式和交互必须内联。
> ⚠️ 不要移除 `.progress-bar`、`.navigation`、`.page-indicator` 三个元素——顶部进度条与页码依赖它们。

### Step 2: 逐页写入内容

按清单顺序，**每次写入 1–2 个页面**到 `{{PAGES}}` 占位处（首次写入时把 `{{PAGES}}` 替换为第一页内容 + 新的 `{{PAGES}}` 占位，如此递增；最后一页写完后删除占位）：

1. 查阅 `templates/deck/page-templates.md` 获取页面 HTML 结构
2. 每个内容页**必须**是"三段式"，顺序固定不可调换：
   - `.content-page` 直接子元素 `.content-header`（`.content-number` + `.content-title` 标题即结论 + `.content-subtitle`）
   - 紧随其后 `.content-body`，其**第一个子元素**必须是 `.lead-bar`（以 `<b>结论：</b>` 开头）
   - `.lead-bar` 之后才是卡片/表格/图表等证据区
   - 结构即 `.content-page > .content-header + .content-body > .lead-bar + …`，`lead-bar` 不能放在 `content-body` 之外
3. **每页都要有 `data-slide-id`**（封面/目录/收尾也不例外）：它是备注绑定键，值与规划清单一致，`id` 与 `data-slide-id` 都唯一
4. **无需维护 `slideOrder` 数组**：脚本按 DOM 顺序翻页、计算页码与进度条；只要 `<section class="slide" id="…">` 的 DOM 顺序正确即可
5. 每写完 1–2 页，用浏览器刷新验证：页数正确、进度条增长、目录结论可读

**页面类型参考**：
| 类型 | 用途 | 关键类名 |
|------|------|---------|
| 封面页 | 开篇 + 结论胶囊 | `.cover-page` / `.cover-chip` |
| 目录页 | 章节导航 + 每章结论 | `.toc-cell` / `.toc-concl` / `.toc-points` |
| 三栏卡片 | 并列要点 | `.card-grid` / `.card` |
| 表格页 | 明细/对比 | `.mini-table` + `.grp-row` |
| 指标行 | 关键数字 | `.stats-row` / `.stat-card` |
| 因果链 | 背景→应对→策略 | `.chain-grid` / `.chain-card` |
| 阶段节奏 | 周/期推进 | `.week-panel` / `.week-box.freeze` |
| 双卡对比 | 扩量/资源 | `.exp-grid` / `.exp-card` |
| 折叠深挖 | 支撑材料 | `.fold-section` / `.fold-title` |
| TOP 风险 | 风险与建议 | `.risk-cards` / `.rcard.high` |
| 时间轴 | 发展历程 | `.timeline` |
| 图表页 | ECharts/Mermaid | `.echart` / `.mermaid-diagram` |
| 图片展示 | 截图/架构图 | `.image-showcase` |
| 收尾页 | 结论复述 + 决策项 | `.qa-page` / `.ask-card` |

### Step 3: 写演讲备注（`SPEAKER_NOTES`）

备注是**交付物的一部分**，不是可选装饰。演讲者视图只读这份数据，不读页面正文。

1. 在骨架末尾的 `window.SPEAKER_NOTES = [];` 中，**为每一页写一条**（含封面、目录、收尾），顺序与页面顺序一致
2. `id` 必须等于该页的 `data-slide-id`，一字不差；对不上就静默显示空备注
3. 必填字段：`id`、`title`、`purpose`、`talk`（2–4 条）、`transition`；选填：`section`、`minutes`、`cue`、`delivery`、`advance`、`interaction`、`fallback`、`pronunciation`

**备注写什么：页面之外的三样东西**

| 写 | 不写 |
|----|------|
| 数字的**来由**、与前后页的关系 | 页面 `lead-bar` 原文 |
| 一个具体**例子/客户/场景** | 卡片里已有的 bullet |
| 讲者的**判断**、担心、要领导拍板的点 | 表格明细 |
| 为什么下一页是下一页（`transition`） | "这一页讲 XX" 式目录复述 |

> 判断标准：把备注念出来，如果观众低头就能在屏幕上看到同样的话，这条备注写错了。
> `talk` 每条 ≤ 40 字；4 条以上说明该页应该拆页。每条备注约 2–5 分钟口播量，`minutes` 汇总应接近会议时长。

详细字段与完整示例见 `templates/deck/page-templates.md` 第 0 节。

### Step 4: 校验

#### 4a. Mermaid 语法校验（必须，若使用了 Mermaid）

```bash
python3 scripts/validate_mermaid.py index.html
python3 scripts/validate_mermaid.py index.html --fix   # 自动修复
```

> Mermaid 陷阱：节点文本中的 `<` `>` 必须用引号包裹 `["text"]` 或实体 `&lt;` `&gt;`。详见 [Mermaid 安全规则](#mermaid-安全规则)。

#### 4b. 结构校验

- [ ] **顶部进度条存在**：`<div class="progress-bar"></div>` 在 `<body>` 首位，翻页时宽度增长
- [ ] **导航存在**：`.navigation` 内含 `#prevBtn` / `#nextBtn`，且页面有 `.page-indicator`
- [ ] **页码可见**：`.page-indicator` 内含 `#currentPage` / `#totalPages`，翻页时更新为 `当前 / 总数`
- [ ] **目录页每格都有结论**：每个 `.toc-cell` 都含 `.toc-concl` 一句话结论 + 紧随其后的兄弟元素 `.toc-points`（≥ 2 条，不要嵌在 `.toc-concl` 里）
- [ ] **每个内容页都是三段式**：`.content-page > .content-header + .content-body`，且 `.lead-bar` 是 `.content-body` 的第一个子元素
- [ ] **页面编号连续**：`.content-number` 为两位数（`01` `02`…），按内容页顺序连续，不跳号
- [ ] **标题是结论句**：`.content-title` 读起来像判断，不像话题词
- [ ] 封面胶囊 2–3 个，且与收尾页结论呼应
- [ ] 所有 `<section class="slide">` 的 `id` 与 `data-slide-id` 各自唯一，第一页带 `active`
- [ ] 所有图片路径可访问；ECharts `data-option` 是合法 JSON
- [ ] 无 `slideOrder` 数组残留（已移除该机制）

#### 4c. 演讲备注校验

- [ ] `window.SPEAKER_NOTES` 条数 = 页数，且 `id` 集合与 `data-slide-id` 集合**完全相等**
- [ ] 每页都渲染出备注：按 `P` 进入演讲者视图逐页翻，右侧不应出现 `本页目的 —`
- [ ] 备注不是页面复读：任取一页，`talk` 里不应出现该页 `lead-bar` 的整句
- [ ] `minutes` 汇总接近会议时长

#### 4d. 可读性与投屏校验

- [ ] 正文内容字号 ≥ 14px（推荐 15–18px，用 `--fs-body` 而非硬编码）
- [ ] 每页要点不超过 7 个
- [ ] 无大段文字（应使用列表）
- [ ] `body` 背景色为主题令牌 `var(--paper)`，禁止高对比度渐变（防止切换闪烁）
- [ ] **两档尺寸一屏放得下**：1366×768 与 1920×1080 下打开，每页 `scrollHeight === clientHeight`，无上下滚动条
- [ ] **大屏不显空**：1920×1080 下正文按 `--fs-body` 上限显示，证据区在剩余空间内上下留白均衡，不出现全堆在页顶或页脚
- [ ] **演讲者视图可用**：`P` 进入 / 退出各一次都正常；当前页/下一页两个 16:9 预览比例不变形；`←/→` 翻页时右侧备注与预览同步切换
- [ ] **换主题不破样**：若选了非默认主题，页面无残留蓝色元素、无掉回默认字体的标题

### Step 5: 输出最终产物

1. 浏览器打开验证翻页、进度条、页码、目录
2. 按 `P` 验证演讲者视图，确认备注齐全、观众屏同步
3. 输出产物清单：

```
✅ H5 汇报材料已生成
📁 文件: <output-path>/index.html (<N> 页, <size>)
🎨 主题: <theme>（演讲者视图按 P）
```

---

## 结论先行的信息架构（强制）

这是一套**结构性要求**，不是风格建议。缺任何一项都视为未完成。

| 位置 | 必须包含 | 反例 |
|------|---------|------|
| 封面 | 徽章 + 标题 + 副标题 + 3 项信息 + **2–3 个结论胶囊** | 只有标题的空白封面 |
| 目录 | 每章：编号 + 标题 + **一句结论** + **2–3 条要点** | 只有章节名的"标签列表" |
| 每个内容页 | 编号 + **标题即结论** + **`lead-bar` 结论条** + 证据区 | "业务概况"这类话题式标题 |
| 收尾 | 3 条以内结论复述（呼应封面）+ 可选决策事项卡 | 只有一个 Q&A 大字 |

### 为什么

汇报现场有两类读者：只看 3 秒标题的领导，和追问细节的执行层。结论先行让前者直接拿走结论，`lead-bar` 与折叠区让后者按需下钻。把结论藏在第三屏的图表里，等于没讲。

---

## 模板系统

### 当前可用主题

四个主题共用同一份 HTML 结构与交互引擎，皮肤各占一个文件：`deck/themes/<id>.css`。**默认 `light-gradient`；用户没提主题就用默认，不要自作主张换成杂志风。**

| `data-theme` / 皮肤文件 | 风格 | 何时选它 |
|--------------|------|---------|
| `light-gradient`（默认） | 浅蓝渐变，清爽现代，企业感 | 技术分享、产品介绍、项目/季度/年度汇报 |
| `kraft-paper` | 牛皮纸底 + 深棕 + 宋体，杂志手作感 | 复盘、总结、内部分享 |
| `dune` | 沙色 + 炭黑，克制高级 | 战略、年度、对外汇报 |
| `ink-classic` | 纸白 + 近黑 + 衬线，印刷锐利 | 观点表达、评审、设计稿 |

选择原则：**用户说了风格就按用户的；没说就用默认。** 不要因为"汇报对象是领导"就自动换深色——这是猜测用户偏好。

产物是单文件，所以**只内联选定的那一个主题**，`<html data-theme>` 与之保持一致。不要把四个主题都塞进去——那会让文件膨胀且叠加覆盖。

页面里**禁止**硬编码颜色与 `font-family`：全部走语义令牌（`--accent` / `--ink` / `--surface` / `--tint` …）。写死会在换主题时留下不协调色块。

### 新增主题

在 `deck/themes/` 下新建一个 `<id>.css`，用一个 `[data-theme="<id>"] { … }` 块覆盖**全部**皮肤令牌（漏一个就掉回蓝色），结构令牌一律不要碰。四个现有主题的文件是完整参照。见 `templates/README.md`。

> 结构文件 `deck/style.css` 里只允许出现结构令牌（字号、间距、圆角、页内边距）——出现颜色值就说明分层被破坏了。

---

## Mermaid 安全规则

Mermaid 代码块中 `<` `>` `&` 等字符会导致渲染失败，**生成时必须遵守**：

1. **节点文本含特殊字符 → 引号包裹**
   ```
   ✅ A["包含 <tag> 的文本"]
   ❌ A[包含 <tag> 的文本]
   ```

2. **子图标题含特殊字符 → 引号包裹**
   ```
   ✅ subgraph "模块 <A> 架构"
   ❌ subgraph 模块 <A> 架构
   ```

3. **禁止 Mermaid 关键字作为节点 ID**
   ```
   ✅ node1 --> flow_node
   ❌ graph --> flowchart
   ```

4. **生成后必须校验**
   ```bash
   python3 scripts/validate_mermaid.py <file>
   ```

`scripts/validate_mermaid.py` 支持 `--fix`、`--json`、`--stdin`。

---

## 设计约束

### 投屏优先（PC 端 16:9）

H5 主要用于会议室投屏，观看距离 2–5 米。主题用 `clamp()` 做流体字号：1440 宽为基准，1080p/2K 大屏自动放大到上限，1366 小屏收敛到下限。

| 元素 | 1440 基准 | 允许区间 | 对应变量 |
|------|----------|---------|---------|
| 封面标题 | 54px | 52–78px | `--fs-cover` |
| 页面标题 | 26px | 26–40px | `--fs-h1` |
| 卡片/区块标题 | 17px | 17–22px | `--fs-h2` |
| 正文内容 | 14px | 14–19px | `--fs-body` |
| 表格/脚注 | 13px | 13–15px | `--fs-small` |
| 指标数字 | 34px | 30–52px | `--fs-number` |

> 禁止为"塞入更多内容"而缩小字体。内容过多时拆分为多页。
> 校验尺寸时至少覆盖 **1366×768**（投影最常见）与 **1920×1080**（会议室大屏）两档：每页内容必须一屏放得下（`scrollHeight === clientHeight`），大屏上文字不能显小。

### 背景色规则

- `body` 背景色由主题令牌 `var(--paper)` 决定（默认主题是 `#e8f4fc`）
- **禁止**高对比度渐变（如紫色 `#667eea → #764ba2`），切换幻灯片时会闪烁
- `.slide` 内部渐变由 `var(--slide-bg)` 决定，已经是浅渐变

### 每页内容密度

- 1 个结论式主标题 + 1 条结论条
- 3–7 个关键要点
- 0–2 个图表/图片
- 使用列表，避免大段文字

### 强调色语义（不要混用）

| 语义 | 类名 | 用途 |
|------|------|------|
| 正常/关键 | `.chip`、`<b>` | 关键数字、普通强调 |
| 风险/冻结 | `.chip.warn`、`.cover-chip.alert`、`.week-box.freeze`、`.risk-high` | 红旗项、禁变更期 |
| 待定/中风险 | `.chip.gold`、`.risk-mh` | 待评审、中-高风险 |
| 完成/低风险 | `.chip.ok`、`.grp-row.g-done`、`.risk-low` | 已交付、低风险 |

> 同一页红色不超过 2 处，否则等于没有重点。

---

## 交互功能

由 `script.js` 提供，无需额外配置：

- **顶部进度条**：`.progress-bar` 宽度 = 当前页 / 总页数
- **翻页**：← / →、PageUp/PageDown、Home/End、触摸滑动、右下按钮
- **页码**：`当前 / 总数`
- **演讲者视图**（`P`）：右侧备注 + 当前页/下一页 16:9 预览 + 双计时；自动开观众屏
- **双屏同步**：观众屏跟随翻页，支持黑屏（`B`）/白屏（`W`）/冻结（`F`）
- **激光笔与圈选**（`L` / `C`，`X` 清除）：在预览画面上标注，鼠标或触控板均可
- **ECharts**：自动初始化可见页的 `.echart[data-option]`
- **Mermaid**：自动渲染 `.mermaid-diagram[data-code]`
- **图片 Lightbox**：点击 `.image-item img` 全屏预览
- **折叠分组**：点击 `.fold-title` 折叠/展开
- **无 CDN 容错**：echarts/mermaid 未加载时跳过图表，不影响翻页
- **打印**：`@media print` 下逐页分页输出

### 演讲者视图：为什么这样设计

- **讲者不碰鼠标**：会议室里讲者往往站在屏幕前或拿着翻页笔，所有操作都能用键盘完成（`→` 翻页、`B` 黑屏、`R` 暂停计时）
- **精简展示**：右侧只放备注，不放缩略图列表、不放工具栏——窄栏里信息越少，讲者越能一眼定位
- **结构化互补**：备注写的是背景、例子、判断、转场，与屏幕上的结论形成"结论 / 论据"互补，而不是同一段文字的两次出现
- **固定深色**：全黑会议室里浅色备注栏会刺眼，演讲者视图不跟随页面主题

### 演讲者键位

| 键 | 作用 | 键 | 作用 |
|----|------|----|------|
| `→` / `PageDown` / `Space` | 下一页 | `←` / `PageUp` | 上一页 |
| `Home` / `End` | 首页 / 末页 | `P` / `Esc` | 退出演讲者视图 |
| `B` / `W` | 观众屏黑屏 / 白屏 | `F` | 冻结观众屏 |
| `R` | 暂停 / 继续计时 | `L` / `C` / `X` | 激光 / 圈选 / 清除 |
| `+` / `-` | 备注字号 | | |

> 演示模式（未进演讲者视图）下 `F` 是全屏。详见 `templates/deck/page-templates.md` 第 16 节。

---

## 常见错误

| 错误 | 后果 | 修正 |
|------|------|------|
| 删掉 `.progress-bar` 或 `.navigation` | 无进度条/无法翻页 | 从 skeleton 原样保留 |
| 目录页只写章节名 | 领导看不到结论 | 每章补 `.toc-concl` + `.toc-points` |
| 标题写话题词（"业务概况"） | 信息量低 | 改写为结论句 |
| 内容页直接堆卡片，没有 `.lead-bar` | 结论埋没 | 页面顶部补结论条 |
| 手工维护 `slideOrder` | 与 DOM 顺序不同步 | 删掉，按 DOM 顺序即可 |
| 用红黄蓝绿各标一遍 | 没有重点 | 每页红色 ≤ 2 处 |
| 没写 `SPEAKER_NOTES` | 演讲者视图右侧空白，讲者裸讲 | 每页一条，`id` 对齐 `data-slide-id` |
| 备注照抄页面要点 | 讲者重读，观众被念两遍 | 改写背景/例子/判断/转场 |
| 页面里写死颜色或字体 | 换主题后残留蓝色/字体断裂 | 一律用语义令牌 |
| 只写 `id` 不写 `data-slide-id` | 备注绑定不上（靠兜底才碰巧生效） | 每页显式写 `data-slide-id` |

---

## 参考文档

| 文件 | 内容 |
|------|------|
| `templates/README.md` | 模板注册中心、主题扩展指南、占位变量表 |
| `templates/deck/page-templates.md` | 页面结构契约 + 备注契约 + 主题 + 键位（必读） |
| `templates/deck/README.md` | 四个主题清单、必须保留的结构 |
| `references/charts-data.md` | ECharts 图表配置参考 |
| `references/optimization.md` | 性能优化建议 |
| `references/responsive-design.md` | 响应式设计指南 |
| `references/troubleshooting.md` | 常见问题排查 |

---

**更新日期**：2026-11-25
**版本**：6.0
**维护者**：vincentruan
