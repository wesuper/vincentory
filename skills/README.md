# Presentation Skills

两个独立 Skill，按任务选择，也可通过统一内容协议联用。本目录是 vincentory 所有 Agent Skill 的唯一来源：**一个子目录一个 Skill**，可单独安装、单独测试，必要时通过显式契约组合。本文件说明目录约定、增删改流程，以及当前两个演示类 Skill 如何单独使用或组合成一条从内容到投屏的工作流；每个 Skill 的触发条件、分步步骤和限制仍以它自己的 `SKILL.md` 为准。

## 安装

将需要的 Skill 目录放入 Agent 使用的 skills 目录；名称与 `SKILL.md` frontmatter 一致。两个目录均可独立使用。联用时通过六文件内容交接，不跨目录调用内部实现。

## 目录约定

- 每个 Skill 独占一个 kebab-case 目录，直接位于 `skills/` 下，不设分类层。
- 目录名必须等于 `SKILL.md` frontmatter 中的 `name`。
- 只有 `skills/<skill-name>/SKILL.md` 会被自动发现；嵌套目录里的 Skill 不会被加载。
- `skills/` 下的内容默认随插件发布。未完成或实验中的 Skill 放在仓库外或分支上，不在此目录占位。
- 本 README 不是 Skill，不参与发现。

> 不设分类层的原因：Claude Code 只在一层深度自动发现 Skill；带分类的路径必须逐条写入清单，漏写不会报错，Skill 只是静默缺席。

## Skill 目录结构

```text
skills/<skill-name>/
  SKILL.md        # 必需：入口、边界、分流、步骤、完成门禁
  README.md       # 可选：维护者视角的说明与运行命令
  references/     # 可选：按需加载的方法、手册、契约和设计指南
  scripts/        # 可选：确定性解析、封存、校验和生成脚本
  schemas/        # 可选：机器可读的内容交接结构
  assets/         # 可选：H5 HTML/CSS/JS 模板与主题资源
  examples/       # 可选：合成、可运行的输入及输出结构示例
  tests/          # 可选：独立自动化测试及运行入口
```

维护约定：

- `SKILL.md` 保持精简：入口、边界、分流、分步流程、完成门禁。长方法、场景手册、协议细节放 `references/`，由正文按需引用。
- 脚本必须确定性、可重复、可离线运行，优先使用标准库；校验器应能独立执行，不依赖 Agent 的临场判断。
- 测试从各自 Skill 根目录运行 `python3 tests/run.py`。同时安装时，内容侧测试检查两份共享契约、schema、解析器与示例完全一致；独立安装时跳过跨目录检查。H5 改动主题后运行 `python3 scripts/theme_contrast.py .`，改动样式或引擎后运行 `python3 scripts/sync-template.py .`。
- `examples/` 是校验与回归测试的真实输入，保持最小可用；不放宣传材料、真实客户数据或敏感信息。
- `schemas/` 与 `references/` 中的契约是对外接口。改字段时同步更新 schema、解析器、测试和 `CHANGELOG.md`。
- 不写入密钥、令牌、邮箱或环境特定值。
- 产物级别要与 Skill 的职责匹配：内容型 Skill 只产出文本/结构化数据，渲染型 Skill 才负责 HTML/CSS，避免职责重叠。

## Frontmatter 契约

```yaml
---
name: <与目录名一致>
description: <何时触发 + 能做什么>
---
```

- `description` 写触发条件与能力边界，不复述执行步骤——复述步骤会让 Agent 照描述行事而不读正文。
- 显式声明调用方式：仅在需要用户显式触发时设置 `disable-model-invocation: true`；不设置表示允许模型自动调用，此时必须保证误触发也不会产生不可逆副作用。
- 触发范围与其他 Skill 重叠时，在 `description` 中写清分工，而不是在正文里反复防御。

## 独立与组合

- 每个 Skill 必须能单独安装并完成其范围内的全部工作，不得假设其他 Skill 一定存在。
- 组合只通过显式产物与契约进行（文件格式、JSON Schema、交接状态），不跨 Skill 引用内部实现文件。
- 参与组合的双方都要写明：输入产物、产物缺失时的降级行为、冲突的回传格式。
- 共享的契约或解析器若在各 Skill 内各留一份，必须逐字节一致，并由测试或校验脚本守门；否则只保留单一来源。
- 上游产物缺失或未就绪时，下游降级为明确标注的预览或草案，不静默补全。

## 如何选用

- 任务能被单个 Skill 覆盖：直接使用，不强行串联。
- 任务跨多个产物阶段：按材料当前状态确定入口，从最接近现状的一环开始，而不是从链路起点重做。
- 只需要其中一环：只安装那一个；组合链路在任一环都能停。
- 分工不清：先读各 `SKILL.md` 的 `description` 与「边界」段，触发条件比功能列表更能区分；能独立完成的范围见下文「双 Skill 演示工作流」。

## 新增 / 修改 / 删除 Skill

新增或修改：

1. 在 `skills/<skill-name>/SKILL.md` 写好 frontmatter 与正文，确认 `name` 与目录名一致。
2. 把该路径加入 `.claude-plugin/plugin.json` 的 `skills` 数组。
3. 在根 `README.md` 的发布列表加一行。
4. 更新本文件的「当前收录」。
5. 需要发布时，同步 `.claude-plugin/plugin.json`、`package.json` 的版本并在 `CHANGELOG.md` 增加条目。
6. 运行下方校验。

删除或重命名：

- 从 `plugin.json`、根 `README.md`、本索引三处同时移除；重命名视为删除加新增。
- 删除前确认没有其他 Skill 的契约、示例或测试引用它。
- 不保留空目录；未发布的半成品不要放进 `skills/`。

## 当前收录

| Skill | 何时选它 | 主要产物 |
|---|---|---|
| [presentation-content-architect](presentation-content-architect/SKILL.md) | 内容尚未成形：需要澄清听众目标、建立主张与证据、逐页写稿和反方预演 | Markdown/JSON 内容真源与交接文件 |
| [h5-report-generator](h5-report-generator/SKILL.md) | 内容已可用：需要生成或改版可投屏的 H5 网页幻灯片、换主题、补演讲者视图 | 单文件 HTML 与渲染记录 |

> 触发词、分步流程与限制的权威版本在各 Skill 的 `SKILL.md`；上表只做一句定位。下面的协作主线描述两者组合时的共同约定，单 Skill 使用时以其入口为准。

## 双 Skill 演示工作流

两个 Skill 合起来覆盖「内容成形 → 可投屏演示」：目标不是把材料装进漂亮模板，而是让听众理解、核查、记住关键判断，并推进合适的下一步。观众页图表优先、文字精炼，讲者备注展开推理与案例。

| 维度 | presentation-content-architect | h5-report-generator |
|---|---|---|
| 输入 | 零散想法、提纲、访谈纪要、参考材料，或需要重构的旧稿 | 成熟稿、`presentation.md` + `handoff.json`，或内容 Skill 的六文件交付 |
| 负责 | 听众目标、澄清、主张与证据、主线、逐页信息增量与口述、反方预演 | 预检、视觉关系路由、模板装配、文字保真、演讲者视图与验收 |
| 适合 | 领导决策、售前、技术分享、晋升答辩、补论证或重排演示逻辑 | 已有内容、H5 投屏、换主题、局部改版 |
| 产物 | `presentation.md`、`outline.md`、`claim-map.json`、`sources.md`、`handoff.json`、`working-state.json` | `index.html`、`render-input.json`、`render-review.json` |

两者通过统一的内容协议联用，也可各自独立安装；共享的契约、schema 与解析器各带一份，仓库内由 `tests/test_contract_parity.py` 守住逐字节一致。

### 推荐的三种使用方式

以下提示词可直接复制，按实际听众、场景和材料调整。

**场景 A：只有想法，需要深度共创。单独使用内容架构师。**

```text
使用 presentation-content-architect。

我准备进行一次面向公司领导的技术战略汇报，但目前只有一些零散想法。

请先从听众的评价标准和决策需求反推汇报目标，通过苏格拉底式提问与我逐步澄清。不要急于生成 PPT，也不要为了使用方法论而使用方法论。

最终形成经得起质疑的论证结构、逐页内容、演讲备注、证据台账和潜在答辩问题。
```

**场景 B：内容已经成熟，只需要视觉化。单独使用 H5 生成器。**

```text
使用 h5-report-generator，将我提供的现有汇报材料转换为可投屏的 H5 演示文稿。

不要重新进行内容策划，也不要擅自修改核心观点、数据和结论。根据每页的信息任务选择合适的视觉表达方式，保留演讲者备注及必要的证据限定。

完成后执行内容保真和页面可用性校验。
```

**场景 C：从零散想法到最终演示。组合使用两份 Skill。**

```text
组合使用 presentation-content-architect 和 h5-report-generator。

第一阶段：根据汇报场景、听众、预期结果和现有材料，协助我完成问题澄清、论证设计、内容生成及反方预演。

第二阶段：内容达到交接条件后，通过共享内容契约交给 H5 生成器，根据内容语义选择页面模板，生成最终可演示的 H5 文件。

两阶段共享同一内容真源，不重复提问，不擅自修改已经确认的事实。如果渲染过程中发现内容问题，返回内容阶段修订，再重新验证。
```

### 主线与质量标准

`听众问题 → 主张与证据 → 页面任务 → 视觉意图/精炼正文/口播 → 逐页质量评审 → 交接 → 渲染 → 保真、投屏与披露验收`

- 每页先问：删去本页，听众会失去什么具体判断依据？空话、重复、占位不应独占页面；封面、过渡、单一判断页有意简洁时，在评审依据中说明理由。
- 先定信息关系再选组件：真实数量/趋势才用数据图，机制/流程/架构才用关系图，精确对比才用矩阵。无数据不画虚假数量，无顺序不加因果箭头，不把图表比例当 KPI。
- `Visible` 保留结论、关键数据、证据标签和必要限制；`Talk` 是现场提示，`Delivery` 展开口述，`Fallback` 准备追问与备用回答。关键证据、风险或口径不能只藏在备注。
- 新稿在 `working-state.json` 记录逐页 `slide_quality`（`quality_profile` 为稿件自身的版本标识，不是 Skill 发布版本号）；未逐页评审的旧稿在 H5 中只能作安全预览。H5 在 `render-review.json` 记录 `content_quality` 与逐页 `page_reviews`，语义评审、视觉检查与实际浏览器检查须分别通过。
- 视觉主体紧随判断，避免小表格漂浮在空白中央；不靠填字、虚假数字、装饰或拉伸空卡消灭合理留白。
- 导航是工具不是内容：右下页码与翻页控件低对比、透明、不使用胶囊底或常态阴影；悬停、键盘焦点与触屏仍可操作，且不遮挡正文。

## 校验

```bash
claude plugin validate . --strict          # 或 npm run validate
(cd skills/presentation-content-architect && python3 tests/run.py)
(cd skills/h5-report-generator && python3 tests/run.py)
```

- `plugin validate` 只检查 `skills` 数组中的路径存在，**不校验** `SKILL.md` 的 frontmatter；`name` 与 `description` 需人工核对。
- 测试必须在 Skill 根目录内运行；`tests/run.py` 会加载该 Skill 的 `scripts/` 模块，目录名含连字符时从仓库根直接发现会失败。
- 存在共享契约副本时，一致性由 `presentation-content-architect/tests/test_contract_parity.py` 守住：它比对共享契约/schema/解析器与 H5 侧的示例副本，两份 Skill 同时存在时漂移即失败，单独安装时跳过。手工核对仍可用 `diff -rq`。
- 本地开发可用 `./scripts/link-skills.sh` 把已发布 Skill 链接到 `~/.claude/skills/`。

## 能力演进与维护记录

当前 SOP 以各 Skill 的 `SKILL.md` 为准；以下变更背景只用于维护回溯，不作为运行时协议或旧格式兼容承诺：

- **V3 听众结果设计**：从作者表达转向听众任务，加入认知障碍、逐页认知旅程、核心/深挖路线、结构化问答、预演与恢复路径；复杂稿启用扩展后必须完整校验。
- **V4 沟通效果闭环**：加入洞察挖掘、持续注意力、三视角压力测试、五维效果计划和真实观察复盘；效果计划与观察独立记录，没有真实观察时为 `unknown`，不把模型自评当现场效果。
- **价值融合与发布整理**：以稳定 SOP 为主体按需吸收增强，取消高级扩展对所有普通稿的强制绑定；协议不再保留 `contract_version` 兼容字段，旧生成器与历史档案移除，HTML/CSS/JS 模板与主题移入 `assets/`，测试移入 `tests/`。

设计决策、验证历史与未验证边界见 [升级记录](docs/upgrade-notes.md)。

实际 Agent 行为评估见各 Skill 的 `references/evaluation.md`。静态测试不代替浏览器及真实听众验证。

## Skill 编写参考

入口精简、按需加载、流程明确、确定性校验、闭环复检，参见 [Claude Skill 编写最佳实践](https://platform.claude.com/docs/zh-CN/agents-and-tools/agent-skills/best-practices)。
