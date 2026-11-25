# Templates — 汇报模板注册中心

本目录包含 H5 汇报演示系统的主题模板。当前只维护一个主题，面向 **PC 端 16:9 投屏**。

## 当前模板

| 模板 ID | 目录 | 风格 | 状态 |
|---------|------|------|------|
| `light-gradient` | `light-gradient/` | 浅蓝渐变，结论先行结构完整（进度条 + 目录结论卡 + 结论条） | ✅ 唯一主题 |

### 主题必备能力

顶部 `.progress-bar`、右下 `.navigation` + `.page-indicator`、目录 `.toc-cell > .toc-concl + .toc-points`、内容页 `.lead-bar`、封面 `.cover-chips`。

`h5-report-template.html` 为 `light-gradient` 的单文件完整示例，可直接打开预览。

## 目录约定

每个模板目录**必须**包含以下文件：

| 文件 | 用途 |
|------|------|
| `style.css` | 完整 CSS 样式表，定义主题色、布局、组件样式 |
| `script.js` | 交互逻辑（幻灯片引擎、图表初始化、图片预览） |
| `skeleton.html` | HTML 骨架模板，包含占位变量和页面结构 |
| `page-templates.md` | 该主题下各页面类型的 HTML 结构规范 |
| `README.md` | 模板说明（风格描述、适用场景） |

## 占位变量约定

`skeleton.html` 中使用 `{{VARIABLE}}` 标记占位符，生成时替换为实际内容：

| 变量 | 含义 | 示例 |
|------|------|------|
| `{{TITLE}}` | 页面标题（`<title>` 标签） | 2026年第三季度风控运营汇报 |
| `{{PRESENTATION_TITLE}}` | 封面主标题（`<h1>`） | 2024年度工作总结 |
| `{{SUBTITLE}}` | 封面副标题 | 技术部门年度汇报 |
| `{{BADGE}}` | 封面顶部徽章标签 | 风控运营部 · 季度汇报（2026.07–09） |
| `{{DATE}}` | 封面日期 | 2024-12-31 |
| `{{AUTHOR}}` | 封面汇报人 | 张三 |
| `{{DEPARTMENT}}` | 封面科室/部门 | 技术研发部 |
| `{{COVER_CHIPS}}` | 封面结论胶囊 HTML（2–3 个） | `<div class="cover-chip">…</div>` |
| `{{TOC_TAGLINE}}` | 目录副标题 | 结论先行 |
| `{{TOC_CELLS}}` | 目录结论卡 HTML | 每章一个 `.toc-cell` |
| `{{PAGES}}` | 内容页 `<section>` 序列 | 按顺序排列 |
| `{{END_ICON}}` | 收尾页图标 | 🛡️ |
| `{{CLOSE_LINES}}` | 收尾页结论复述 | 3 条以内 `.close-line` |

## 新增主题（可选）

默认只维护 `light-gradient`。确有需要时再新增：

1. 复制 `light-gradient/` 为新目录（如 `tech-dark/`）
2. 修改 `style.css` 中的 CSS 变量（`--primary-blue` 等）实现换色
3. 调整 `skeleton.html` 结构（如需要不同的布局）
4. 更新 `page-templates.md` 中的页面 HTML 结构
5. 更新 `script.js`（如需要特殊交互效果）
6. 在 SKILL.md 的模板选择步骤中注册新模板

## 使用方式

SKILL.md 固定使用 `light-gradient` 主题：
1. Step 0 读取本目录与 `light-gradient/` 下的模板文件
2. Step 1 把 `style.css` / `script.js` 内联进 `skeleton.html`
3. Step 2 按 `light-gradient/page-templates.md` 的三段式逐页写入内容
