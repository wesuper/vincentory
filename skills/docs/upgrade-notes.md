# Presentation Skills 升级改造记录

本文是面向维护者的设计决策与变更回溯文档，不属于任一 Skill 的运行时指令。安装 Skill 时仅选择对应技能目录即可；不要求 Agent 加载本文。当前执行规范以各 Skill 的 `SKILL.md`、契约、脚本和示例为准。

## 1. 改造背景与目标

以用户原始 `skills.zip`（V2）为起点，面向互联网 / IT 技术专家与技术管理者，强化技术方案、风险变更、预期管理、成果汇报、晋升答辩、架构评审、技术深度分享、团队宣导等场景。

核心目标不是生产形式完整的 PPT，而是帮助听众获得有证据支持的判断、理解必要边界、形成可迁移的认识，并作出合适的决策或行动。对内容架构 Skill 强化思考和论证，对 H5 Skill 强化认知表达和演讲支持。真实沟通效果与材料准备质量分开评价。

## 2. 改造过程与关键决策

| 阶段 | 主要改动 | 价值与取舍 |
|---|---|---|
| 原始基础（V2） | 四类内容入口、六阶段工作流、思考方法路由、主张与证据映射、逐页质量门禁、六文件交接、H5 四主题及演讲者引擎 | 保留成熟 SOP 和操作细节，尤其考虑较弱模型的执行可靠性 |
| 听众结果设计（V3） | 听众认知障碍、场景检查、逐页认知旅程、核心/深挖路线、结构化问答、预演与恢复路径；语义路由及演讲者主动跳转核心页 | 从作者表达转向听众任务；真实风险、关键限定和证据不因缩短路线而消失 |
| 沟通效果闭环（V4） | 洞察挖掘、持续注意力、三视角压力测试、五维效果计划、真实观察和会后复盘 | 不将模型自评冒充真实效果；保留独立的效果计划及观察校验 |
| 价值融合 | 以 V2 为主体吸收上述增强，而非整体替换 SOP；取消高级扩展对所有普通稿的强制绑定 | 普通任务执行成本可控，复杂任务仍有具体指导及严格门禁 |
| 首次发布目录整理 | 去掉历史叙事、废弃实现和多版本协议；统一语义命名，重组参考、资源和测试目录 | 尚未正式投入使用，无须维护历史兼容路径；保持当前实现干净、可验证 |
| 本次归档 | 将改造记录集中在 `docs/upgrade-notes.md` | 保留维护者的回溯依据，不把历史内容引入 Skill 的执行上下文 |

## 3. 当前能力与文件定位

| 能力 | 当前文件位置（相对于对应 Skill 根目录） |
|---|---|
| 内容任务分流、澄清、主线、写稿、评审、交接 | 内容侧 `SKILL.md` |
| 听众分析、方法路由、技术场景、结果设计 | 内容侧 `references/audience-playbook.md`、`method-router.md`、`technical-scenarios.md`、`outcome-design.md` |
| 逐页信息增量、证据及口述质量 | 内容侧 `references/slide-quality.md`、`quality-gates.md` |
| 认知旅程、核心路线、问答及预演 | 共享 `references/experience-contract.md`；内容侧 `references/rehearsal-playbook.md` |
| 洞察与五维效果计划、真实反馈复盘 | 内容侧 `references/effectiveness-design.md`、`effectiveness-review-template.md`；共享 `references/effectiveness-contract.md`、`scripts/evaluate_effectiveness.py` |
| 语义路由、视觉同频、恢复路径 | H5 侧 `SKILL.md`、`references/visual-routing.md`、`audience-synchrony.md`、`effectiveness-display.md` |
| 页面组件、主题和手工装配操作 | H5 侧 `references/page-templates.md`、`deck-design.md`、`theme-guide.md`、`render-workflow.md` |
| 六文件交接、内容解析与校验 | 两份 Skill 内各自携带的内容契约、`schemas/handoff.schema.json`、`scripts/content_contract.py` |
| 确定性 H5 渲染、静态及保真检查 | H5 侧 `scripts/prepare_render.py`、`render_reference.py`、`validate_deck.py`、`verify_render.py` |
| 可复用 H5 模板与主题 | H5 侧 `assets/` |
| 基础稿、复杂风险变更及效果计划 | 两份 Skill 的 `examples/` |
| 回归及共享文件一致性检查 | 两份 Skill 的 `tests/` |

### 当前协议与门禁

- 一套内容协议，不再维护 `contract_version` 字段及旧格式兼容分支。
- 基础正式稿必须通过内容、逐页质量、证据及封存检查；无需强制生成听众旅程或效果观察文件。缺失质量记录的输入只能走明确标注的安全预览路径，不得冒充正式交付。
- 听众旅程按需启用；已声明扩展必须完整校验，通过后才启用演讲者核心路线。
- 效果计划与观察独立记录。没有真实观察时为 `unknown`，排练与实际观察分离；不能自动证明沟通效果或把内部反馈嵌入观众 HTML。
- 当前语义标识为 `slide-review`、`audience-journey`、`communication-effectiveness`。稿件自身的 `revision` 和哈希仍保留，用于防止源内容、状态、交接及效果计划不一致；这些不是 Skill 发布版本号。

## 4. 首次发布整理的具体文件变更

| 整理对象 | 处理 |
|---|---|
| 根目录历史融合报告、验证记录 | 从执行包中移除；其重要决策、历史验证范围由本文归档 |
| 两个 Skill 内的重复 README | 合并为包根目录 README；后续回补了各自的精简维护说明，只保留安装、运行、边界和当前目录约定，不放版本历史 |
| H5 `templates/` | HTML/CSS/JS 与主题移入 `assets/`；页面模板、主题、引擎说明移入 `references/` |
| `legacy-rendering-guide.md` | 删除历史档案；有效的分步装配、投屏、主题、演讲与校验经验融入当前参考文件 |
| `scripts/generate.py` 与 `references/samples/` 中旧配置 | 删除已不属于当前工作流的生成器与示例 |
| 备注解析 | 移除旧 JS 对象字面量求值分支；统一严格 JSON，不执行输入备注代码 |
| `scripts/test_*.py` | 移入 `tests/`，提供 `tests/run.py`；历史版本测试命名改为语义名称 |
| 共享协议、schema、示例 | 同步统一格式和命名，重新生成相应示例哈希；保持两份 Skill 可独立安装 |
| 长参考与排查手册 | 保留或整合有效操作知识，删除不适用旧实现的指导；使用索引和按需引用 |

当前安装布局：根目录 `README.md`、`presentation-content-architect/`、`h5-report-generator/`、`docs/`。只有两个技能目录参与实际安装。

## 5. 验证记录及限制

以下是历次改造时已报告的验证结果，不是本次文档归档重新执行的测试。

| 阶段 | 内容侧自动化测试 | H5 侧自动化测试 | 其他检查 |
|---|---:|---:|---|
| 听众结果增强 | 54 项通过 | 26 项通过 | 模板同步、示例静态及保真；局部浏览器检查 |
| 沟通效果闭环 | 64 项通过 | 36 项通过 | 效果计划/观察字段及一致性 |
| 价值融合 | 67 项通过 | 41 项通过 | 基础与扩展稿、四主题静态及保真 |
| 首次发布目录整理 | 67 项通过 | 41 项通过 | 8 组端到端静态与保真检查通过；4 主题 78 组对比度检查无未达标；模板同步、共享契约、效果计划、文件引用检查通过 |

本次文档归档仅增加本文，验证压缩包完整性及原有文件逐字节一致性；未重新运行功能测试。

尚未完成：真实小模型/标准模型/强推理模型的同任务对照实验、真实用户反馈、完整浏览器及物理双屏演示。早期浏览器局部检查受导航环境限制，演讲者 iframe 和真实双窗口同步未得到完整验证。静态与单元测试通过不代表听众效果、真实投屏及复杂图表语义已验证。

当前测试命令：在各 Skill 根目录运行 `python3 tests/run.py`；H5 主题校验 `python3 scripts/theme_contrast.py .`，模板同步 `python3 scripts/sync-template.py .`。

## 6. 后续维护准则

- 稳定 SOP 留在 `SKILL.md`，专业知识按需加载；不在执行入口写改造历史。
- 对每项增删改判断必要性、实际价值、较弱模型执行成本、上下文成本和可验证性。
- 保留明确操作、示例与错误恢复，不用简洁代替可靠性，不以规则数量代替能力。
- 优先使用真实任务验证，结合错误记录决定后续改造；不同场景不强行汇总为一个效果分数。
- 维护决策与验证边界可继续集中记录在本文，不新增运行时历史分支。

设计参考：
- [Claude Skill 编写最佳实践](https://platform.claude.com/docs/zh-CN/agents-and-tools/agent-skills/best-practices)
- [Assertion–Evidence Approach](https://www.assertion-evidence.com/)
- [Applying the science of learning](https://pubmed.ncbi.nlm.nih.gov/19014238/)
- [Five Strategies for Optimizing Instructional Materials](https://pubmed.ncbi.nlm.nih.gov/33716467/)
- [Google SRE Workbook: Canarying Releases](https://sre.google/workbook/canarying-releases/)
- [Google Documentation Best Practices](https://google.github.io/styleguide/docguide/best_practices.html)
- [StaffEng: Promotion Packets](https://staffeng.com/guides/promo-packets/)

上述参考为设计依据，不是实际效果已经得到验证的证据。

---

## 附录：价值融合阶段原始审查记录

以下保留当时的审查文档原文，便于核对价值取舍。**其中关于旧稿兼容、协议版本字段、`templates/` 及历史档案的描述是当时的决策，已被本文第 3、4 节的首次发布整理替代，不作为当前执行规范。**

# Skill 融合审查记录

## 输入与原则

以用户的 V2 ZIP 为基线，吸收 V4 的高价值增强，而非以 V4 覆盖 V2。两个 Skill 名称、相互独立的安装方式、原有六文件内容协议、H5 四套主题、模板、交互、原有质量门禁全部保留。版本历史只用于维护审查；SKILL.md 是面向 Agent 的稳定 SOP。机器协议的版本字段仍保留以维持兼容性。

参考：[Claude Skill 编写最佳实践](https://platform.claude.com/docs/zh-CN/agents-and-tools/agent-skills/best-practices)。本次重点落实渐进式披露、任务自由度匹配、具体操作与异常处理、可执行校验、反馈闭环。多模型的真实任务评估仍需实际运行，不能用文本审查或单元测试代替。

## 价值取舍矩阵

| 能力 | 决策 | 必要性与价值 | 执行位置 |
|---|---|---|---|
| 原内容四类任务入口、六阶段工作流 | 保留 | 防止重复采访、过度澄清、遗漏交付物，较弱模型尤其需要明确顺序 | 内容 SKILL.md |
| 原思考方法及路由 | 保留 | 按问题选方法，避免套路化；不以框架数量替代思考 | method-router.md |
| 原场景手册（含市场、售前、客户） | 保留 | 保持通用性与原用户群，不因技术场景深化而删除 | audience-playbook.md |
| 原信息增量、证据、可见边界、时长、反方评审与状态机 | 保留为强制门禁 | 避免正确但空洞的演示及不合规正式交付 | slide-quality.md、quality-gates.md、脚本 |
| 原六文件与共享契约 | 保留 | 独立交付、跨 Skill 协作和旧稿兼容 | 两份契约、schema、解析器 |
| 原 H5 模板、四主题、交互快捷键、双屏与保真流程 | 保留 | 既有工程能力，不用泛化的新模板重写 | H5 templates/、scripts/ |
| 听众认知障碍、成功条件、非批准类目标 | 融入基础 SOP | 内容从听众判断而非作者叙事出发 | 内容步骤 1 |
| 洞察挖掘、反例、竞争解释 | 融入基础 SOP | 提升专业观点的可证伪性和真实增量 | 内容步骤 2 |
| 真实开场张力、逐段认知进展 | 融入基础 SOP | 不靠悬念套路制造注意力 | 内容步骤 3 |
| 三视角压力测试 | 强化原反方预演 | 复述、质疑、执行各有独立检查对象 | 内容步骤 5 |
| 技术细分场景及复杂预演 | 按需引用 | 给弱模型提供场景具体指引，又不占普通任务上下文 | technical-scenarios.md、rehearsal-playbook.md |
| 听众旅程、场景检查、核心路线 | 条件启用，声明后严格校验 | 高风险/复杂稿有价值；普通稿不必增加成本 | experience-contract.md |
| H5 同频、跨页语义一致、恢复路径 | 基础原则＋复杂稿深化 | 保持口播与视觉证据一致，不自动感知听众 | H5 SKILL.md、audience-synchrony.md |
| 效果计划与真实观察 | 独立按需启用 | 复盘和持续演讲值得记录；不可伪造现场数据 | effectiveness-contract.md、evaluate_effectiveness.py |
| 扩展强制绑定普通稿 | 取消 | 这是 V4 对原有 READY 路径的兼容性退化 | prepare_render.py、verify_render.py、文档 |
| 版本叙事 | 移出入口 | 不影响运行的历史信息属于维护文档 | 本审查记录 |

## 兼容行为

- 原 V2 基础正式稿经原门禁通过：content_quality=reviewed，experience_quality=not_applicable，保持 READY 进入渲染，不嵌入核心路线。
- 启用听众旅程扩展：完整记录、版本封存、逐页校验均通过才允许路线。声明扩展但未评审、无效或过期时，不能以基础路径绕过检查。
- 缺失质量记录或未就绪：标注安全预览；真实冲突、非法字段、blocked 按原策略处理。
- 效果观察缺失：unknown；合成示例、演练与实际观察分离。基础模式效果计划不要求听众旅程扩展，使用同目录六文件的基础封存和手册所述校验方式。
- Skill 入口使用稳定语义引用名。内部机器协议和兼容测试可含协议版本号。
- 长参考资料增加目录或使用原有导航；模板及旧详细档案仍可按需参考，冲突以当前 SOP 为准。

## 后续验证建议

用同一批材料分别测试较快/较小模型、标准模型和强推理模型，记录追问次数、任务完成率、错误类型、渲染质量及实际听众反馈。评估任务至少覆盖：短基础稿、风险变更、深度技术分享、晋升答辩、已有稿纯渲染、资料不足或敏感内容。不宣称已完成真实跨模型对照或物理投屏验证。
