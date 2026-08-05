# Light Gradient Theme — 页面类型 HTML 结构

> 适用于 `templates/light-gradient/` 主题。

## 通用约定

- 每页是一个 `<section class="slide" id="slide-xxx">` 元素
- 第一页（封面）需要 `class="slide active"`，其余只保留 `class="slide"`
- 页面 ID 必须同步到 `slideOrder` 数组中
- 页面追加位置：`<div class="presentation">` 内部、注释 `<!-- 在此追加更多页面 -->` 之后
- `body` 背景色已由主题固定为 `#e8f4fc`，无需修改

---

## 1. 封面页

```html
<section class="slide active" id="slide-cover">
    <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 80vh;">
        <h1 style="font-size: 56px; font-weight: 700; color: var(--primary-blue); text-align: center; margin-bottom: 20px;">
            {{PRESENTATION_TITLE}}
        </h1>
    </div>
    <div style="position: absolute; bottom: 60px; left: 60px; font-size: 16px; color: #555; line-height: 1.8;">
        <p>汇报人：{{DEPARTMENT}}</p>
        <p>日期：{{DATE}}</p>
    </div>
</section>
```

---

## 2. 目录页

```html
<section class="slide" id="slide-toc">
    <div style="display: flex; height: 85vh;">
        <div style="width: 35%; background: linear-gradient(135deg, var(--primary-blue) 0%, #1a4a7a 100%); display: flex; flex-direction: column; justify-content: center; padding: 60px; position: relative; overflow: hidden;">
            <h1 style="color: white; font-size: 48px; font-weight: 700; margin-bottom: 20px;">目录</h1>
            <p style="color: rgba(255,255,255,0.7); font-size: 16px;">CONTENTS</p>
        </div>
        <div style="flex: 1; display: flex; flex-direction: column; justify-content: center; padding: 40px 60px; gap: 16px;">
            <div style="display: flex; align-items: center; gap: 24px; padding: 20px 30px; background: linear-gradient(135deg, #f0f7ff 0%, #e3f0ff 100%); border-radius: 16px; border-left: 5px solid var(--primary-blue); box-shadow: 0 6px 24px rgba(0,102,204,0.1);">
                <div style="width: 50px; height: 50px; background: linear-gradient(135deg, var(--primary-blue) 0%, var(--light-blue) 100%); border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 20px; font-weight: 700; flex-shrink: 0;">01</div>
                <div>
                    <h3 style="font-size: 20px; font-weight: 600; color: var(--primary-blue); margin-bottom: 4px;">章节标题</h3>
                    <p style="font-size: 13px; color: #666;">章节副标题</p>
                </div>
            </div>
        </div>
    </div>
</section>
```

---

## 3. 三栏卡片页

```html
<section class="slide" id="slide-xxx">
    <h1 class="page-title">页面标题</h1>
    <p class="page-subtitle">副标题说明</p>
    <div class="three-columns">
        <div class="column-card">
            <div class="column-header">
                <h3>卡片标题</h3>
                <p>英文/补充</p>
            </div>
            <div class="feature-tag">标签</div>
            <div class="column-features">
                <ul>
                    <li>要点 1</li>
                    <li>要点 2</li>
                    <li>要点 3</li>
                </ul>
            </div>
            <div class="column-status status-green">状态</div>
        </div>
        <!-- 更多卡片 -->
    </div>
</section>
```

---

## 4. 对比表格页

```html
<section class="slide" id="slide-xxx">
    <h1 class="page-title">页面标题</h1>
    <div class="comparison-table">
        <table>
            <thead>
                <tr>
                    <th style="width: 25%;">维度</th>
                    <th style="width: 25%;">方案 A</th>
                    <th style="width: 25%;">方案 B</th>
                    <th style="width: 25%;">结论</th>
                </tr>
            </thead>
            <tbody>
                <tr class="item-row">
                    <td><strong>维度 1</strong></td>
                    <td>数据 A</td>
                    <td>数据 B</td>
                    <td>结论</td>
                </tr>
            </tbody>
        </table>
    </div>
</section>
```

---

## 5. 两栏布局页

```html
<section class="slide" id="slide-xxx">
    <h1 class="page-title">页面标题</h1>
    <div class="two-columns">
        <div class="info-panel">
            <div class="info-section">
                <h4>左栏标题</h4>
                <ul>
                    <li>要点 1</li>
                    <li>要点 2</li>
                </ul>
            </div>
        </div>
        <div class="flow-diagram">
            <!-- 可放置 Mermaid 或 ECharts -->
        </div>
    </div>
</section>
```

---

## 6. 数据展示页

```html
<section class="slide" id="slide-xxx">
    <h1 class="page-title">页面标题</h1>
    <div class="stats-row">
        <div class="stat-card">
            <div class="stat-value">100</div>
            <div class="stat-label">指标名称</div>
        </div>
        <!-- 更多指标 -->
    </div>
</section>
```

---

## 7. 图片展示页

```html
<section class="slide" id="slide-images">
    <h1 class="page-title">图片展示</h1>
    <div class="image-showcase">
        <div class="image-item">
            <img src="image1.png" alt="说明文字 1">
            <div class="image-caption">说明文字 1</div>
        </div>
        <div class="image-item">
            <img src="image2.png" alt="说明文字 2">
            <div class="image-caption">说明文字 2</div>
        </div>
    </div>
</section>
```

> 点击图片会自动触发 Lightbox 全屏预览（由 `script.js` 提供）。

---

## 8. Mermaid 图表页

```html
<section class="slide" id="slide-xxx">
    <h1 class="page-title">流程图</h1>
    <div class="mermaid-diagram" data-code="flowchart LR
    A[&quot;节点 A&quot;] --> B[&quot;节点 B&quot;]
    B --> C[&quot;节点 C&quot;]"></div>
</section>
```

> 节点文本含 `<` `>` `&` 时，必须用 `["text"]` 引号包裹。生成后运行 `validate_mermaid.py` 校验。

---

## 9. ECharts 图表页

```html
<section class="slide" id="slide-xxx">
    <h1 class="page-title">数据图表</h1>
    <div class="echart" data-option='{"xAxis":{"type":"category","data":["Q1","Q2"]},"yAxis":{"type":"value"},"series":[{"data":[100,200],"type":"bar"}]}' style="height: 450px;"></div>
</section>
```

---

## 10. Q&A / 附录页

```html
<section class="slide" id="slide-qa">
    <div style="display: flex; flex-direction: column; justify-content: center; align-items: center; height: 80vh;">
        <h1 style="font-size: 120px; font-weight: 700; color: var(--primary-blue); text-align: center;">Q&A</h1>
    </div>
</section>
```
