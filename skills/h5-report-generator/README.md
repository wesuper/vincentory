# H5 Report Generator

独立 Skill，入口 `SKILL.md`。根据既有内容生成 16:9、可离线演示的单文件网页幻灯片：先预检内容质量，再按信息关系选择图表、流程、对照矩阵或精炼文字，最后完成装配、保真与浏览器验收。备注承载口述细节，关键证据和边界保留在观众页。

## 输入与产物

- **结构化联用**：读取 `presentation.md` + `handoff.json`，同目录存在时自动读取 `working-state.json` 等六文件；不重新采访、不重构已确定主线。契约 1.1 新稿额外带逐页 `slide_quality`。
- **直接生成**：成熟稿按原顺序、事实、措辞与限制映射；允许时做轻量整理和补备注，不做无授权的新研究。
- **产物**：`index.html`（单文件）、`render-input.json`（内部中间件，不随意外发）、`render-review.json`（源状态/hash、各项检查、未测项）。

## 运行

在 Skill 根目录运行：

```bash
python3 scripts/prepare_render.py examples/presentation.md --out render-input.json
python3 scripts/render_reference.py render-input.json index.html
python3 scripts/validate_deck.py index.html --profile adaptive --target-minutes 5 --theme dune
python3 scripts/verify_render.py render-input.json index.html --source examples/presentation.md
python3 -m unittest discover -s scripts -p 'test_pipeline.py'
```

上面的时长、主题与 profile 只对应当前示例（三页、5 分钟、`dune`），实际按稿件设置。需要 Mermaid 时再跑 `validate_mermaid.py`。

## 演示

用浏览器打开生成的 `index.html`：方向键 / `PageDown` / 空格翻页，`Home` / `End` 跳首末页，按 `P`（或右下按钮）进入演讲者视图——左侧当前页与下一页预览，右侧备注、计时与现场草稿，观众屏自动另开窗口并双向同步。

| 键 | 作用 | 键 | 作用 |
|---|---|---|---|
| `→` `PageDown` `Space` | 下一页 | `←` `PageUp` | 上一页 |
| `Home` / `End` | 首页 / 末页 | `P` / `Esc` | 进出演讲者视图 |
| `G` | 宫格选页 | `?` | 快捷键表 |
| `B` / `W` | 观众屏黑屏 / 白屏 | `F` | 冻结观众屏 |
| `T` | 计时开始/暂停 | `R` | 开始/结束排练记录 |
| `L` / `C` / `X` | 激光 / 圈选 / 清除 | `+` / `-` | 备注字号 |

`B` / `W` / `F` / `L` / `C` / `X` / `T` / `R` 及备注字号只在演讲者视图内生效；观众普通视图里 `F` 是切换全屏，其余为翻页键。

主题共四套，用 `--theme` 或 `handoff.adapter.theme` 指定：`light-gradient`（默认，清爽现代）、`kraft-paper`（牛皮纸杂志感）、`dune`（沙丘克制）、`ink-classic`（墨水经典印刷感）。主题只由 CSS 变量实现，页面内不写死色值或字体。

## 边界

- **内容不由本 Skill 负责**：发现空洞、重复、缺证据或不适配视觉的页面，回传 `slide_id / issue / available_space / proposed_revision`，由内容源修订后再渲染；不擅自补事实、改结论或删限制。
- **参考渲染器只是基线**：支持显式流程链、分组卡片、比较表及原有封面/目录/收尾；复杂数据图、架构图与条件分支仍需 Agent 按真实内容完成。默认不引入外网 CDN，核心证据要有本地文本/表格/SVG 兜底。
- **未逐页评审的旧稿只作安全预览**：源状态非 `ready` 或 `content_quality` 未达 `reviewed` 时，观众页标注「预览｜内容待确认」，不得标 `presentation_ready`。正式交付还需语义、视觉、功能及披露验收，见 `references/presentation-quality.md`。
- **静态通过不等于可用**：脚本不证明说服力、图表语义、真实听众认可，也不证明物理投屏链路；浏览器双尺寸实测与现场设备需另行确认，未测项记 `not_tested`。
- **单文件不等于保密**：HTML 内的备注、隐藏页与 JS 数据也可被文件接收者查看，敏感内容先确认披露边界再写入。

## 维护

`examples/` 是独立安装所需的完整输入副本，内容真源在 `presentation-content-architect/examples/`（合成的售前知识助手试点，三页、五分钟）。当前没有自动同步脚本：修改真源后手动复制，`presentation-content-architect/scripts/test_contract_parity.py` 会在两份 Skill 同时存在时逐字节比对共享契约、schema 与示例，漂移即失败；单独安装时该检查跳过。不要只改其中一份，也不要把示例中的业务结论当真实数据引用。
