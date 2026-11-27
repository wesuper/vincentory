# 故障排查

先定位问题属于内容、装配、运行还是现场设备。不要以修改引擎或静默删除内容来通过检查。

| 症状 | 核查 | 修正 |
|---|---|---|
| 无法翻页、总页数为0 | 控制台异常；DOM 中 `.presentation > section.slide` 是否存在；导航 ID 是否齐全 | 保留 skeleton 和完整 script.js；按 DOM 顺序组织页，id/data-slide-id 唯一；不要单独维护页序数组 |
| 备注为空或串页 | `window.SPEAKER_NOTES` 是否为合法 JSON；每条 id 与 data-slide-id 一致 | 从内容源恢复备注；运行 verify_render.py 和 validate_deck.py |
| 目录无结论或编号跳号 | standard 结构、`.toc-concl + .toc-points`、内容页连续编号 | 按 page-templates.md 恢复组件，不为 adaptive 强行补目录 |
| 页面溢出 | 动画结束后检查两个投屏尺寸；逐页 scrollHeight/clientHeight 与 scrollWidth/clientWidth | 改列宽、分组、图表尺寸；仍无法容纳时回传源端，不压小字体或删关键限定 |
| 字体颜色或主题异常 | `<html data-theme>` 与内联皮肤是否匹配、令牌是否齐全、槽位注释是否闭合 | 结构 CSS 在前，仅一个主题 CSS 在后；用主题令牌，运行 theme_contrast.py 与 sync-template.py |
| 图表空白 | `.echart[data-option]` 合法 JSON、容器非零尺寸、库是否加载；Mermaid `.mermaid-diagram[data-code]` 语法 | 采用内置初始化；核实真实数据映射；无网络时提供本地 SVG/表格/文本替代 |
| 图片无法显示 | 来源、权限、路径、离线访问及实际尺寸 | 单文件交付时内嵌经授权资源或提供同等证据替代；不删除必要标签 |
| P 视图预览空白 | 浏览器弹窗权限、iframe 同源限制、打开方式、控制台及预览通信 | 使用允许本地文件或本地静态服务的真实浏览器；不能用空白预览通过验收 |
| 双屏不同步 | 观众窗口是否打开，握手、消息通信与心跳状态；黑白/冻结状态 | 恢复连接后测试双向翻页、标注与退出；物理投屏仍需现场目视确认 |
| 计时或草稿异常 | 显式开始/暂停计时；翻页后本页计时重置；localStorage 权限及路径键 | 用 T/R 操作并检查存储；不声称无实际验证的持久化 |
| 性能差 | 图表数量、图片体积、重复初始化、动画及控制台错误 | 压缩经授权图片；避免重复库及初始化；保留 reduced-motion；关键内容静态可读 |

## 浏览器诊断（只读）
在浏览器控制台检查实际页面、备注及可见尺寸。先等待动画结束或模拟 reduced motion。
```javascript
const slides = [...document.querySelectorAll('.presentation > section.slide')];
console.table(slides.map(s => ({
  id: s.dataset.slideId,
  active: s.classList.contains('active'),
  height: s.clientHeight,
  scrollHeight: s.scrollHeight,
  width: s.clientWidth,
  scrollWidth: s.scrollWidth
})));
console.log('notes', Array.isArray(window.SPEAKER_NOTES) ? window.SPEAKER_NOTES.length : 0);
console.log('nav', ['prevBtn','nextBtn','currentPage','totalPages'].map(id => [id, !!document.getElementById(id)]));
```
隐藏页尺寸可能为零；逐页切换后再测，不把隐藏页数据当作溢出结果。调试时可临时加 outline 观察布局，交付前删除调试样式。遇到静态校验报错先定位 slide_id 和具体字段，再改对应源或组件、重新封存/渲染/复检；工具或环境不可用时记 not_tested。
