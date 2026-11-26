# Templates — 汇报模板注册中心

本目录包含 H5 汇报演示系统的主题模板，全部面向 **PC 端 16:9 投屏**。

## 当前模板

`templates/deck/` 是一套**主题系统**：一份 HTML 结构（`style.css`）+ 一份交互引擎（`script.js`）+ `themes/` 下四个独立的皮肤文件。主题通过 `<html data-theme="…">` 选择，页面结构不随主题变化。

| 模板 ID（`data-theme`） | 风格 | 状态 |
|------------------------|------|------|
| `light-gradient` | 浅蓝渐变，清爽现代（**默认**） | ✅ 内置 |
| `kraft-paper` | 牛皮纸，暖棕 + 宋体，杂志感 | ✅ 内置 |
| `dune` | 沙丘，沙色 + 炭黑，克制高级 | ✅ 内置 |
| `ink-classic` | 墨水经典，纸白 + 近黑 + 衬线 | ✅ 内置 |

### 主题必备能力

四个主题都实现同一套结构契约与语义令牌：顶部 `.progress-bar`、右下 `.navigation` + `.page-indicator`、目录 `.toc-cell > .toc-concl + .toc-points`、内容页 `.lead-bar`、封面 `.cover-chips`、演讲者视图 `.presenter`。

`h5-report-template.html` 是默认主题（`light-gradient`）的单文件完整示例，含 6 页内容与 6 条 `SPEAKER_NOTES`，可直接打开预览。

⚠️ **不要手工编辑这个示例文件**。它由 `scripts/sync-template.py` 从 `deck/` 机械生成：

```bash
python3 scripts/sync-template.py .        # 在 skill 根目录执行
```

脚本按三个槽位替换内容，其余部分（页面 HTML、演讲备注）原样保留：

| 槽位 | 内容来源 |
|------|---------|
| `/* === STYLE_CSS === */` | `deck/style.css` |
| `/* === THEME_CSS === */` | `deck/themes/light-gradient.css`（`DEFAULT_THEME`） |
| `/* === SCRIPT_JS === */` | `deck/script.js` |

改完 `deck/` 下的样式或脚本，重跑一次脚本即可，示例永远是机械拷贝。想看其他主题效果，把 `DEFAULT_THEME` 改掉再跑一次。

## 目录约定

模板放在 `deck/` 下，**必须**包含以下文件：

| 文件 | 用途 |
|------|------|
| `style.css` | **只放结构**：结构令牌（字号/间距/圆角/页内边距）+ 全部组件样式 + 演讲者视图样式 |
| `themes/<id>.css` | 一个主题一个文件，**只含皮肤令牌**（颜色/字体/阴影），一个 `[data-theme="<id>"] { … }` 块 |
| `script.js` | 交互逻辑（幻灯片引擎、图表初始化、图片预览、演讲者视图与双屏同步） |
| `skeleton.html` | HTML 骨架模板，包含占位变量和页面结构 |
| `page-templates.md` | 页面类型 HTML 结构规范 + 备注契约 |
| `README.md` | 模板说明（主题清单、占位变量、演讲者视图要点） |

> **装配顺序不能反**：先 `style.css` 再 `themes/<id>.css`。两个文件在层级上不可互换——结构先立骨架，皮肤后覆盖令牌。`skeleton.html` 的 `<style>` 里就是按这个顺序摆的两个槽位。

## 占位变量约定

`skeleton.html` 中使用 `{{VARIABLE}}` 标记占位符，生成时替换为实际内容：

| 变量 | 含义 | 示例 |
|------|------|------|
| `{{THEME}}` | 主题 ID（`data-theme`） | `light-gradient` / `kraft-paper` / `dune` / `ink-classic` |
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
| `window.SPEAKER_NOTES = [ … ]` | 末尾脚本块 | 每页一条，`id` 对齐 `data-slide-id` |

## 新增主题

主题 = `deck/themes/` 下的一个新文件。结构与脚本完全复用，不要复制目录。

1. 新建 `deck/themes/<id>.css`，写一个 `[data-theme="<id>"] { … }` 块
2. 覆盖**全部**皮肤令牌（44 个），完整清单看现有主题文件：`--accent` / `--accent-2` / `--accent-3` / `--accent-rgb` / `--accent-ink` / `--accent-ink-2` / `--on-accent` / `--accent-fill` / `--paper` / `--slide-bg` / `--surface` / `--surface-soft` / `--tint` / `--tint-soft` / `--tint-strong` / `--ink` / `--ink-rgb` / `--text-body` / `--text-muted` / `--ink-faint` / `--line` / `--line-2` / `--danger` 系列 / `--warn` 系列 / `--ok` 系列 / `--glass` / 三个 `--shadow-*` / `--font-display` / `--font-body`
3. **不要**声明结构令牌（`--fs-*` / `--gap-*` / `--radius-*` / `--pad-*` / `--page-min-h`）——它们由 `style.css` 统一负责，写进主题会让不同主题的字号间距漂移
4. 漏掉任何一个皮肤令牌，该元素会掉回浏览器默认值（通常是黑色或衬线体），视觉上非常明显——逐项对照一个现有主题文件检查
5. 在本表格和 `deck/README.md` 的主题表里登记

校验一行命令够用：`for f in deck/themes/*.css; do echo "$f $(grep -c -- '^    --' $f)"; done`，四个文件应输出相同的令牌数。

## 使用方式

SKILL.md 的生成流程：

1. Step 0 读取本目录与 `deck/` 下的模板文件，确认用户主题选择（默认 `light-gradient`）
2. Step 1 把 `style.css` + `themes/<选定主题>.css` + `script.js` 内联进 `skeleton.html`，替换占位变量（含 `{{THEME}}`）
3. Step 2 按 `deck/page-templates.md` 的三段式逐页写入内容，每页带 `data-slide-id`
4. Step 3 写 `SPEAKER_NOTES`（每页一条，`id` 对齐 `data-slide-id`），再跑结构与投屏校验
