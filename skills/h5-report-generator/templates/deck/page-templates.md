# Deck Theme — 页面类型 HTML 结构 (v6)

> 适用于 `templates/deck/` 主题系统（`light-gradient` 默认 / `kraft-paper` / `dune` / `ink-classic`）。本文件是**结构契约**：照抄骨架、替换文字即可。

## 通用约定

- 每页是一个 `<section class="slide" id="slide-<页面名>" data-slide-id="<备注 id>">` 元素，`id` 与 `data-slide-id` 都全局唯一
- **`data-slide-id` 是演讲者备注的绑定键**：必须每页都有（含封面/目录/收尾），且与 `window.SPEAKER_NOTES` 中对应条目的 `id` 完全一致。缺 `data-slide-id` 时脚本会退回用 `id` 去掉 `slide-` 前缀，但不要依赖这个兜底
- **页面顺序 = DOM 顺序**，无需维护 `slideOrder` 数组（脚本按 DOM 顺序生成页码与进度）
- 第一页（封面）带 `class="slide active"`，其余只写 `class="slide"`
- 追加位置：`<div class="presentation">` 内部、`{{PAGES}}` 占位处
- 主题由 `<html data-theme="…">` 与内联的皮肤文件 `themes/<id>.css` 共同决定（两者必须一致），**页面结构不随主题变化**
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

## 0. 演讲者备注（`SPEAKER_NOTES`）契约

演讲者视图（`P` 键）不读页面正文，只读 `window.SPEAKER_NOTES`。**每页必须有一条**，`id` 与页面的 `data-slide-id` 一一对应。

```js
window.SPEAKER_NOTES = [
  {
    id: 'metrics',                    // 必填：= section 的 data-slide-id
    title: '风险指标：四项全部达标',    // 必填：备注栏顶部标题，可不同于页面标题
    section: '风险指标',                // 选填：所属章节
    minutes: 4,                        // 选填：本页计划时长（分钟）
    purpose: '把"达标"拆成四个可核对的指标',   // 必填：这一页存在的理由
    talk: [                            // 必填：2–4 条讲述要点
      '逾期率 2.1%，低于 2.5% 目标，连续三个季度下降',
      '投诉率 0.3%，离预警线只剩 0.05 个百分点，这是真正的风险点'
    ],
    transition: '达标不等于可以松手，所以有了 Q4 的三步计划',  // 必填：转场句
    advance: '讲完投诉率预警后停一下，再翻页',   // 选填：翻页时机
    cue: '投诉率这里放慢，这是全场最需要被记住的风险',  // 选填：舞台提示
    delivery: '语速放慢，数字重读',              // 选填：表达方式
    interaction: '问一句：投诉率预警线是多少？',   // 选填：互动
    fallback: '被追问口径时翻回上一页的表格',      // 选填：备用方案
    pronunciation: '逾期率（yú qī lǜ）'          // 选填：生僻读音
  }
];
```

### 写备注的规矩：补页面，不抄页面

演讲者视图右侧是窄栏，**照抄页面要点等于让讲者重读一遍观众已经看见的字**。备注只写观众看不到的三种东西：

| 该写 | 不该写 |
|------|--------|
| **背景**——这个数字从哪来、和前几页什么关系 | 页码上已有的 `lead-bar` 原文 |
| **例子**——一个具体客户/场景，让抽象数字落地 | 卡片里已经列出的三条 bullet |
| **判断**——讲者自己的取舍、担心、需要领导拍板的点 | 表格里的明细行 |
| **转场句**——为什么下一页是下一页 | "这一页讲风险指标"这类目录式复述 |

`talk` 每条 ≤ 40 字，2–4 条；超过 4 条说明这页该拆。`purpose` 一句话，回答"听众听完这页应该改变什么判断"。

---

## 1. 封面页

```html
<section class="slide active" id="slide-cover" data-slide-id="cover">
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
        <div class="cover-hint">← / → 翻页 · F 全屏 · P 演讲者视图</div>
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
<section class="slide" id="slide-toc" data-slide-id="toc">
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
<section class="slide" id="slide-cards" data-slide-id="cards">
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
<section class="slide" id="slide-table" data-slide-id="table">
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
<section class="slide" id="slide-metrics" data-slide-id="metrics">
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
<section class="slide" id="slide-end" data-slide-id="closing">
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

---

## 15. 主题切换

主题由两处共同决定，且必须一致：`<html data-theme="…">` 的属性值，以及内联进 `THEME_CSS` 槽位的那一个皮肤文件。页面 HTML 一行都不用动：

```html
<html lang="zh-CN" data-theme="light-gradient">   <!-- 默认：浅蓝，内联 themes/light-gradient.css -->
<html lang="zh-CN" data-theme="kraft-paper">      <!-- 牛皮纸：暖棕 + 宋体 -->
<html lang="zh-CN" data-theme="dune">             <!-- 沙丘：沙色 + 炭黑 -->
<html lang="zh-CN" data-theme="ink-classic">      <!-- 墨水经典：纸白 + 近黑 + 衬线 -->
```

> **只内联一个皮肤**。四个都塞进去会互相覆盖，且文件平白多出三份无用样式。`data-theme` 填了 A 却内联了 B 的皮肤，页面会变成「结构和 B 的皮肤、但所有 `[data-theme="A"]` 选择器全部落空」——症状是整页掉回浏览器默认样式。

| 主题 | 主色 | 背景 | 气质 | 适用 |
|------|------|------|------|------|
| `light-gradient` | `#0066cc` 蓝 | 浅蓝渐变 | 清爽、企业、默认 | 技术/产品/季度汇报（默认首选） |
| `kraft-paper` | `#9b5a2e` 棕 | 牛皮纸 `#eedfc7` | 手作、杂志、沉稳 | 复盘、总结、内部分享 |
| `dune` | `#8f7650` 沙 | 沙色 `#f0e6d2` | 克制、高级、安静 | 战略、年度、对外汇报 |
| `ink-classic` | `#111` 墨 | 纸白 `#f1efea` | 极简、印刷、锐利 | 观点表达、评审、设计稿 |

> 三个杂志主题的显示字体切为衬线（`Songti SC` / `Noto Serif SC` / `Playfair Display`），换主题时**不要**再手写 `font-family`，否则会破坏主题一致性。颜色一律走语义变量（`--accent` / `--ink` / `--surface` / `--tint` …），禁止在页面里写死十六进制色值——写死就会在换主题时变成不协调的色块。

---

## 16. 演讲者视图（`P` 键）

这不是页面结构，是交付时必须验证的演示能力。打开 `index.html` 按 `P`（或点右下 `P` 按钮）：

- **左侧**：当前页 16:9 显示 + 下一页小窗，均为真实缩放的 iframe 预览（不重新加载页面）
- **右侧**：`SPEAKER_NOTES` 渲染成窄栏提示——本页目的、讲述要点、舞台提示、表达、翻页时机、转场句
- **底部**：总计时 + 本页计时 + 计划剩余 + 页码
- **观众屏**：进入演讲者视图时自动另开一个 `?mode=audience` 窗口供投屏；两窗页码、黑屏状态双向同步

键盘即可完成全部操作，讲者不需要碰鼠标：

| 键 | 作用 | 键 | 作用 |
|----|------|----|------|
| `→` `PageDown` `Space` | 下一页 | `←` `PageUp` | 上一页 |
| `Home` / `End` | 首页 / 末页 | `P` / `Esc` | 退出演讲者视图 |
| `B` | 观众屏黑屏（可再按恢复） | `W` | 观众屏白屏 |
| `F` | 冻结观众屏在当前页 | `R` | 暂停 / 继续计时 |
| `L` | 激光笔（跟随触控板） | `C` | 圈选批注 |
| `X` | 清除批注 | `+` / `-` | 备注字号增减 |

> `F` 是上下文相关的：**演示模式下是全屏**，**演讲者视图里是冻结观众屏**。`Space` 与 `→` 等价（翻页），演讲者视图里的 `Esc` 等价于 `P`（退出），都不会误触浏览器全屏。

> 演讲者视图**固定深色**（右侧备注栏在全黑房间里不刺眼），与页面主题无关——所以不要在 `.presenter` 作用域内引用浅色主题变量。
