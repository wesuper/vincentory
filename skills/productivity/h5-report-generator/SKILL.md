---
name: h5-report-generator
description: 企业级HTML5幻灯片演示系统生成器。当用户需要生成汇报材料、H5演示文稿、网页版幻灯片、部门汇报、项目汇报、工作总结展示，或明确要求"H5格式"、"网页版PPT"、"浏览器里展示的幻灯片"时，必须使用此技能。支持多主题模板、双章节目录、ECharts/Mermaid图表、响应式布局，10-30页幻灯片。
---

# H5 汇报材料生成工具

## 概述

企业级 HTML5 幻灯片演示系统，支持**多主题模板**扩展。产物为**单文件 H5**（index.html 内联全部 CSS/JS），浏览器直接打开即可演示。

## 文件结构

```
skills/in-progress/h5-report-generator/
├── SKILL.md                    # 本文件：工作流程与规范
├── templates/                  # 主题模板（可扩展）
│   ├── README.md               # 模板注册与扩展指南
│   ├── h5-report-template.html # 单文件完整模板（快速预览）
│   ├── light-gradient/         # 浅蓝渐变主题（默认）
│   │   ├── style.css           # CSS 样式系统
│   │   ├── script.js           # 交互引擎（切换、图表、Lightbox）
│   │   ├── skeleton.html       # HTML 骨架模板
│   │   ├── page-templates.md   # 页面类型 HTML 结构规范
│   │   └── README.md           # 主题说明
│   └── blue-business/          # 蓝色商务主题（备选）
├── scripts/
│   └── validate_mermaid.py     # Mermaid 语法校验工具
└── references/                 # 通用参考文档
```

---

## 核心工作流程（分步写入）

> **关键原则**：H5 产物文件较大（单文件可达数千行），**禁止一次性写入全部内容**。必须按以下 5 步分阶段写入，每步完成后验证再继续。

### Step 0: 需求分析

1. 确认用户需要的页面数量和章节结构
2. 确定主题模板（默认 `light-gradient`，查看 `templates/README.md` 获取可用模板列表）
3. 规划 `slideOrder` 数组：列出所有页面 `id`（如 `slide-cover`、`slide-toc`）和顺序
4. 读取模板文件：`templates/<theme>/style.css`、`script.js`、`skeleton.html`

### Step 1: 写入骨架

1. 读取 `templates/<theme>/skeleton.html` 作为基础骨架
2. 替换占位变量：`{{TITLE}}`、`{{PRESENTATION_TITLE}}`、`{{SUBTITLE}}`、`{{DATE}}`、`{{DEPARTMENT}}`、`{{BADGE}}`
3. 将 `style.css` 和 `script.js` 的**完整内容**分别嵌入 `<style>` 和 `<script>` 标签（禁止替换或截断原始样式）
4. **此时 index.html 只包含封面页**，后续页面逐页追加

> 💡 为什么内联 CSS/JS：H5 需要**单文件可移植**，所有样式和交互必须内联到 `<style>` 和 `<script>` 标签中。

### Step 2: 逐页写入内容

按 `slideOrder` 数组顺序，**每次写入 1-2 个页面**，插入到 `<div class="presentation">` 内部：

1. 查阅 `templates/<theme>/page-templates.md` 获取页面 HTML 结构
2. 每个页面为 `<section class="slide" id="slide-xxx">...</section>`
3. 追加到 `<div class="presentation">` 内部，注释 `<!-- 在此追加更多页面 -->` 之后
4. 更新文件底部的 `slideOrder` 数组，加入新页面的 id

**页面类型参考**：
| 类型 | 用途 | id 命名建议 |
|------|------|------------|
| 封面页 | 开篇展示 | `slide-cover` |
| 目录页 | 章节导航 | `slide-toc` |
| 三栏卡片 | 并列要点 | `slide-cards` |
| 对比表格 | 方案对比 | `slide-compare` |
| 两栏布局 | 信息+图表 | `slide-info` |
| 数据展示 | 关键指标 | `slide-stats` |
| 时间轴 | 发展历程 | `slide-timeline` |
| 图表页 | ECharts/Mermaid | `slide-chart` |
| 图片展示 | 项目截图 | `slide-images` |
| Q&A 页 | 问答过渡 | `slide-qa` |
| 附录页 | 补充材料 | `slide-appendix` |

### Step 3: 校验

完成所有内容页写入后，执行以下检查：

#### 3a. Mermaid 语法校验（必须）

```bash
python3 scripts/validate_mermaid.py index.html
```

如果发现问题，使用 `--fix` 自动修复：

```bash
python3 scripts/validate_mermaid.py index.html --fix
```

> Mermaid 常见陷阱：节点文本中的 `<` `>` 必须用引号包裹 `["text"]` 或使用实体 `&lt;` `&gt;`。详见 [Mermaid 安全规则](#mermaid-安全规则)。

#### 3b. 结构校验

- [ ] `slideOrder` 数组中的 id 与 HTML 中的 `<section id="...">` 一一对应
- [ ] 封面页 `<section>` 有 `active` 类
- [ ] 封面 `id="slide-cover"` 在 `slideOrder` 首位
- [ ] 所有图片路径可访问
- [ ] ECharts `data-option` 是合法 JSON
- [ ] `slideOrder` 长度 = 页码分母（`totalPages`）

#### 3c. 可读性校验

- [ ] 正文内容字号 ≥ 14px（推荐 15-18px）
- [ ] 每页内容不超过 7 个要点
- [ ] 无大段文字（应使用列表）
- [ ] `body` 背景色为浅色系纯色（如 `#e8f4fc`），禁止高对比度渐变（防止切换闪烁）

### Step 4: 输出最终产物

1. 确认 `index.html` 完整可运行（浏览器打开验证）
2. 输出产物清单：

```
✅ H5 汇报材料已生成
📁 文件: <output-path>/index.html (<N> 页, <size>)
```

---

## 模板系统

### 当前可用模板

| 模板 ID | 风格 | 适用场景 |
|---------|------|---------|
| `light-gradient` | 浅蓝渐变背景 | 技术分享、产品介绍、项目汇报（默认） |
| `blue-business` | 深蓝商务渐变 | 年度/季度汇报、工作总结 |

### 扩展新模板

详见 `templates/README.md`。核心步骤：
1. 在 `templates/` 下创建新目录
2. 提供 `style.css`、`script.js`、`skeleton.html`、`page-templates.md`
3. 在 `templates/README.md` 中注册

---

## Mermaid 安全规则

Mermaid 代码块中 `<` `>` `&` 等字符会导致渲染失败，**生成时必须遵守**：

### 规则

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

### 校验工具

`scripts/validate_mermaid.py` 支持：
- 检测裸 `<` `>` `&` 字符（排除 Mermaid 箭头语法 `-->` `===` 等）
- 检测引号包裹状态
- 检测关键字冲突
- `--fix` 自动修复
- `--json` 结构化输出
- `--stdin` 管道输入

---

## 设计约束

### 投屏优先

H5 主要用于会议室投屏，观看距离 2-5 米：

| 元素 | 最小字号 |
|------|---------|
| 封面标题 | 52px |
| 页面标题 | 26px |
| 卡片标题 | 17px |
| 正文内容 | 14px |
| 表格内容 | 13px |

> 禁止为"塞入更多内容"而缩小字体。内容过多时拆分为多页。

### 背景色规则

- `body` 背景色**必须为浅色系纯色**（如 `#e8f4fc`），与 `.slide` 背景色系一致
- **禁止**高对比度渐变（如紫色 `#667eea → #764ba2`），切换幻灯片时会导致闪烁
- `.slide` 内部可使用浅渐变（如 `#f0f7ff → #ffffff → #f8fcff`）

### 每页内容密度

- 1 个主标题（+ 可选副标题）
- 3-7 个关键要点
- 0-2 个图表/图片
- 使用列表，避免大段文字

### 信息层级

1. **一级**：页面标题（蓝色，底部蓝色分割线）
2. **二级**：卡片/区块标题
3. **三级**：正文内容
4. **强调**：数字指标用大字号突出，颜色标签表优先级

---

## 图表集成

### ECharts

在 `<section>` 中使用 `data-option` 属性传递配置（JSON 字符串），`script.js` 自动初始化：

```html
<section class="slide" id="slide-chart">
    <h1 class="page-title">数据图表</h1>
    <div class="echart" data-option='{"xAxis":{"type":"category","data":["Q1","Q2"]},"yAxis":{"type":"value"},"series":[{"data":[100,200],"type":"bar"}]}' style="height: 450px;"></div>
</section>
```

详细配置参考 `references/charts-data.md`。

### Mermaid

使用 `data-code` 属性传递 Mermaid 代码：

```html
<section class="slide" id="slide-flow">
    <h1 class="page-title">流程图</h1>
    <div class="mermaid-diagram" data-code="flowchart LR
    A[&quot;开始&quot;] --> B[&quot;处理&quot;]
    B --> C[&quot;结束&quot;]"></div>
</section>
```

> ⚠️ `data-code` 中的 `<` `>` 必须用 HTML 实体 `&quot;` 转义，或用 `["text"]` 引号包裹节点文本。生成后必须运行校验脚本。

---

## 交互功能

以下功能由 `script.js` 提供，无需额外配置：

- **幻灯片切换**：键盘方向键（←/→）、空格键、右下导航按钮
- **页码显示**：右下胶囊形导航中 `当前页 / 总页数`
- **ECharts 渲染**：自动初始化 `.echart[data-option]` 元素
- **Mermaid 渲染**：自动渲染 `.mermaid-diagram[data-code]` 元素（或 `<pre class="mermaid">` 代码块）
- **图片 Lightbox**：点击 `.image-item img` 触发全屏预览
- **响应式布局**：1200px / 768px 断点自动适配

---

## 参考文档

| 文件 | 内容 |
|------|------|
| `templates/README.md` | 模板系统说明与扩展指南 |
| `templates/light-gradient/page-templates.md` | 浅蓝渐变主题页面 HTML 结构 |
| `templates/blue-business/page-templates.md` | 蓝色商务主题页面 HTML 结构 |
| `references/charts-data.md` | ECharts 图表配置参考 |
| `references/optimization.md` | 性能优化建议 |
| `references/responsive-design.md` | 响应式设计指南 |
| `references/troubleshooting.md` | 常见问题排查 |

---

**更新日期**：2026-08-05
**版本**：4.0
**维护者**：vincentruan
