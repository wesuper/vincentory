#!/usr/bin/env python3
"""校验生成的 H5 汇报是否符合结构契约与演讲备注契约。

SKILL.md 里的校验清单过去只能靠人眼逐条看（「每页都有 lead-bar 吗」「备注 id
对得上吗」）。一次生成 20 页时，这条路径漏检是常态：漏一页 lead-bar 浏览器
完全正常，只有汇报当天才发现。这个脚本把清单里**可机械判定**的部分固化下来。

用法:
    python3 scripts/validate_deck.py index.html
    python3 scripts/validate_deck.py index.html --target-minutes 20
    python3 scripts/validate_deck.py index.html --theme kraft-paper

退出码: 0 通过（可能有警告）；1 有 error。

设计说明:
- 只做静态解析，不跑浏览器。版式是否溢出、演讲者视图是否可用仍需人工在
  1366×768 / 1920×1080 实测，那部分在 SKILL.md Step 4d 里。
- 备注数组用 json 解析而不是 eval。示例与骨架都要求写合法 JSON，所以这里
  顺带把「写了 JS 字面量（单引号、尾逗号、注释）导致解析失败」也当成错误。
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field

# 页面结构契约：内容页三段式的三个锚点
CONTENT_PAGE = 'content-page'
CONTENT_HEADER = 'content-header'
CONTENT_BODY = 'content-body'
LEAD_BAR = 'lead-bar'

REQUIRED_NOTE_FIELDS = ('id', 'title', 'purpose', 'talk', 'transition')
OPTIONAL_NOTE_FIELDS = (
    'section', 'minutes', 'cue', 'interaction', 'delivery',
    'advance', 'fallback', 'pronunciation', 'autoAdvanceSeconds',
)
KNOWN_THEMES = ('light-gradient', 'kraft-paper', 'dune', 'ink-classic')

# 投影常见两档，用于提示人工实测
SCREEN_SIZES = ('1366×768', '1920×1080')


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def class_list(tag: str) -> set[str]:
    m = re.search(r'class="([^"]*)"', tag)
    return set(m.group(1).split()) if m else set()


def strip_tags(text: str) -> str:
    text = re.sub(r'<[^>]+>', '', text)
    return re.sub(r'\s+', ' ', text).strip()


def split_sections(html: str) -> list[tuple[str, str]]:
    """切成 (section 起始标签, section 内容) 列表。"""
    out = []
    for m in re.finditer(r'(<section\b[^>]*>)([\s\S]*?)</section>', html):
        out.append((m.group(1), m.group(2)))
    return out


def elements_with_class(html: str, marker: str) -> list[str]:
    """取出每个 class 含 marker 元素的内部 HTML，按 div 嵌套配对切分。

    两个坑都要躲开：
    1. 不能用 `<div … class="…marker…">` 直接匹配，`\\b` 会在连字符处成立，
       于是 `toc-cell-header` 也被当成 `toc-cell`，逐格检查数量翻倍。
       这里先取出 class 属性、切成 token 再精确比对。
    2. 不能用正则找最近的 `</div>`，目标元素内部还有嵌套 div，提前收尾会把
       后续格子一起吞掉。必须按嵌套深度配对。
    """
    out = []
    for m in re.finditer(r'<div\b([^>]*)>', html):
        classes = class_list(m.group(0))
        if marker not in classes:
            continue
        i = m.end()
        depth = 1
        for tag in re.finditer(r'<div\b|</div>', html[i:]):
            if tag.group(0) == '</div>':
                depth -= 1
                if depth == 0:
                    out.append(html[i:i + tag.start()])
                    break
            else:
                depth += 1
    return out


def direct_children_of_classes(inner: str, parent_marker: str) -> str | None:
    """取出 class 含 parent_marker 的第一个元素的内部 HTML（按 div 配对，不依赖解析器）。"""
    m = re.search(r'<div\b[^>]*class="[^"]*\b' + re.escape(parent_marker) + r'\b[^"]*"[^>]*>', inner)
    if not m:
        return None
    i = m.end()
    depth = 1
    for tag in re.finditer(r'<div\b|</div>', inner[i:]):
        if tag.group(0) == '</div>':
            depth -= 1
            if depth == 0:
                return inner[i:i + tag.start()]
        else:
            depth += 1
    return None


def first_element_classes(fragment: str) -> set[str]:
    m = re.search(r'<[a-z][a-z0-9]*\b[^>]*>', fragment.strip())
    return class_list(m.group(0)) if m else set()


def parse_notes(html: str, rep: Report) -> list[dict]:
    """Read speaker notes as JSON data; never execute input JavaScript."""
    m = re.search(r'window\.SPEAKER_NOTES\s*=\s*', html)
    if not m:
        rep.error('找不到 window.SPEAKER_NOTES 数组：演讲者视图会整页空白')
        return []
    try:
        value, _ = json.JSONDecoder().raw_decode(html[m.end():])
        if isinstance(value,list):
            return value
    except ValueError:
        pass
    rep.error('SPEAKER_NOTES 必须是合法 JSON 数组；检查引号、逗号和括号')
    return []


def check_notes(notes: list[dict], slide_ids: list[str], rep: Report) -> None:
    if not notes:
        if slide_ids: rep.error("备注数组为空")
        return

    if len(notes) != len(slide_ids):
        rep.error(f'备注条数 {len(notes)} ≠ 页数 {len(slide_ids)}：演讲者视图会有页面显示"—"')

    missing = [i for i, n in enumerate(notes, 1) if not isinstance(n, dict)]
    if missing:
        rep.error(f'第 {missing} 条备注不是对象')
        return

    ids = [n.get('id') for n in notes]
    dupes = sorted({i for i in ids if isinstance(i,str) and i and ids.count(i) > 1})
    if dupes:
        rep.error(f'备注 id 重复：{", ".join(dupes)}')

    if ids != slide_ids:
        rep.error("备注 ID/顺序与页面不一致")
    if all(isinstance(i,str) for i in ids) and sorted(filter(None, ids)) != sorted(slide_ids):
        only_notes = sorted(set(filter(None, ids)) - set(slide_ids))
        only_slides = sorted(set(slide_ids) - set(filter(None, ids)))
        detail = []
        if only_notes:
            detail.append(f'备注多出来的 id: {", ".join(only_notes)}')
        if only_slides:
            detail.append(f'页面没有对应备注: {", ".join(only_slides)}')
        rep.error('备注 id 与 data-slide-id 不一致（' + '；'.join(detail) + '）')

    for i, n in enumerate(notes, 1):
        nid = n.get('id') or f'#{i}'
        for f in REQUIRED_NOTE_FIELDS:
            v = n.get(f)
            if f == 'talk':
                if not isinstance(v, list) or not v:
                    rep.error(f'备注 {nid}: talk 必须是非空数组')
                continue
            if not isinstance(v, str) or not v.strip():
                rep.error(f'备注 {nid}: 缺必填字段 {f}')

        talk = n.get('talk')
        if isinstance(talk, list):
            if not 2 <= len(talk) <= 4:
                rep.error(f'备注 {nid}: talk 有 {len(talk)} 条，超过 4 条说明这页该拆')
            for t in talk:
                if not isinstance(t, str) or not t.strip():
                    rep.error(f'备注 {nid}: talk 含空条目')
                elif len(t) > 40:
                    rep.error(f'备注 {nid}: talk 有一条 {len(t)} 字，超过 40 字建议压缩')

        minutes = n.get('minutes')
        if minutes is not None and not (isinstance(minutes, (int, float)) and not isinstance(minutes,bool) and math.isfinite(minutes) and minutes > 0):
            rep.error(f'备注 {nid}: minutes 必须为正数或省略')

        for f in ('cue', 'interaction', 'delivery', 'advance', 'fallback', 'pronunciation'):
            if f not in n or n[f] in (None, ''):
                continue
            v = n[f]
            ok = (isinstance(v, str) and v.strip()) or (
                isinstance(v, list) and v and all(isinstance(x, str) and x.strip() for x in v))
            if not ok:
                rep.error(f'备注 {nid}: {f} 必须是文本或非空文本数组')


def check_notes_not_repeating_page(notes: list[dict], lead_bars: dict[str, str], rep: Report) -> None:
    """备注不该复述页面 lead-bar——念出来等于观众读两遍同一句。"""
    for n in notes:
        if not isinstance(n, dict):
            continue
        lead = lead_bars.get(n.get('id', ''))
        if not lead:
            continue
        lead_plain = strip_tags(lead).replace('结论：', '').strip()
        if len(lead_plain) < 8:
            continue
        for t in n.get('talk') or []:
            if not isinstance(t, str):
                continue
            t_plain = t.strip()
            if len(t_plain) < 8:
                continue
            if t_plain in lead_plain or lead_plain in t_plain:
                rep.warn(f'备注 {n.get("id")}: talk 复述了本页 lead-bar「{lead_plain[:24]}…」')


def check_slides(html: str, rep: Report, profile: str = "standard") -> tuple[list[str], dict[str, str]]:
    sections = split_sections(html)
    if not sections:
        rep.error('找不到 <section class="slide">：没有任何页面')
        return [], {}

    if profile == "standard" and len(sections) < 5:
        rep.error(f'只有 {len(sections)} 页，SKILL.md 要求最少 5 页')

    slide_ids: list[str] = []
    lead_bars: dict[str, str] = {}
    content_numbers: list[str] = []

    for idx, (tag, inner) in enumerate(sections, 1):
        sid_m = re.search(r'data-slide-id="([^"]+)"', tag)
        id_m = re.search(r'\bid="([^"]+)"', tag)
        sid = sid_m.group(1) if sid_m else ''
        label = sid or (id_m.group(1) if id_m else f'第{idx}页')

        if not sid:
            rep.error(f'{label}: 缺 data-slide-id（备注按它绑定）')
        elif not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', sid):
            rep.error(f'{label}: data-slide-id 必须是小写字母数字连字符')
        else:
            slide_ids.append(sid)

        if idx == 1 and 'active' not in class_list(tag):
            rep.error('第一页缺 class="active"：打开时不会显示封面')

        if CONTENT_PAGE not in class_list(tag) and CONTENT_PAGE not in inner[:400]:
            continue  # 封面 / 目录 / 收尾不套三段式

        # 内容页：content-header 在前，content-body 里 lead-bar 排第一
        header_i = inner.find(CONTENT_HEADER)
        body_i = inner.find(CONTENT_BODY)
        if header_i == -1:
            rep.error(f'{label}: 内容页缺 .content-header')
        if body_i == -1:
            rep.error(f'{label}: 内容页缺 .content-body')
        if header_i != -1 and body_i != -1 and header_i > body_i:
            rep.error(f'{label}: .content-header 必须排在 .content-body 之前')

        num = re.search(r'class="[^"]*\bcontent-number\b[^"]*"[^>]*>\s*([^<]*)<', inner)
        if num:
            content_numbers.append(num.group(1).strip())
        else:
            rep.error(f'{label}: 内容页缺 .content-number')

        title = re.search(r'class="[^"]*\bcontent-title\b[^"]*"[^>]*>([\s\S]*?)</', inner)
        if not title:
            rep.error(f'{label}: 内容页缺 .content-title（标题即结论）')
        elif not re.search(r'[，。！？、；：]|是|为|需|应|已|将|要', strip_tags(title.group(1))):
            rep.warn(f'{label}: 标题「{strip_tags(title.group(1))[:20]}」读起来像话题词，不像结论句')

        body = direct_children_of_classes(inner, CONTENT_BODY)
        if body is not None:
            first = first_element_classes(body)
            if LEAD_BAR not in first:
                got = ' '.join(sorted(first)) or '空'
                if LEAD_BAR in inner:
                    rep.error(f'{label}: .lead-bar 存在但不在 .content-body 首位（首位是 {got}）')
                else:
                    rep.error(f'{label}: 缺 .lead-bar 结论条——标题即结论、结论条复述，缺一条就不算合格')
            lead = None
            for m in re.finditer(r'<div\b[^>]*>', inner):
                if LEAD_BAR in class_list(m.group(0)):
                    lead = re.match(r'([\s\S]*?)</div>', inner[m.end():])
                    break
            if lead:
                lead_bars[sid] = lead.group(1)
                if '结论' not in strip_tags(lead.group(1)):
                    rep.warn(f'{label}: lead-bar 没有以「结论：」开头')

        # 只数页面级要点（卡片之外的 li）；卡片内部条目属于同一要点组，
        # 把卡片里的 li 一起数会把正常的三栏卡片页误判为超载。
        outside_cards = re.sub(r'<div\b[^>]*class="[^"]*\bcard\b[^"]*"[^>]*>[\s\S]*?</div>\s*</div>', '', inner)
        li_count = len(re.findall(r'<li\b', outside_cards))
        if li_count > 7:
            rep.warn(f'{label}: 页面级要点 {li_count} 个，超过 7 个建议拆页')

    if len(slide_ids) != len(set(slide_ids)):
        rep.error("data-slide-id 重复")
    # 内容页编号应从 01 起连续
    expected = [f'{i:02d}' for i in range(1, len(content_numbers) + 1)]
    if content_numbers and content_numbers != expected:
        rep.error(f'.content-number 应连续为 01..{len(content_numbers):02d}，实际为 {content_numbers}')

    return slide_ids, lead_bars


def check_structure(html: str, rep: Report, profile: str = "standard") -> None:
    if 'class="progress-bar"' not in html:
        rep.error('缺 <div class="progress-bar">：顶部进度条失效')
    if 'id="prevBtn"' not in html or 'id="nextBtn"' not in html:
        rep.error('缺 #prevBtn / #nextBtn：无法翻页')
    if 'page-indicator' not in html:
        rep.error('缺 .page-indicator：不显示页码')
    # 注释里提到 slideOrder 是正常的（说明为什么不维护它），只拦真正的声明
    if re.search(r'(?:const|let|var)\s+slideOrder\s*=', html):
        rep.error('不允许声明 slideOrder：翻页顺序由 DOM 顺序决定')

    # 逐格校验，不能只比全局计数：结构示例里 .toc-concl 可能出现在说明性位置，
    # 全局计数会把「某一格缺结论、别处多一个」算平，漏掉真实的缺格。
    toc_cells = elements_with_class(html, 'toc-cell')
    if not toc_cells and profile == "standard":
        rep.warn('没有 .toc-cell：目录页缺结论卡')
    for i, cell in enumerate(toc_cells, 1):
        if 'toc-concl' not in cell:
            rep.error(f'目录第 {i} 格缺 .toc-concl（每章一句结论）')
        if 'toc-points' not in cell:
            rep.error(f'目录第 {i} 格缺 .toc-points（≥2 条要点，且必须是 .toc-concl 的兄弟元素）')
        else:
            points = re.search(r'<ul\b[^>]*class="[^"]*\btoc-points\b[^"]*"[^>]*>([\s\S]*?)</ul>', cell)
            if points and len(re.findall(r'<li\b', points.group(1))) < 2:
                rep.error(f'目录第 {i} 格的 .toc-points 少于 2 条要点')

    # 只看 <body> 之后：样式表里也有 .cover-chip 选择器，查全文会漏掉正文缺失。
    body = html[html.index('<body>') + len('<body>'):] if '<body>' in html else html
    chips = sum(1 for m in re.finditer(r'<div\b[^>]*>', body)
                if 'cover-chip' in class_list(m.group(0)))
    if chips == 0 and (profile == "standard" or 'class="cover-page"' in body):
        rep.error('封面缺 .cover-chip 结论胶囊（结论先行要求 2–3 个）')
    elif chips and not 2 <= chips <= 3:
        rep.error(f'封面只有 {chips} 个 .cover-chip，要求 2–3 个')


def check_theme(html: str, expected: str | None, rep: Report) -> str | None:
    m = re.search(r'<html\b[^>]*data-theme="([^"]+)"', html)
    theme = m.group(1) if m else None
    if not theme:
        rep.warn('缺 <html data-theme>：将使用默认主题 light-gradient')
    elif theme not in KNOWN_THEMES:
        rep.error(f'未知主题 {theme}，可用：{", ".join(KNOWN_THEMES)}')

    if theme and expected and theme != expected:
        rep.error(f'data-theme="{theme}" 与请求的主题 {expected} 不一致')

    # 内联的皮肤必须与 data-theme 对应：填 A 却内联 B，[data-theme="A"] 选择器全部落空
    if theme and theme != 'light-gradient':
        if f'[data-theme="{theme}"]' not in html:
            rep.error(f'data-theme="{theme}" 但内联的皮肤里没有 [data-theme="{theme}"] 块：整页会掉回浏览器默认样式')
        for other in KNOWN_THEMES:
            if other == theme or other == 'light-gradient':
                continue
            if f'[data-theme="{other}"] {{' in html or f'[data-theme="{other}"]{{' in html:
                rep.warn(f'同时内联了 {other} 的皮肤：只需一个，多个会互相覆盖')

    return theme


def check_hardcoded_colors(html: str, rep: Report) -> None:
    """页面里写死颜色 / 字体，换主题时会留下不协调色块。"""
    body = re.sub(r'<style[\s\S]*?</style>', '<style></style>', html)
    body = re.sub(r'<script[\s\S]*?</script>', '<script></script>', body)
    hits = re.findall(r'style="[^"]*(?:color|background)\s*:\s*[^"]*#[0-9a-fA-F]{3,6}', body)
    if hits:
        rep.warn(f'页面内联了 {len(hits)} 处写死的颜色（如 {hits[0][:60]}…）：换主题后会是残留色块')
    font_hits = re.findall(r'style="[^"]*font-family\s*:', body)
    if font_hits:
        rep.warn(f'页面内联了 {len(font_hits)} 处 font-family：应交给主题令牌 --font-display / --font-body')


def check_placeholders(html: str, rep: Report) -> None:
    """生成完还留着 {{X}} 说明占位符没替换干净，页面上会直接显示大括号。"""
    left = sorted(set(re.findall(r'\{\{[A-Z_]+\}\}', html)))
    if left:
        rep.error(f'仍有未替换的占位符：{", ".join(left)}')


def check_duplicate_ids(html: str, rep: Report) -> None:
    """内容页被写两遍（常见于骨架里同名占位符出现多次）会产出重复 id。"""
    ids = re.findall(r'<section\b[^>]*\bid="([^"]+)"', html)
    dupes = sorted({i for i in ids if ids.count(i) > 1})
    if dupes:
        rep.error(f'<section> id 重复：{", ".join(dupes)}（内容页可能被写入两遍）')


def check_budget(notes: list[dict], target: int | None, rep: Report) -> float | None:
    mins = [n.get('minutes') for n in notes if isinstance(n, dict)]
    if not mins or any(not isinstance(m, (int, float)) or isinstance(m, bool) or not math.isfinite(m) or m <= 0 for m in mins):
        if target:
            rep.error('部分或全部备注缺少有效 minutes：无法核对时间预算')
        return None
    total = float(sum(float(m) for m in mins if isinstance(m, (int, float))))
    if target:
        if total > target * 0.9 + 1e-9:
            rep.error(f'计划总时长 {total:g} 分钟超过 {target} 分钟的 90%（{target * 0.9:g}）：没给互动和意外留缓冲')
        elif total < target * 0.55:
            rep.warn(f'计划总时长 {total:g} 分钟不足 {target} 分钟的 55%：可能讲不满')
    return total


def main() -> None:
    ap = argparse.ArgumentParser(description='校验 H5 汇报的结构契约与演讲备注契约')
    ap.add_argument('file', help='生成的 index.html')
    ap.add_argument('--target-minutes', type=float, default=None, help='汇报时长（分钟），用于核对时间预算')
    ap.add_argument('--theme', default=None, help='期望的主题 ID')
    ap.add_argument('--profile', choices=('standard','adaptive'), default='standard')
    args = ap.parse_args()
    if args.target_minutes is not None and (not math.isfinite(args.target_minutes) or args.target_minutes <= 0): ap.error('target-minutes must be positive finite')

    try:
        html = open(args.file, encoding='utf-8').read()
    except OSError as exc:
        sys.exit(f'读不到文件：{exc}')

    rep = Report()
    theme = check_theme(html, args.theme, rep)
    check_structure(html, rep, args.profile)
    slide_ids, lead_bars = check_slides(html, rep, args.profile)
    notes = parse_notes(html, rep)
    check_notes(notes, slide_ids, rep)
    check_notes_not_repeating_page(notes, lead_bars, rep)
    check_placeholders(html, rep)
    check_duplicate_ids(html, rep)
    check_hardcoded_colors(html, rep)
    total = check_budget(notes, args.target_minutes, rep)

    for w in rep.warnings:
        print(f'⚠️  {w}')
    for e in rep.errors:
        print(f'❌ {e}')

    pages = len(split_sections(html))
    planned = f'{total:g} 分钟' if total is not None else '—'
    print(f'结构校验：{pages} 页 / {len(notes)} 条备注 / 主题 {theme or "默认"} / 计划 {planned}')
    print(f'  {len(rep.errors)} errors, {len(rep.warnings)} warnings')
    if not rep.errors:
        print('  仍需人工实测（脚本看不到渲染结果）：'
              + ' / '.join(SCREEN_SIZES) + ' 下每页 scrollHeight === clientHeight；'
              '按 P 验证演讲者视图与观众屏同步')
    sys.exit(1 if rep.errors else 0)


if __name__ == '__main__':
    main()
