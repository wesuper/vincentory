# H5 Report Generator

独立 Skill，入口 `SKILL.md`。把现成内容预检后转换成 16:9、可离线演示的单文件 H5：按信息关系选择图表、流程、对照矩阵或精炼文字，保留演讲备注与必要限制，再做装配、保真、视觉与浏览器验收。

## 输入与产物

- **结构化联用**：读取 `presentation.md` + `handoff.json`，同目录存在时自动读取 `working-state.json` 等六文件；不重新采访、不重构已确定主线。
- **直接生成**：成熟稿按原顺序、事实、措辞与限制映射；允许时做轻量整理和补备注，不做无授权的新研究。
- **局部改版**：保留内容源与 ID；只改主题/显示要求时无需修改内容 revision，内容改动必须回到源文件并重新封存。
- **产物**：`index.html`（单文件）、`render-input.json`（内部中间件，不随意外发）、`render-review.json`（源状态/hash、各项检查、未测项）。

## 使用方式

在 Skill 根目录运行：

```bash
python3 scripts/prepare_render.py examples/presentation.md --out render-input.json
python3 scripts/render_reference.py render-input.json index.html
python3 scripts/validate_deck.py index.html --profile adaptive --target-minutes 5 --theme light-gradient
python3 scripts/verify_render.py render-input.json index.html --source examples/presentation.md
python3 tests/run.py
```

上面的时长、主题与 profile 只对应当前示例，实际按稿件设置。使用 Mermaid 时再运行 `scripts/validate_mermaid.py`。输入备注按严格 JSON 解析，不执行内嵌代码；HTML 内的备注、隐藏页和 JS 数据也能被文件接收者查看，敏感内容先确认披露边界。

## 演示操作

用浏览器打开生成的 `index.html`：方向键 / `PageDown` / 空格翻页，`Home` / `End` 跳首末页，按 `P`（或右下按钮）进入演讲者视图；左侧是当前页和下一页预览，右侧是备注、计时与现场草稿。

| 键 | 作用 | 键 | 作用 |
|---|---|---|---|
| `→` `PageDown` `Space` | 下一页 | `←` `PageUp` | 上一页 |
| `Home` / `End` | 首页 / 末页 | `P` / `Esc` | 进出演讲者视图 |
| `G` | 宫格选页 | `?` | 快捷键表 |
| `B` / `W` | 观众屏黑屏 / 白屏 | `F` | 冻结观众屏 |
| `T` | 计时开始/暂停 | `R` | 开始/结束排练记录 |
| `L` / `C` / `X` | 激光 / 圈选 / 清除 | `+` / `-` | 备注字号 |

`B` / `W` / `F` / `L` / `C` / `X` / `T` / `R` 及备注字号只在演讲者视图内生效；观众普通视图里 `F` 是切换全屏，其余为翻页键。右下导航是低存在感工具，不遮挡内容；键盘焦点和触屏仍可操作。

## 质量门禁

- 基础稿按内容、逐页质量、证据和封存检查验收；未逐页评审的旧稿只作标注清楚的安全预览，不冒充正式交付。
- 声明听众旅程扩展后必须完整校验，才启用演讲者核心路线；缺扩展不自动补造，不擅自跳页。
- 效果计划和真实观察是独立内部材料，不进入 HTML，不作为普通稿验收前提；没有真实观察时为 `unknown`。
- 静态检查通过不等于浏览器可用、图表语义正确或听众认可；两尺寸翻页、演讲者视图、计时、离线与双屏需另行核对，未测项记 `not_tested`。

## 维护

`assets/` 保存可复用 HTML/CSS/JS 模板与四套主题（`light-gradient` 默认、`kraft-paper`、`dune`、`ink-classic`）；主题只由 CSS 变量实现。`references/page-templates.md` 说明组件、备注契约与快捷键，`references/theme-guide.md` 说明主题扩展。修改主题后运行 `python3 scripts/theme_contrast.py .`，修改模板或引擎后运行 `python3 scripts/sync-template.py .`。`tests/` 保存独立回归测试，行为评估见 `references/evaluation.md`。

`examples/` 是合成、可运行的输入与输出结构示例，内容真源在 `presentation-content-architect/examples/`；不要把示例业务结论当真实数据引用。
