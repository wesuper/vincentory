# Light Gradient Theme

浅蓝到白色渐变背景的企业级 H5 汇报主题，视觉风格轻盈现代，适合技术分享、产品介绍、项目汇报。

## 文件清单

| 文件 | 用途 |
|------|------|
| `style.css` | 主题样式系统 |
| `script.js` | 幻灯片切换、Mermaid/ECharts 渲染、图片 Lightbox |
| `skeleton.html` | HTML 骨架模板 |
| `page-templates.md` | 页面类型 HTML 结构规范 |

## 设计特点

- 主色：`#0066cc` 明亮蓝
- 背景：`#f0f7ff → #ffffff → #f8fcff` 浅蓝到白色渐变
- body 背景：`#e8f4fc`（纯色，避免切换闪烁）
- 导航：右下胶囊形半透明控制条
- 卡片：圆角 + 大阴影 + 悬停上浮效果
- 响应式：支持 1200px 和 768px 断点

## 占位变量

| 变量 | 位置 | 含义 |
|------|------|------|
| `{{TITLE}}` | `<title>` | 页面标题 |
| `{{PRESENTATION_TITLE}}` | 封面 `<h1>` | 汇报主标题 |
| `{{SUBTITLE}}` | 封面副标题 | 副标题 |
| `{{DEPARTMENT}}` | 封面底部 | 汇报人/部门 |
| `{{DATE}}` | 封面底部 | 日期 |
| `{{BADGE}}` | 封面顶部 | 徽章标签 |
