# 装配、质量门禁及回传

## 依赖与装配
主流程 Python 3.10+ 标准库；浏览器测试可用实际 Chromium/浏览器或 Playwright（可选，先核对是否可用）。未安装时不声称浏览器测试。保持 skeleton 的进度、navigation、页码、交互引擎；样式和一个主题、脚本内联，数据 `JSON` 编码并转义 `<`；所有输入文字 HTML escape，禁止执行未审计的输入代码。手工高级页按实际组件模板分步写入，数据和来源保留。外部 ECharts/Mermaid 仅在允许联网且必要时引入，核心内容提供文本/表格或本地 SVG；单文件不等于完全离线或保密。默认基础渲染去掉 CDN，复杂图表/图像须额外处理。主题改动跑 theme_contrast.py。

## 静态与保真
- validate_deck.py：结构、ID、备注、页数 profile、主题、时间等；警告逐条解释。传统 standard 默认至少 5 页，adaptive 不硬性要求封面/目录/收尾，但有专用封面时仍检胶囊。两者内容页遵循三段式。
- verify_render.py：比对计划与 HTML 页序、逐页标题/Takeaway/Visible 文字、备注及源状态提示；只检查可静态提取的文字，不证明图表语义、视觉可见性、来源质量、无额外虚构文字。复杂图表文字可能不在 DOM，需保留可读兜底或人工批准并回到源更新。任何修改源后重做 prepare_render。
- 观察口径、符号、单位、数值、比较维度、来源提示、限制、未决项；有误返回源，不用设计掩盖。

## 演示质量门禁（与结构校验并行）
按 [presentation-quality](presentation-quality.md) 核对每页信息增量、视觉优先、精炼文字与口述、留白和导航，写入 `content_quality` 与 `page_reviews`；缺失、revise 或 not_tested 不能标正式验收。未评审稿先补审或预览；不能靠主题和占满画面掩盖缺内容。

## 浏览器验收（实际测量，不凭静态通过推定）
在 1366×768 和 1920×1080 打开每页，等待入场动画结束或开启 reduced motion；检查 scrollHeight/clientHeight、scrollWidth/clientWidth、边界截断、字号（原结构正文≥14px）、对比度、图表/图片、无控制遮挡、主题。截图抽检首、中、末及最密/图表页。键盘左右/首页末页、页码/进度、P 进入/退出、当前/下一页预览、备注同步、G 宫格跳转、T 计时、R 排练、草稿持久化、观众屏同步、黑白冻结、激光/圈选（按实际使用需求）逐项记录 pass/fail/not_tested/not_applicable；测试网络不可用时核心证据仍能看；外接投影物理链路只能现场确认。修改后重新测。任何关键项未测或失败不得标 presentation_ready。

## 披露与状态
HTML 备注、内部附录、图片、数据和前端代码都可被阅读；外部转发前检查是否允许随文件流转。不要把完整 sources.md、内部用户原话或隐私写入 HTML；Visible 只使用获准公开的引用及必要限定；Evidence 用于内部核查。草案在观众页明显标记「预览｜内容待确认」。敏感或权限未定时停止输出该内容并报告缺口。render-review.json 示例：

```json
{"source_readiness":"ready","source_sha256":"实际哈希","theme":"light-gradient","profile":"adaptive","checks":{"static":"pass","fidelity":"pass","visual_1366":"not_tested","visual_1920":"not_tested","presenter":"not_tested","offline":"not_tested","disclosure":"not_tested"},"issues":["未运行浏览器"],"status":"preview"}
```

如有复杂功能单列检查项；有真实缺陷要附 slide_id / issue / available_space / proposed_revision / changes_semantics。所有关键项和逐页质量评审通过、content_quality=reviewed、内容 ready、披露满足才 presentation_ready；真实听众反馈与物理设备另记。不能将准备完成当作用户批准公开发布。


## 同频与路线的附加验收
启用听众旅程扩展时记录 `experience_quality`；`checks.short_route`（pass/fail/not_tested/not_applicable）、`checks.synchrony_review` 及实际依据。用实际浏览器进入 P，检查核心/深挖标签和预算、明确点击下一核心页的行为、末页、普通导航、宫格、双屏、预览无路由、无数据泄露；已启用扩展不得以 content_quality 代替 experience_quality；未启用扩展且基础门禁通过的稿正常验收，短路线记 not_applicable。人工高级装配须嵌入同样的最小路线 JSON；verify_render.py 检查该 JSON 与计划一致。真实反馈独立记录，不能填入机器通过字段。

## 手工高级页装配（复杂图表、架构或特定组件）
1. 明确主讲时间、页序、每页任务与主题。仅给会议时长时，可将30分钟会议按约25分钟主讲、60分钟会议按约50分钟主讲初步规划；页数随内容复杂度调整，用户明确时长/页数优先。standard 模式有封面、目录、至少两页内容和收尾；adaptive 按源稿，不补空页。主题按用户指定，否则 light-gradient。
2. 读取 skeleton、结构 CSS、选定主题 CSS、交互 JS 及 [页面模板](page-templates.md)。用脚本按三个唯一槽位完整内联，结构在皮肤之前；不要一次手贴整份长 HTML 或改写交互引擎。保留进度条、导航、页码和备注块。内容占位符只出现一次；最后无残留。
3. 推荐先运行 render_reference.py，再按页替换复杂证据区。手工装配时每批1–2页，检查结构和源内容后继续。普通内容页保持 `.content-page > .content-header + .content-body`，`.lead-bar` 为正文第一个子元素；内容页从01连续编号，专用封面/目录/收尾不计入。所有 slide 的 id 和 data-slide-id 各自唯一，按 DOM 顺序翻页，不额外维护页序数组。standard 的专用封面有2–3条结论胶囊，目录每章一句结论及2–3条要点，收尾不超过3条核心判断；adaptive 不强行制造这些角色。
4. 每页（含过渡、附录）对应一条合法 JSON 备注，id 与 data-slide-id 精确匹配；title/purpose/talk/transition/minutes 等按契约，禁止执行输入代码。把事实口径、案例解释与判断依据写入口述展开，关键限定仍留在 Visible。
5. 重跑静态、保真及浏览器检查。重点实测观众屏握手、预览比例、右侧备注切换、草稿保存、演前检查、排练实际/计划对照、标注同步和非默认主题。若采用复杂图表，必须检查其实际渲染及数据标签；不靠静态脚本证明图表可用。

## 图表与主题专项
Mermaid 节点或子图标题含特殊字符时用引号或实体；不用 graph/flowchart 等保留字作节点 ID。使用时运行 validate_mermaid.py（若 --fix 自动修正，人工复核关系及标签再重新验收）。主题使用语义令牌，不硬编码色值或字体；改主题后运行 theme_contrast.py，确保皮肤令牌齐全。样式/引擎变更后用 sync-template.py 同步完整示例。
