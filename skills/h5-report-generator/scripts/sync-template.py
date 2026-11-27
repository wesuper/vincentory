#!/usr/bin/env python3
"""把 deck/ 的样式与脚本同步进单文件示例 h5-report-template.html。

为什么需要它：示例文件必须内联全部 CSS/JS（产物要求单文件可移植），
但手写内联会与 deck/ 漂移。这个脚本保证示例永远是 deck/ 的机械拷贝。

三个槽位（都靠槽位注释定位，不靠标签猜测）：

  /* === STYLE_CSS === */    → deck/style.css
  /* === THEME_CSS === */    → deck/themes/<默认主题>.css
  /* === SCRIPT_JS === */    → deck/script.js

每个槽位的内容 = 槽位注释行之后、下一个槽位注释或宿主标签结束之前的部分。
示例文件里那个 6 条演讲备注的 <script> 不归本脚本管，原样保留。

用法：
  python3 scripts/sync-template.py <skill-root>
  python3 scripts/sync-template.py .          # 在 skill 根目录执行
"""
import os
import json
import re
import sys

DEFAULT_THEME = 'light-gradient'

STYLE_CSS = '/* === STYLE_CSS === */'
THEME_CSS = '/* === THEME_CSS === */'
SCRIPT_JS = '/* === SCRIPT_JS === */'


def read(path):
    with open(path, encoding='utf-8') as f:
        return f.read()


def write(path, text):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(text)


def need(text, anchor, where):
    n = text.count(anchor)
    if n != 1:
        raise SystemExit(f'{where}: 槽位 {anchor} 出现 {n} 次，应恰好 1 次')
    return text.index(anchor)


def inject_style(html, root):
    css = read(os.path.join(root, 'assets/deck/style.css')).strip()
    theme = read(os.path.join(root, f'assets/deck/themes/{DEFAULT_THEME}.css')).strip()

    # 槽位顺序固定：STYLE_CSS 在前，THEME_CSS 在后，同处一个 <style> 里。
    i = need(html, STYLE_CSS, 'html')
    j = need(html, THEME_CSS, 'html')
    if i > j:
        raise SystemExit('槽位顺序错误：THEME_CSS 应在 STYLE_CSS 之后')

    style_end = html.index('</style>', j)
    # 注意：注释标记必须整行闭合。写成 `/* === THEME_CSS === */ （当前：x）`
    # 会让括号里的文字落到注释外，被浏览器当成选择器前缀，后面所有规则失效。
    style_body = (css + '\n\n'
                  + THEME_CSS + '\n'
                  + f'/* 当前主题：{DEFAULT_THEME} */\n'
                  + theme + '\n')

    start = html.index('\n', i) + 1
    return html[:start] + style_body + html[style_end:]


def inject_script(html, root):
    js = read(os.path.join(root, 'assets/deck/script.js')).strip()
    start = need(html, SCRIPT_JS, 'html') + len(SCRIPT_JS)
    start = html.index('\n', start) + 1
    end = html.index('</script>', start)
    return html[:start] + js + '\n' + html[end:]


def force_theme_attr(html):
    """把 <html data-theme> 对齐到实际内联的皮肤。

    内联的皮肤文件用 [data-theme="x"] 作选择器（默认主题用 :root）。属性值与皮肤
    不一致时选择器全部落空，整页掉回浏览器默认样式——背景透明、黑字、无字体。
    这个失败极其显眼但很难归因，所以由脚本保证两者永远同步。
    """
    m = re.search(r'<html\b[^>]*>', html)
    if not m:
        raise SystemExit('html: 找不到 <html> 起始标签')
    tag = m.group(0)
    fixed, n = re.subn(r'\sdata-theme="[^"]*"', f' data-theme="{DEFAULT_THEME}"', tag)
    if n == 0:
        fixed = tag[:-1] + f' data-theme="{DEFAULT_THEME}">'
    return html[:m.start()] + fixed + html[m.end():]


def check(html, root):
    """同步后的机械校验：CSS 注释平衡 + 皮肤令牌齐全 + 结构/皮肤不串层。"""
    problems = []

    css = html[html.index('<style>') + len('<style>'):html.index('</style>')]
    depth = 0
    for m in re.finditer(r'/\*|\*/', css):
        if m.group(0) == '/*':
            depth += 1
            if depth > 1:
                problems.append('CSS 注释嵌套：块注释里出现了 /*（CSS 不支持嵌套注释）')
                break
        else:
            depth -= 1
            if depth < 0:
                problems.append('CSS 注释失衡：出现多余的 */')
                break
    if depth > 0:
        problems.append('CSS 注释未闭合：结尾仍处于注释中，其后样式全部失效')

    # 期望集合不能来自「当前主题文件里有什么」——删掉一个令牌，期望集也会跟着缩小，
    # 永远抓不到。基准取四个主题文件的并集，再逐个校验完整性与主题间一致性。
    theme_dir = os.path.join(root, 'assets/deck/themes')
    themes = {}
    for fn in sorted(os.listdir(theme_dir)):
        if fn.endswith('.css'):
            themes[fn[:-4]] = set(re.findall(r'(--[a-z0-9-]+)\s*:', read(os.path.join(theme_dir, fn))))

    if len(themes) > 1:
        union = set().union(*themes.values())
        for name, toks in themes.items():
            absent = sorted(union - toks)
            if absent:
                problems.append(f'主题 {name} 缺少令牌：' + ', '.join(absent))

    skin = themes.get(DEFAULT_THEME, set())
    struct_css = read(os.path.join(root, 'assets/deck/style.css'))
    presenter = re.search(r'\.presenter\s*\{[^}]*\}', struct_css)
    outside = struct_css.replace(presenter.group(0), '') if presenter else struct_css
    leaked = set(re.findall(r'(--[a-z0-9-]+)\s*:', outside)) & skin
    if leaked:
        problems.append('令牌分层破损，结构文件里出现皮肤令牌：' + ', '.join(sorted(leaked)))

    # 只在皮肤段里查，不能查整份 CSS：演讲者视图的 .presenter 固定深色覆盖块
    # 也声明了同名令牌，用它兜底会掩盖观众页缺令牌的真实缺陷。
    skin_css = css[css.index('/* === THEME_CSS === */'):]
    missing = [t for t in skin if not re.search(re.escape(t) + r'\s*:', skin_css)]
    if missing:
        problems.append('皮肤段缺少令牌（观众页会掉回浏览器默认值）：' + ', '.join(sorted(missing)))

    # Read strict JSON only; do not execute JavaScript or accept object literals.
    match = re.search(r'window\.SPEAKER_NOTES\s*=\s*', html)
    notes = []
    try:
        if not match:
            raise ValueError('missing notes')
        value, _ = json.JSONDecoder().raw_decode(html[match.end():])
        if not isinstance(value,list) or any(not isinstance(item,dict) or not isinstance(item.get('id'),str) for item in value):
            raise ValueError('invalid notes')
        notes = [item['id'] for item in value]
    except ValueError:
        problems.append('备注必须是合法 JSON 数组')
    slides = re.findall(r'data-slide-id="([^"]+)"', html)
    if sorted(notes) != sorted(slides):
        problems.append(f'备注 id 与 data-slide-id 不匹配：notes={sorted(notes)} slides={sorted(slides)}')

    return problems


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    path = os.path.join(root, 'assets/h5-report-template.html')

    html = force_theme_attr(read(path))
    html = inject_style(html, root)
    html = inject_script(html, root)
    write(path, html)
    print(f'synced {path}')

    problems = check(html, root)
    if problems:
        for p in problems:
            print(f'  ✗ {p}')
        raise SystemExit(1)
    print(f'  ✓ 主题属性、注释平衡、令牌分层、备注对齐 全部通过（{DEFAULT_THEME}）')


if __name__ == '__main__':
    main()
