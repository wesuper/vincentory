# 响应式设计指南

## 内容索引

- 视口设置
- 断点设置
- 核心布局适配
- 移动端优化
- 图表适配
- 测试建议
- 完整示例


本指南介绍如何为H5汇报材料添加移动设备支持，确保在不同屏幕尺寸下都能正常显示。

## 视口设置

在HTML的`<head>`部分添加：

```html
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
```

## 断点设置

`deck` 主题系统内置三组媒体查询，新增主题时建议沿用：

| 查询 | 作用 |
|------|------|
| `@media (max-height: 820px)` | 1366×768 投屏等矮屏：压缩目录卡字号与间距，保证一页放得下 |
| `@media (max-width: 1200px)` | 小笔记本/平板横屏：缩小页面左右内边距 |
| `@media (max-width: 768px)` | 手机竖屏：单列布局，导航压缩 |

> 页面高度用 `--pad-top` / `--pad-bottom` / `--page-min-h` 三个 CSS 变量控制，不要在各组件里硬编码 `calc(100vh - Npx)`。

推荐断点：

```css
/* 小屏设备 (手机竖屏) */
@media (max-width: 768px) { }

/* 中等设备 (手机横屏/小平板) */
@media (min-width: 769px) and (max-width: 1024px) { }

/* 大屏设备 (桌面) */
@media (min-width: 1025px) { }
```

## 核心布局适配

### 1. 导航控制适配

```css
.nav-controls {
    bottom: 20px;
    padding: 12px 20px;
    gap: 15px;
}

@media (max-width: 768px) {
    .nav-controls {
        bottom: 10px;
        padding: 8px 15px;
        gap: 10px;
    }
    .nav-btn {
        padding: 8px 15px;
        font-size: 14px;
    }
}
```

### 2. 幻灯片内容适配

```css
.slide {
    padding: 20px 30px;  /* 桌面 */
}

@media (max-width: 768px) {
    .slide {
        padding: 15px 20px;
    }
}
```

### 3. 三栏布局适配

```css
.three-columns {
    grid-template-columns: repeat(3, 1fr);  /* 桌面 */
}

@media (max-width: 1024px) {
    .three-columns {
        grid-template-columns: repeat(2, 1fr);  /* 平板 */
    }
}

@media (max-width: 768px) {
    .three-columns {
        grid-template-columns: 1fr;  /* 手机 */
    }
}
```

### 4. 标题字体适配

```css
.page-title {
    font-size: 32px;  /* 桌面 */
}

@media (max-width: 768px) {
    .page-title {
        font-size: 24px;
        margin-bottom: 20px;
    }
}

.column-header h3 {
    font-size: 28px;  /* 桌面 */
}

@media (max-width: 768px) {
    .column-header h3 {
        font-size: 20px;
    }
}
```

### 5. 目录页适配

```css
#slide-toc1 > div {
    display: flex;
    gap: 30px;
}

@media (max-width: 768px) {
    #slide-toc1 > div {
        flex-direction: column;
        gap: 15px;
    }
}
```

### 6. 表格适配

```css
.comparison-table {
    overflow-x: auto;  /* 允许横向滚动 */
}

@media (max-width: 768px) {
    .comparison-table table {
        min-width: 600px;  /* 最小宽度 */
    }
}
```

## 移动端优化

### 触摸友好

```css
.nav-btn,
.column-card {
    min-height: 44px;  /* 符合Apple人机界面指南 */
}

.column-card {
    cursor: pointer;
    -webkit-tap-highlight-color: rgba(0,0,0,0.1);  /* 去除点击高亮 */
}
```

### 性能优化

```css
/* 减少阴影动画 */
@media (max-width: 768px) {
    .column-card {
        transition: none;  /* 移除动画 */
    }
}

/* 简化背景渐变 */
@media (max-width: 768px) {
    body {
        background: var(--primary-blue);  /* 纯色背景 */
    }
}
```

## 图表适配

### ECharts响应式

```javascript
window.addEventListener('resize', function() {
    myChart.resize();
});
```

### Mermaid图表适配

```css
@media (max-width: 768px) {
    .mermaid {
        font-size: 12px;  /* 缩小字体 */
    }
}
```

## 测试建议

1. **设备测试**：
   - iPhone SE (375px)
   - iPad (768px)
   - 桌面 (1024px+)

2. **浏览器测试**：
   - Safari (iOS)
   - Chrome (Android)
   - Safari/Chrome (桌面)

3. **检查项目**：
   - 内容是否完整显示
   - 导航是否易用
   - 文字是否清晰可读
   - 操作是否响应及时

## 完整示例

响应式实现见 `assets/h5-report-template.html`（由 `deck/style.css` 内联生成），三组断点定义在 `assets/deck/style.css` 末尾的 `@media` 块中。

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>{{TITLE}}</title>
    <!-- 其他head内容... -->
    <style>
        /* 基础样式... */

        /* 平板适配 */
        @media (max-width: 1024px) {
            .three-columns { grid-template-columns: repeat(2, 1fr); }
        }

        /* 手机适配 */
        @media (max-width: 768px) {
            .slide { padding: 15px 20px; }
            .page-title { font-size: 24px; }
            .three-columns { grid-template-columns: 1fr; gap: 15px; }
            .nav-controls { bottom: 10px; padding: 8px 15px; }
            .nav-btn { padding: 6px 12px; font-size: 14px; }
        }
    </style>
</head>
<body>
    <!-- 页面内容... -->
</body>
</html>
```
