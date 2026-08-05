# Templates — 汇报模板注册中心

本目录包含 H5 汇报演示系统的**可替换主题模板**。每个子目录代表一套完整的视觉主题。

## 当前模板

| 模板 ID | 目录 | 风格 | 状态 |
|---------|------|------|------|
| `light-gradient` | `light-gradient/` | 浅蓝到白色渐变背景，轻盈现代 | ✅ 可用（默认） |
| `blue-business` | `blue-business/` | 深蓝商务渐变，卡片布局 | ✅ 可用 |

另有 `h5-report-template.html` 为 `light-gradient` 主题的单文件完整预览。

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
| `{{TITLE}}` | 页面标题（`<title>` 标签） | Open Code Review |
| `{{PRESENTATION_TITLE}}` | 封面主标题 | 2024年度工作总结 |
| `{{SUBTITLE}}` | 封面副标题 | 技术部门年度汇报 |
| `{{BADGE}}` | 封面顶部徽章标签 | ANNUAL REPORT |
| `{{DATE}}` | 封面底部日期 | 2024-12-31 |
| `{{DEPARTMENT}}` | 封面底部汇报人/部门 | 技术研发部 |

## 扩展新模板

1. 复制 `blue-business/` 为新目录（如 `tech-dark/`）
2. 修改 `style.css` 中的 CSS 变量（`--primary-blue` 等）实现换色
3. 调整 `skeleton.html` 结构（如需要不同的布局）
4. 更新 `page-templates.md` 中的页面 HTML 结构
5. 更新 `script.js`（如需要特殊交互效果）
6. 在 SKILL.md 的模板选择步骤中注册新模板

## 使用方式

SKILL.md 工作流程中的"模板选择"步骤会：
1. 读取本目录下的模板列表
2. 根据用户需求或使用默认模板（`blue-business`）
3. 将对应模板的 CSS/JS/HTML 组装为最终产物
