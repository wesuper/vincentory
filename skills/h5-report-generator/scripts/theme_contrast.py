#!/usr/bin/env python3
"""校验每个主题的皮肤令牌对比度（WCAG 2.1 AA）。

用法：python3 theme_contrast.py <skill-root>
退出码：0 全部达标；1 有未达标项。
"""
import glob
import os
import re
import sys

# 作为前景文字出现在 paper / surface 上的令牌，要求 AA 正文 4.5:1
TEXT_ON_PAPER = ['--ink', '--text-body', '--text-muted', '--ink-faint',
                 '--accent-ink', '--accent-ink-2', '--danger-ink', '--warn-ink', '--ok-ink']
# --on-accent 在结构样式里只出现在 --accent-fill 渐变（封面徽章 / 页面编号 / 表格表头）。
# 取渐变里最亮的一档校验，因为文字可能压在任何一档上。


def rgb(hexv):
    h = hexv.lstrip('#')
    if len(h) == 3:
        h = ''.join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(hexv):
    r, g, b = (_lin(c) for c in rgb(hexv))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def ratio(a, b):
    la, lb = luminance(a), luminance(b)
    hi, lo = max(la, lb), min(la, lb)
    return (hi + 0.05) / (lo + 0.05)


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else '.'
    files = sorted(glob.glob(os.path.join(root, 'templates/deck/themes/*.css')))
    if not files:
        sys.exit(f'找不到主题文件：{root}/templates/deck/themes/')

    failures = []
    checked = 0
    for path in files:
        name = os.path.basename(path)[:-4]
        src = open(path, encoding='utf-8').read()
        tok = dict(re.findall(r'(--[a-z0-9-]+)\s*:\s*(#[0-9a-fA-F]{6})\b', src))
        paper, surface = tok.get('--paper'), tok.get('--surface')
        if not paper or not surface:
            failures.append(f'{name}: 缺少 --paper 或 --surface')
            continue

        for t in TEXT_ON_PAPER:
            if t not in tok:
                continue
            for bg_name, bg in (('paper', paper), ('surface', surface)):
                r = ratio(tok[t], bg)
                checked += 1
                if r < 4.5:
                    failures.append(f'{name}: {t} {tok[t]} 在 {bg_name} 上只有 {r:.2f}:1（需 ≥ 4.5）')

        if '--on-accent' in tok:
            fill = re.search(r'--accent-fill\s*:\s*([^;]+);', src)
            stops = re.findall(r'#[0-9a-fA-F]{6}', fill.group(1)) if fill else []
            if not stops:
                failures.append(f'{name}: --accent-fill 里找不到色值，无法校验 --on-accent')
            for stop in stops:
                r = ratio(tok['--on-accent'], stop)
                checked += 1
                if r < 4.5:
                    failures.append(
                        f'{name}: --on-accent {tok["--on-accent"]} 在 --accent-fill 的 {stop} 档上只有 {r:.2f}:1（需 ≥ 4.5）')

    for f in failures:
        print(f'✗ {f}')
    print(f'对比度校验：{len(files)} 个主题，{checked} 组配对，{len(failures)} 项未达标')
    sys.exit(1 if failures else 0)


if __name__ == '__main__':
    main()
