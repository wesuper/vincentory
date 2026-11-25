# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-11-25

### Changed

- `h5-report-generator` v5：结论先行信息架构。封面新增结论胶囊（`.cover-chips`）；目录页每章升级为结论卡（一句话结论 `.toc-concl` + 2–3 条要点 `.toc-points`）；每个内容页强制三段式（`.content-header` 标题即结论 + `.lead-bar` 结论条 + `.content-body`）。
- `light-gradient` 主题重写样式系统与交互引擎：顶部进度指示条、可见页码、折叠分组、无 CDN 容错、打印分页；按 DOM 顺序翻页替代 `slideOrder` 数组。
- `light-gradient` 面向 PC 端 16:9 投屏重做排版：`clamp()` 流体字号与间距令牌，修复 1366×768 目录页溢出、收尾页装饰越界、目录卡空白与大屏稀疏页留白。
- `scripts/generate.py` 标注为 v4 兼容参考，不再作为主流程。

### Removed

- `h5-report-generator` 的 `blue-business` 主题目录（style / script / skeleton / 页面结构文档 / README）。风格与产品定位不符，模板收敛为单一 PC 端主题 `light-gradient`。

### Breaking

- `h5-report-generator` 移除 `slideOrder` 数组机制：翻页顺序改由 `<section class="slide">` 的 DOM 顺序决定，已生成的历史产物需删除该数组。

## [0.1.0] - 2026-08-05

### Added

- Initialized the vincentory skill repository.
- Added the create-skill engineering skill.
- Added Claude Code plugin and marketplace manifests.
