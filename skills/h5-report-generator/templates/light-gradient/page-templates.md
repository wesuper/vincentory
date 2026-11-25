# Light Gradient Theme — 页面类型 HTML 结构 (v5)

> 适用于 `templates/light-gradient/` 主题。本文件是**结构契约**：照抄骨架、替换文字即可。

## 通用约定

- 每页是一个 `<section class="slide" id="slide-<页面名>">` 元素，id 全局唯一
- **页面顺序 = DOM 顺序**，无需维护 `slideOrder` 数组（脚本按 DOM 顺序生成页码与进度）
- 第一页（封面）带 `class="slide active"`，其余只写 `class="slide"`
- 追加位置：`<div class="presentation">` 内部、`{{PAGES}}` 占位处
- `body` 背景色由主题固定为 `#e8f4fc`，不要改
- 章节编号与目录中的罗马数字（Ⅰ Ⅱ Ⅲ …）保持一致

### 每页必备的三段式（结构契约，缺一即为不合格）

| 段落 | 元素 | 要求 |
|------|------|------|
| ① 页面标题 | `.content-page` 的直接子元素 `.content-header` | 圆形编号 `.content-number`（两位数字符串 `01` `02`…，按**内容页**出现顺序连续编号，封面/目录/收尾不计入）+ `.content-title`（标题即结论）+ 英文副标题 `.content-subtitle` |
| ② 结论条 | `.content-body` 的**第一个子元素** `.lead-bar` | `<b>结论：</b>` 开头，一句话说清"所以呢" |
| ③ 展开区 | `.content-body` 内 `.lead-bar` 之后的卡片/表格/图表 | 3–7 个要点，不一页塞满 |

> 结构即 `.content-page > .content-header + .content-body > .lead-bar + …`。`lead-bar` 必须在 `content-body` 内部、且排第一，不能提到 `.content-page` 这一层。

> **第 6–13 节给的是"展开区片段"**（`.chain-grid`、`.week-panel`、`.fold-section`、`.risk-cards`、`.timeline`、`.chart-container`、`.image-showcase` 等），它们只替换 ③ 展开区。使用时仍需自己套上 `.content-page > .content-header + .content-body > .lead-bar` 三段式外壳；第 1–5、14 节给的是完整页面示例。

> 结论先行：标题写结论、`lead-bar` 复述结论、展开区再给证据。管理层只看标题与结论条也能带走信息。

---

## 1. 封面页

```html
<section class="slide active" id="slide-cover">
    <div class="cover-page">
        <div class="cover-decoration">
            <div class="deco-circle deco-circle-1"></div>
            <div class="deco-circle deco-circle-2"></div>
            <div class="deco-circle deco-circle-3"></div>
            <div class="deco-line deco-line-1"></div>
            <div class="deco-line deco-line-2"></div>
        </div>
        <div class="cover-badge">部门 · 专项名称（时间范围）</div>
        <h1 class="cover-title">主标题<br>可换行</h1>
        <p class="cover-subtitle">副标题：一句话说明汇报背景与范围</p>
        <div class="cover-info">
            <div class="cover-info-item"><span class="ci-k">日期</span> 2026-11-03</div>
            <div class="cover-info-item"><span class="ci-k">汇报人</span> 张三</div>
            <div class="cover-info-item"><span class="ci-k">科室</span> 某某开发室</div>
        </div>
        <div class="cover-chips">
            <div class="cover-chip">核心数字＝<b>2</b>项已完成 · <b>15</b>项推进中</div>
            <div class="cover-chip alert">关键风险期 <b>零变更</b></div>
            <div class="cover-chip">资源就绪 · <b>已扩容</b></div>
        </div>
        <div class="cover-hint">← / → 方向键翻页</div>
    </div>
</section>
```

**封面结论胶囊规则**
- 2–3 个，最多 3 个；每个不超过一行，数字用 `<b>` 包住
- 有风险/冻结/延期类信息时，该胶囊加 `class="cover-chip alert"`（红边红字）
- 不要在封面放图表或长段文字

---

## 2. 目录页

```html
<section class="slide" id="slide-toc">
    <div class="toc-page">
        <div class="toc-header">
            <div class="toc-icon">📋</div>
            <div>
                <div class="toc-title">目录</div>
                <div class="toc-subtitle">CONTENTS · 结论先行</div>
            </div>
        </div>
        <div class="toc-stack">
            <div class="toc-cell">
                <div class="toc-cell-header">
                    <div class="toc-column-number">Ⅰ</div>
                    <div class="toc-column-title">第一章标题</div>
                </div>
                <div class="toc-concl">一句话结论（本章最重要的判断，30 字内）。</div>
                <ul class="toc-points">
                    <li>要点一，含 <b>关键数字</b> 或关键举措</li>
                    <li>要点二，含 <b>关键数字</b> 或 <b class="hl">风险提示</b></li>
                </ul>
            </div>
            <!-- 每章一个 .toc-cell，建议 3–4 章 -->
        </div>
    </div>
</section>
```

**目录页规则（v5 新增，必须遵守）**
- 每个 `.toc-cell` **必须**包含：`.toc-cell-header`（章节编号 + 章节标题）+ `.toc-concl` 一句话结论 + `.toc-points` 2–3 条要点
- `.toc-concl` 与 `.toc-points` 是 `.toc-cell` 下**并列的两个子元素**：结论句写在 `.toc-concl` 里，`<ul class="toc-points">` 放在 `.toc-concl` **之后**，不要把 `<ul>` 嵌进结论句内部
- `.toc-concl` 用一句带 `<b>` 的结论句（不是"本章讲什么"，而是"本章的结论是什么"）
- `.toc-points` 每条 ≤ 40 字，数字/时间用 `<b>`；风险项用 `<b class="hl">`
- 3–4 章最佳；超过 4 章考虑合并，少于 3 章省略目录页

---

## 3. 三栏卡片页

```html
<section class="slide" id="slide-cards">
    <div class="content-page">
        <div class="content-header">
            <div class="content-number">01</div>
            <div>
                <div class="content-title">标题即结论：三方面并列推进，核心指标全部达成</div>
                <div class="content-subtitle">SECTION IN ENGLISH</div>
            </div>
        </div>
        <div class="content-body">
            <div class="lead-bar"><b>结论：</b>一句话总结本页 <b>关键数字</b> 与影响。</div>
            <div class="card-grid">
                <div class="card">
                    <div class="card-icon">🎯</div>
                    <div class="card-title">卡片标题</div>
                    <ul class="card-list">
                        <li class="card-item"><span class="card-item-dot"></span><span>要点一，含 <b>数字</b></span></li>
                        <li class="card-item"><span class="card-item-dot"></span><span>要点二</span></li>
                        <li class="card-item"><span class="card-item-dot"></span><span>要点三</span></li>
                    </ul>
                </div>
                <!-- 第二、第三张卡片 -->
            </div>
        </div>
    </div>
</section>
```

风险卡片：在 `.card` 上加 `class="card risk-card high"`（红顶边）或 `risk-card mh`（橙顶边），标题后加 `<span class="rk risk risk-high">风险：高</span>`。

---

## 4. 对比 / 明细表格页

```html
<section class="slide" id="slide-table">
    <div class="content-page">
        <div class="content-header">
            <div class="content-number">02</div>
            <div>
                <div class="content-title">标题即结论：N 项分级收口，关键窗口前完成</div>
                <div class="content-subtitle">CHANGE PLAN</div>
            </div>
        </div>
        <div class="content-body">
            <div class="lead-bar"><b>结论：</b>一句话总结分布与节奏。</div>
            <div class="principle-row">
                <div class="chip gold">关键节点 <b>11.05 前</b>完成</div>
                <div class="chip warn">冻结期 <b>零变更</b></div>
                <div class="chip">回退优先级：开关 &gt; 名单 &gt; 版本</div>
            </div>
            <div class="legend-bar"><b>图例</b>：灰字＝已完成 · 红左边条＝对客 · 风险
                <span class="legend-dot" style="background:var(--hl-red);"></span>高
                <span class="legend-dot" style="background:var(--hl-orange);"></span>中
                <span class="legend-dot" style="background:var(--ok-green);"></span>低
            </div>
            <table class="mini-table">
                <thead>
                    <tr><th>#</th><th>类别</th><th>要点</th><th>窗口</th><th>风险</th></tr>
                </thead>
                <tbody>
                    <tr class="grp-row g-done"><td colspan="5">✅ 已完成 · 2 项</td></tr>
                    <tr class="done"><td>1</td><td>系统</td><td>已完成事项</td><td>10.30</td><td class="risk risk-low">低</td></tr>
                    <tr class="grp-row"><td colspan="5">📦 计划窗口 · 7 项</td></tr>
                    <tr class="cust"><td>2</td><td>系统</td><td>对客变更</td><td>11.04</td><td class="risk risk-mid">中</td></tr>
                </tbody>
            </table>
            <div class="footnote">口径截至 2026-11-02，以最新状态为准。</div>
        </div>
    </div>
</section>
```

**表格规则**
- 长表必须用 `tr.grp-row` 分段（`g-done` 绿、`g-defer` 橙），段内行数 ≤ 8
- 风险列统一 `class="risk risk-high|risk-mh|risk-mid|risk-low"`
- 表下必须有 `.footnote` 说明数据口径与时间
- 超长表格（> 12 行）拆成"总览 + 展开"：总览页放分布芯片 + TOP 风险卡，展开页放明细

---

## 5. 指标行页

```html
<section class="slide" id="slide-metrics">
    <div class="content-page">
        <div class="content-header">
            <div class="content-number">03</div>
            <div>
                <div class="content-title">核心指标：四项指标全部达标，逾期率持续下降</div>
                <div class="content-subtitle">KEY METRICS</div>
            </div>
        </div>
        <div class="content-body">
            <div class="lead-bar"><b>结论：</b>四项指标均优于目标值。</div>
            <div class="stats-row">
                <div class="stat-card">
                    <div class="stat-value">2.1<small>%</small></div>
                    <div class="stat-label">逾期率（目标 ≤ 2.5%）</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">87<small>%</small></div>
                    <div class="stat-label">回收率</div>
                </div>
                <!-- 另两张；超标用 class="stat-card alert"（红）/ warn（橙） -->
            </div>
        </div>
    </div>
</section>
```

---

## 6. 因果链页（背景 → 应对 → 策略）

```html
<div class="chain-grid">
    <div class="chain-card">
        <div class="chain-tag">① 背景</div>
        <div class="chain-text">外部变化造成的影响，<b>关键判断</b></div>
    </div>
    <div class="chain-card">
        <div class="chain-tag">② 应对</div>
        <div class="chain-text">采取的双线措施，<b class="hl">无法完全避免的风险</b></div>
    </div>
    <div class="chain-card">
        <div class="chain-tag">③ 策略</div>
        <div class="chain-text">由此形成的分级策略</div>
    </div>
</div>
```

## 7. 阶段 / 周节奏页

```html
<div class="week-panel">
    <div class="week-panel-title">📅 推进节奏</div>
    <div class="week-strip">
        <div class="week-box"><h4>W1 · 11.01–11.07</h4><p>收口：全部变更 <b>11.05 前</b>投产</p></div>
        <div class="week-box"><h4>W2 · 11.08–11.15</h4><p>验证为主，<b>不加新变更</b></p></div>
        <div class="week-box freeze"><h4>W3 · 11.16–11.20 活动周</h4><p><b>零变更、零加量</b></p></div>
        <div class="week-box"><h4>W4 · 11.21–11.25</h4><p>维持管控，<b>11.25 解除</b></p></div>
    </div>
</div>
```

> 冻结/禁变更阶段必须用 `class="week-box freeze"`（红框红字），这是全场最需要被看见的信息。

## 8. 双卡对比页（扩量 / 资源）

```html
<div class="exp-grid">
    <div class="exp-card">
        <div class="exp-title">📞 外呼扩量 · 峰值对比</div>
        <div class="exp-nums">
            <div class="exp-num"><div class="v">30.6<small>万/日</small></div><div class="l">上月实际</div></div>
            <div class="exp-num"><div class="v">31.4<small>万/日</small></div><div class="l">本月测算</div></div>
            <div class="exp-num"><div class="v">+2.4<small>%</small></div><div class="l">差异（低风险模型 +2 实例已扩容）</div></div>
        </div>
        <div class="exp-desc">扩量方式与资源复用说明。</div>
        <div class="exp-sub lock">
            <div class="exp-sub-head">🔒 封网期间风险评估</div>
            <ul><li>风险判断与兜底</li></ul>
        </div>
    </div>
    <div class="exp-card"><!-- 第二张 --></div>
</div>
```

## 9. 折叠分组页（资源 / 明细深挖）

```html
<section class="fold-section">
    <div class="fold-title" role="button" tabindex="0">
        <span class="fold-arrow">▾</span>
        <span class="fold-name">🖥 应用侧</span>
        <span class="fold-sub">一句话结论</span>
        <span class="fold-tip">点击折叠/展开</span>
    </div>
    <div class="fold-body">
        <div class="res-block"><h4>块标题即结论</h4><ul><li>要点</li></ul></div>
    </div>
</section>
```

> 折叠只用于"现场可能被问到、但不主动讲"的支撑材料，主结论必须放在折叠区外。

## 10. TOP 风险卡页

```html
<div class="rel-head">⚠ TOP3 风险与应对</div>
<div class="risk-cards">
    <div class="rcard high">
        <div class="rcard-title">#11 · 高风险模型<span class="rk risk risk-high">风险：中</span></div>
        <ul>
            <li>风险描述</li>
            <li>措施：…</li>
            <li>回退：…</li>
            <li class="rc-sug">建议：…（需要领导决策时写在这里）</li>
        </ul>
    </div>
</div>
```

## 11. 时间轴页

```html
<div class="timeline">
    <div class="timeline-item">
        <div class="timeline-dot"></div>
        <div class="timeline-content"><h4>阶段一 · 时间</h4><p>目标与产出</p></div>
    </div>
</div>
```

## 12. 图表页

```html
<!-- ECharts -->
<div class="chart-container">
    <div class="chart-title">图表标题即结论</div>
    <div class="echart" data-option='{"xAxis":{"type":"category","data":["Q1","Q2"]},"yAxis":{"type":"value"},"series":[{"data":[100,200],"type":"bar"}]}' style="height:420px;"></div>
</div>

<!-- Mermaid：节点文本含 < > & 必须用 &quot; 包裹 -->
<div class="mermaid-diagram" data-code="flowchart LR
    A[&quot;开始&quot;] --> B[&quot;处理&quot;]
    B --> C[&quot;结束&quot;]"></div>
```

> 生成后必须运行 `python3 scripts/validate_mermaid.py index.html`。

## 13. 图片展示页

```html
<div class="image-showcase">
    <div class="image-item">
        <img src="image1.png" alt="说明文字">
        <div class="image-caption">说明文字（点击放大）</div>
    </div>
</div>
```

## 14. 收尾页

```html
<section class="slide" id="slide-end">
    <div class="qa-page">
        <div class="qa-decoration">
            <div class="qa-circle qa-circle-1"></div>
            <div class="qa-circle qa-circle-2"></div>
        </div>
        <div class="qa-icon">🛡️</div>
        <div class="close-lines">
            <div class="close-line">结论一 → <b>核心判断</b></div>
            <div class="close-line">结论二：<b>数字</b> 支撑</div>
            <div class="close-line">结论三：行动号召</div>
        </div>
        <!-- 需要领导拍板时： -->
        <div class="ask-card">
            <div class="ask-title">恳请协调与决策事项</div>
            <div class="ask-item"><span class="ask-ico">①</span><span><b>事项一</b><span class="ask-sub">补充说明与期望决策</span></span></div>
        </div>
        <div class="close-thanks">谢 谢 · 恳 请 指 正</div>
    </div>
</section>
```

> 收尾页复述 3 条以内核心结论（与封面胶囊呼应），不要引入新信息。
