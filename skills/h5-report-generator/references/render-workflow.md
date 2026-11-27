# 装配、质量门禁及回传

## 依赖与装配
主流程 Python 3.9+ 标准库；浏览器测试可用实际 Chromium/浏览器或 Playwright（可选，先核对是否可用）。未安装时不声称浏览器测试。保持 skeleton 的进度、navigation、页码、交互引擎；样式和一个主题、脚本内联，数据 `JSON` 编码并转义 `<`；所有输入文字 HTML escape，禁止执行未审计的输入代码。手工高级页按实际组件模板分步写入，数据和来源保留。外部 ECharts/Mermaid 仅在允许联网且必要时引入，核心内容提供文本/表格或本地 SVG；单文件不等于完全离线或保密。默认基础渲染去掉 CDN，复杂图表/图像须额外处理。主题改动跑 theme_contrast.py。

## 静态与保真
- validate_deck.py：结构、ID、备注、页数 profile、主题、时间等；警告逐条解释。传统 standard 默认至少 5 页，adaptive 不硬性要求封面/目录/收尾，但有专用封面时仍检胶囊。两者内容页遵循三段式。
- verify_render.py：比对计划与 HTML 页序、逐页标题/Takeaway/Visible 文字、备注及源状态提示；只检查可静态提取的文字，不证明图表语义、视觉可见性、来源质量、无额外虚构文字。复杂图表文字可能不在 DOM，需保留可读兜底或人工批准并回到源更新。任何修改源后重做 prepare_render。
- 观察口径、符号、单位、数值、比较维度、来源提示、限制、未决项；有误返回源，不用设计掩盖。

## 演示质量门禁（与结构校验并行）
按 [presentation-quality](presentation-quality.md) 核对每页信息增量、视觉优先、精炼文字与口述、留白和导航，写入 `content_quality` 与 `page_reviews`；缺失、revise 或 not_tested 不能标正式验收。旧稿先补审或预览；不能靠主题和占满画面掩盖缺内容。

## 浏览器验收（实际测量，不凭静态通过推定）
在 1366×768 和 1920×1080 打开每页，等待入场动画结束或开启 reduced motion；检查 scrollHeight/clientHeight、scrollWidth/clientWidth、边界截断、字号（原结构正文≥14px）、对比度、图表/图片、无控制遮挡、主题。截图抽检首、中、末及最密/图表页。键盘左右/首页末页、页码/进度、P 进入/退出、当前/下一页预览、备注同步、G 宫格跳转、T 计时、R 排练、草稿持久化、观众屏同步、黑白冻结、激光/圈选（按实际使用需求）逐项记录 pass/fail/not_tested/not_applicable；测试网络不可用时核心证据仍能看；外接投影物理链路只能现场确认。修改后重新测。任何关键项未测或失败不得标 presentation_ready。

## 披露与状态
HTML 备注、内部附录、图片、数据和前端代码都可被阅读；外部转发前检查是否允许随文件流转。不要把完整 sources.md、内部用户原话或隐私写入 HTML；Visible 只使用获准公开的引用及必要限定；Evidence 用于内部核查。草案在观众页明显标记「预览｜内容待确认」。敏感或权限未定时停止输出该内容并报告缺口。render-review.json 示例：

```json
{"source_readiness":"ready","source_sha256":"实际哈希","theme":"light-gradient","profile":"adaptive","checks":{"static":"pass","fidelity":"pass","visual_1366":"not_tested","visual_1920":"not_tested","presenter":"not_tested","offline":"not_tested","disclosure":"not_tested"},"issues":["未运行浏览器"],"status":"preview"}
```

如有复杂功能单列检查项；有真实缺陷要附 slide_id / issue / available_space / proposed_revision / changes_semantics。所有关键项和逐页质量评审通过、content_quality=reviewed、内容 ready、披露满足才 presentation_ready；真实听众反馈与物理设备另记。不能将准备完成当作用户批准公开发布。
