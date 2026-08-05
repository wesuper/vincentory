# Blue Business 主题 — 页面模板规范

本文件定义蓝色商务主题下各页面类型的 HTML 结构。生成 H5 时，按此结构组装页面内容。

> CSS 类名定义在 `style.css` 中，交互逻辑在 `script.js` 中。

## 页面结构约定

每个页面是一个 `<div class="slide">` 元素，通过 `data-page` 属性标识：

```html
<div class="slide" data-page="页面唯一ID">
    <!-- 页面内容 -->
</div>
```

第一页（封面）需添加 `active` 类：`<div class="slide active" data-page="cover">`

---

## 1. 封面页 (cover)

深蓝渐变全屏背景 + 装饰圆环 + 标题居中。

```html
<div class="slide active" data-page="cover">
    <div class="cover-page">
        <div class="cover-decoration">
            <div class="deco-circle deco-circle-1"></div>
            <div class="deco-circle deco-circle-2"></div>
            <div class="deco-circle deco-circle-3"></div>
            <div class="deco-line deco-line-1"></div>
            <div class="deco-line deco-line-2"></div>
        </div>
        <div class="cover-badge">ANNUAL REPORT</div>
        <h1 class="cover-title">汇报标题</h1>
        <p class="cover-subtitle">副标题说明</p>
        <div class="cover-info">
            <div class="cover-info-item"><span>📅</span> 2024-12-31</div>
            <div class="cover-info-item"><span>👤</span> 汇报人</div>
            <div class="cover-info-item"><span>🏢</span> 部门名称</div>
        </div>
    </div>
</div>
```

## 2. 目录页 (toc)

双栏布局，左右分栏展示章节列表。当前章节高亮，其他淡化。

```html
<div class="slide" data-page="toc">
    <div class="toc-page">
        <div class="toc-header">
            <div class="toc-icon">📋</div>
            <div>
                <div class="toc-title">目录</div>
                <div class="toc-subtitle">CONTENTS</div>
            </div>
        </div>
        <div class="toc-content">
            <!-- 左栏：章节 1-4 -->
            <div class="toc-column">
                <div class="toc-column-header">
                    <div class="toc-column-number">I</div>
                    <div class="toc-column-title">第一章标题</div>
                </div>
                <ul class="toc-list">
                    <li class="toc-item">
                        <span class="toc-item-number">01</span>
                        <span class="toc-item-title">小节标题</span>
                        <span class="toc-item-dot"></span>
                    </li>
                    <!-- 更多 toc-item -->
                </ul>
            </div>
            <!-- 右栏：章节 5-8 -->
            <div class="toc-column">
                <!-- 结构同上 -->
            </div>
        </div>
    </div>
</div>
```

## 3. 内容页 — 三栏卡片 (content-cards)

```html
<div class="slide" data-page="content-1">
    <div class="content-page">
        <div class="content-header">
            <div class="content-number">01</div>
            <div>
                <div class="content-title">页面标题</div>
                <div class="content-subtitle">SECTION TITLE</div>
            </div>
        </div>
        <div class="content-body">
            <div class="card-grid">
                <div class="card">
                    <div class="card-icon">🚀</div>
                    <div class="card-title">模块标题</div>
                    <ul class="card-list">
                        <li class="card-item">
                            <span class="card-item-dot"></span>
                            <span>功能点描述</span>
                        </li>
                    </ul>
                </div>
                <!-- 更多 card（最多 3 个） -->
            </div>
        </div>
    </div>
</div>
```

## 4. 内容页 — 对比表格 (content-table)

```html
<div class="slide" data-page="content-2">
    <div class="content-page">
        <div class="content-header">
            <div class="content-number">02</div>
            <div>
                <div class="content-title">对比分析</div>
                <div class="content-subtitle">COMPARISON</div>
            </div>
        </div>
        <div class="content-body">
            <table class="comparison-table">
                <thead>
                    <tr>
                        <th>对比项</th>
                        <th>方案 A</th>
                        <th>方案 B</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>指标 1</td>
                        <td>数据</td>
                        <td>数据</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>
```

## 5. 内容页 — 时间轴 (content-timeline)

```html
<div class="slide" data-page="content-3">
    <div class="content-page">
        <div class="content-header">
            <div class="content-number">03</div>
            <div>
                <div class="content-title">发展历程</div>
                <div class="content-subtitle">TIMELINE</div>
            </div>
        </div>
        <div class="content-body">
            <div class="timeline">
                <div class="timeline-item">
                    <div class="timeline-dot"></div>
                    <div class="timeline-content">
                        <div class="timeline-title">阶段标题</div>
                        <div class="timeline-desc">详细描述</div>
                    </div>
                </div>
                <!-- 更多 timeline-item -->
            </div>
        </div>
    </div>
</div>
```

## 6. 内容页 — 数据展示 (content-stats)

```html
<div class="slide" data-page="content-4">
    <div class="content-page">
        <div class="content-header">
            <!-- 同上 -->
        </div>
        <div class="content-body">
            <div class="stats-row">
                <div class="stat-card">
                    <div class="stat-value">128</div>
                    <div class="stat-label">指标名称</div>
                </div>
                <!-- 最多 4 个 stat-card -->
            </div>
            <div class="chart-container">
                <div class="chart-title">图表标题</div>
                <!-- ECharts 或 Mermaid 图表容器 -->
            </div>
        </div>
    </div>
</div>
```

## 7. 图表页

### ECharts

```html
<div class="chart-container">
    <div class="chart-title">数据趋势</div>
    <div class="echart" data-option='{
        "xAxis": {"type": "category", "data": ["一月","二月","三月"]},
        "yAxis": {"type": "value"},
        "series": [{"data": [120, 200, 150], "type": "bar"}]
    }' style="height: 350px;"></div>
</div>
```

> `data-option` 的值是 JSON 字符串，由 `script.js` 中的 `initCharts()` 解析并渲染。

### Mermaid

```html
<div class="chart-container">
    <div class="chart-title">流程图</div>
    <div class="mermaid-diagram" data-code="flowchart TB
    A[开始] --> B[处理]
    B --> C{判断}
    C -->|是| D[完成]
    C -->|否| B"></div>
</div>
```

> `data-code` 的值由 `script.js` 中的 `initMermaid()` 解析并渲染。
> **注意**：`data-code` 中的 `<` `>` 必须用 `&lt;` `&gt;` 转义，或使用引号包裹节点文本 `["text"]`。

## 8. 图片展示页 (content-images)

```html
<div class="slide" data-page="content-5">
    <div class="content-page">
        <div class="content-header">
            <!-- 同上 -->
        </div>
        <div class="content-body">
            <div class="image-showcase">
                <div class="image-item">
                    <img src="path/to/image.jpg" alt="描述">
                    <div class="image-caption">图片说明</div>
                </div>
                <!-- 最多 4 张 -->
            </div>
        </div>
    </div>
</div>
```

> 图片点击触发 Lightbox 全屏预览（由 `script.js` 中 `ImagePreview` 类处理）。

## 9. Q&A 页 (qa)

深蓝渐变背景 + 居中动画图标。

```html
<div class="slide" data-page="qa">
    <div class="qa-page">
        <div class="qa-decoration">
            <div class="qa-circle qa-circle-1"></div>
            <div class="qa-circle qa-circle-2"></div>
        </div>
        <div class="qa-icon">💬</div>
        <div class="qa-title">Q&A</div>
        <div class="qa-subtitle">欢迎提问与交流</div>
    </div>
</div>
```

## 10. 附录页 (appendix)

浅蓝渐变背景 + 表格/文字内容。

```html
<div class="slide" data-page="appendix">
    <div class="appendix-page">
        <div class="appendix-header">
            <div class="appendix-icon">📎</div>
            <div class="appendix-title">附录</div>
        </div>
        <div class="appendix-content">
            <div class="appendix-section">
                <div class="appendix-section-title">📌 术语说明</div>
                <table class="appendix-table">
                    <thead>
                        <tr><th>术语</th><th>说明</th></tr>
                    </thead>
                    <tbody>
                        <tr><td>ASR</td><td>自动语音识别</td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
```

---

## 设计约束

### 字体（投屏优先）

| 元素 | 最小字号 | 推荐字号 |
|------|---------|---------|
| 封面标题 | 52px | 56-68px |
| 页面标题 | 26px | 28-34px |
| 卡片标题 | 17px | 18-22px |
| 正文内容 | 14px | 15-18px |
| 标签/徽章 | 13px | 14-16px |

> 投屏最小可读距离 2-5 米，禁止为"塞入更多内容"而缩小字体。内容过多时应拆分为多页。

### 每页内容密度

- 1 个主标题
- 3-7 个关键要点
- 0-2 个图表/图片
- 避免大段文字，使用列表

### Mermaid 安全规则

1. **节点文本含 `<` `>` `&`**：必须用引号包裹 `A["文本 <tag>"]` 或使用 HTML 实体 `&lt;` `&gt;`
2. **子图标题含特殊字符**：必须用引号包裹 `subgraph "标题 <标记>"`
3. **禁止使用 Mermaid 关键字作为节点 ID**：如 `graph`, `flowchart`, `sequenceDiagram` 等
4. **生成后必须运行校验**：`python3 scripts/validate_mermaid.py <file>`
