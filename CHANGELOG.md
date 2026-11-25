# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- `h5-report-generator` v5：结论先行信息架构。封面新增结论胶囊（`.cover-chips`）；目录页每章升级为结论卡（一句话结论 `.toc-concl` + 2–3 条要点 `.toc-points`）；每个内容页强制三段式（`.content-header` 标题即结论 + `.lead-bar` 结论条 + `.content-body`）。
- `light-gradient` 主题重写样式系统与交互引擎：顶部进度指示条、可见页码、折叠分组、无 CDN 容错、打印分页；移除 `slideOrder` 数组，改为按 DOM 顺序翻页。
- `scripts/generate.py` 标注为 v4 兼容参考，不再作为主流程。
- 移除 `blue-business` 主题：风格与产品定位不符，模板收敛为单一 PC 端主题 `light-gradient`。

## [0.1.0] - 2026-08-05

### Added

- Initialized the vincentory skill repository.
- Added the create-skill engineering skill.
- Added Claude Code plugin and marketplace manifests.
