# H5 适配与回传

保持协议中立。联用时传真实路径：presentation.md + handoff.json + working-state.json 及同目录 outline.md、claim-map.json、sources.md。下游按自己的 SKILL.md 校验并生成 render-input.json；内容 READY 不代表渲染 READY。用户明确主题优先于 adapter.theme；默认 light-gradient。不要在前置稿写 HTML/CSS 类名。短稿、纯分享、附录按真实页序，不能为模板强行制造目录/收尾。默认保留原有四主题和演讲者备注；视觉语义建议（指标、比较、因果、流程、时间轴、架构、决策）由下游选择模板。出现无法一屏容纳、来源限制或模板不支持时，回传：

```json
{"slide_id":"s01","issue":"两档投屏尺寸下出现溢出","available_space":"1366×768，正文约需再少一行","proposed_revision":"将非关键实现细节移到备注；保留数值、口径和限制","changes_semantics":true}
```

修改真源需要用户授权或前置阶段已授权的编辑范围；重封存 revision，重新验证。仅版式变更不改变内容。用户只要内容时，无需安装下游 Skill。用户明确要求组合且两个 Skill 可用时，完成内容阶段即调用下游，不重复采访；非 ready 只提供带状态提示的预览（敏感或矛盾内容应先隔离）。
