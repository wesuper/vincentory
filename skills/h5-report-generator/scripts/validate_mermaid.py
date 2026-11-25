#!/usr/bin/env python3
"""
Mermaid 语法校验工具

检测 Mermaid 代码块中的常见语法问题，特别是 HTML 特殊字符
（< > & " '）未转义导致渲染失败的问题。

用法:
    # 校验单个文件中的所有 Mermaid 代码块
    python validate_mermaid.py <file.md>

    # 校验字符串（通过 stdin）
    echo 'graph TD; A-->B' | python validate_mermaid.py --stdin

    # 输出修复后的内容
    python validate_mermaid.py <file.md> --fix

    # 作为模块导入
    from validate_mermaid import validate_mermaid_code, fix_mermaid_code
"""

import re
import sys
import json
import argparse
from dataclasses import dataclass
from typing import List, Tuple


@dataclass
class MermaidIssue:
    """Mermaid 语法问题"""
    line: int
    column: int
    severity: str  # "error" | "warning"
    message: str
    original: str
    suggestion: str = ""


# === 需要检测的危险字符模式 ===

# HTML 特殊字符在 Mermaid 节点文本中的使用（未用引号包裹时会导致解析失败）
# 例: A["包含 <tag> 的文本"] ✅ (引号内安全)
# 例: A[包含 <tag> 的文本]   ❌ (裸 < > 导致解析失败)
DANGEROUS_CHARS = {
    '<': '&lt;',
    '>': '&gt;',
    '&': '&amp;',
}

# Mermaid 关键字（可能被误用为节点名）
MERMAID_KEYWORDS = {
    'graph', 'flowchart', 'sequenceDiagram', 'classDiagram',
    'stateDiagram', 'erDiagram', 'gantt', 'pie', 'gitGraph',
    'journey', 'C4Context', 'mindmap', 'timeline', 'sankey',
    'xychart', 'block', 'packet-beta',
}

# 图表方向关键字
GRAPH_DIRS = {'TD', 'TB', 'BT', 'RL', 'LR'}


def validate_mermaid_code(code: str, filename: str = "<input>") -> List[MermaidIssue]:  # noqa: unused
    """
    校验一段 Mermaid 代码，返回问题列表。

    Args:
        code: Mermaid 代码字符串
        filename: 文件名（用于错误报告）

    Returns:
        MermaidIssue 列表
    """
    issues: List[MermaidIssue] = []
    lines = code.split('\n')

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()

        # 跳过空行和注释
        if not stripped or stripped.startswith('%%'):
            continue

        # === 检查 1: 裸 < > 字符（不在引号内） ===
        issues.extend(_check_bare_angle_brackets(stripped, line_num))

        # === 检查 2: 节点标签中未转义的 & ===
        issues.extend(_check_bare_ampersand(stripped, line_num))

        # === 检查 3: 节点 ID 使用关键字 ===
        issues.extend(_check_keyword_as_id(stripped, line_num))

        # === 检查 4: 子图中使用特殊字符作为标题 ===
        issues.extend(_check_subgraph_title(stripped, line_num))

    return issues


def _is_inside_quotes(text: str, pos: int) -> bool:
    """判断某个位置是否在引号内（支持 "" 和 ""）"""
    in_double = False
    in_unicode = False
    for i, ch in enumerate(text):
        if i == pos:
            return in_double or in_unicode
        if ch == '"' and not in_unicode:
            in_double = not in_double
        elif ch == '“' and not in_double:  # "
            in_unicode = True
        elif ch == '”' and in_unicode:  # "
            in_unicode = False
    return in_double or in_unicode


def _strip_mermaid_arrows(line: str) -> str:
    """
    移除 Mermaid 连接语法（箭头），返回仅含节点文本的行。
    这样后续检查 <> 时不会误报 --> === 等连接符。
    """
    # 多字符箭头（长箭头先匹配，避免子串误匹配）
    arrows = [
        r'--?>>', r'--?x', r'--?o',      # -->>  --x  --o  及变体
        r'==?>>',                          # ==>>
        r'-\.-+->',  r'-\.-+-',           # -.->  -.-
        r'==>', r'===',                    # ==>  ===
        r'-->', r'---',                    # -->  ---
        r'\|[^|]*\|',                      # |text| 标注
    ]
    result = line
    for pattern in arrows:
        result = re.sub(pattern, lambda m: ' ' * len(m.group()), result)
    return result


def _check_bare_angle_brackets(line: str, line_num: int) -> List[MermaidIssue]:
    """检查裸 < > 字符（排除 Mermaid 箭头语法）"""
    issues = []
    scan_line = _strip_mermaid_arrows(line)
    i = 0
    while i < len(scan_line):
        ch = scan_line[i]
        if ch in ('<', '>') and not _is_inside_quotes(line, i):
            if ch == '<':
                # 检查是否构成 HTML 标签（如 <br>），是则整体跳过
                rest = line[i:]
                m = re.match(r'<[a-zA-Z/][^>]*>', rest)
                if m:
                    tag = m.group(0)
                    issues.append(MermaidIssue(
                        line=line_num,
                        column=i + 1,
                        severity="warning",
                        message=f"HTML 标签 '{tag}' 在节点文本中可能导致渲染问题，建议用引号包裹节点标签",
                        original=tag,
                        suggestion=f"将节点标签用引号包裹: [\"text with {tag}\"]",
                    ))
                    i += len(tag)  # 跳过整个标签
                    continue
            issues.append(MermaidIssue(
                line=line_num,
                column=i + 1,
                severity="error",
                message=f"裸 '{ch}' 字符在 Mermaid 中会导致解析失败",
                original=ch,
                suggestion=f"使用 HTML 实体: {DANGEROUS_CHARS.get(ch, ch)}，或将节点标签用引号包裹: [\"text\"]",
            ))
        i += 1
    return issues


def _check_bare_ampersand(line: str, line_num: int) -> List[MermaidIssue]:
    """检查裸 & 字符"""
    issues = []
    for i, ch in enumerate(line):
        if ch == '&' and not _is_inside_quotes(line, i):
            # 检查是否是已有的 HTML 实体
            rest = line[i:]
            if re.match(r'&[a-zA-Z]+;', rest) or re.match(r'&#[0-9]+;', rest):
                continue  # 已经是合法实体
            issues.append(MermaidIssue(
                line=line_num,
                column=i + 1,
                severity="warning",
                message="裸 '&' 字符可能干扰 Mermaid 解析",
                original='&',
                suggestion="使用 &amp; 替代",
            ))
    return issues


def _check_keyword_as_id(line: str, line_num: int) -> List[MermaidIssue]:
    """检查节点 ID 是否使用了 Mermaid 关键字"""
    issues = []
    # 匹配 节点ID[标签] 或 节点ID --> 的模式
    pattern = r'(?:^|\s)([a-zA-Z_]\w*)(?:\s*\[|-->|---|-\.|==>)'
    for match in re.finditer(pattern, line):
        node_id = match.group(1)
        if node_id.lower() in {kw.lower() for kw in MERMAID_KEYWORDS}:
            # 排除图表声明行（如 graph TD）
            first_word = line.split()[0] if line.split() else ''
            if first_word.lower() in {kw.lower() for kw in MERMAID_KEYWORDS}:
                continue
            issues.append(MermaidIssue(
                line=line_num,
                column=match.start(1) + 1,
                severity="error",
                message=f"节点 ID '{node_id}' 与 Mermaid 关键字冲突，会导致解析错误",
                original=node_id,
                suggestion=f"使用其他名称: {node_id}1, node_{node_id}, {node_id}_node",
            ))
    return issues


def _check_subgraph_title(line: str, line_num: int) -> List[MermaidIssue]:
    """检查子图标题中的特殊字符"""
    issues = []
    match = re.match(r'\s*subgraph\s+(.+)', line)
    if match:
        title = match.group(1).strip()
        # 子图标题如果包含特殊字符需要用引号包裹
        if any(ch in title for ch in '<>&') and not (title.startswith('"') and title.endswith('"')):
            issues.append(MermaidIssue(
                line=line_num,
                column=line.find(title) + 1,
                severity="error",
                message=f"子图标题包含特殊字符: '{title}'",
                original=title,
                suggestion=f'用引号包裹: subgraph "{title}"',
            ))
    return issues


def fix_mermaid_code(code: str) -> Tuple[str, List[str]]:
    """
    自动修复 Mermaid 代码中的常见问题。

    Returns:
        (修复后的代码, 修复描述列表)
    """
    fixes = []
    lines = code.split('\n')
    result = []

    for line_num, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped or stripped.startswith('%%'):
            result.append(line)
            continue

        fixed_line = line

        # 修复裸 & (非实体)
        def replace_bare_amp(m):
            pos = m.start()
            if _is_inside_quotes(fixed_line, pos):
                return m.group(0)
            rest = fixed_line[pos:]
            if re.match(r'&[a-zA-Z]+;', rest) or re.match(r'&#[0-9]+;', rest):
                return m.group(0)
            fixes.append(f"Line {line_num}: & → &amp;")
            return '&amp;'
        fixed_line = re.sub(r'&', replace_bare_amp, fixed_line)

        # 修复裸 < >（跳过 Mermaid 箭头语法和引号内文本）
        scan = _strip_mermaid_arrows(fixed_line)
        chars = list(fixed_line)
        j = 0
        while j < len(scan):
            ch = scan[j]
            if ch in ('<', '>') and not _is_inside_quotes(fixed_line, j):
                if ch == '<':
                    rest = fixed_line[j:]
                    m = re.match(r'<[a-zA-Z/][^>]*>', rest)
                    if m:
                        j += len(m.group(0))  # 跳过 HTML 标签
                        continue
                chars[j] = DANGEROUS_CHARS[ch]
                fixes.append(f"Line {line_num}: {ch} → {DANGEROUS_CHARS[ch]}")
            j += 1
        fixed_line = ''.join(chars)

        result.append(fixed_line)

    return '\n'.join(result), fixes


def extract_mermaid_blocks(text: str) -> List[Tuple[int, str, str]]:
    """
    从 Markdown 文本中提取所有 Mermaid 代码块。

    Returns:
        [(起始行号, 代码内容, 围栏前后文本)]
    """
    blocks = []
    pattern = re.compile(r'^```mermaid\s*$', re.MULTILINE)
    lines = text.split('\n')

    i = 0
    while i < len(lines):
        if pattern.match(lines[i]):
            start_line = i + 1  # 1-indexed
            code_lines = []
            j = i + 1
            while j < len(lines) and not lines[j].strip().startswith('```'):
                code_lines.append(lines[j])
                j += 1
            code = '\n'.join(code_lines)
            blocks.append((start_line, code, lines[i]))
            i = j + 1
        else:
            i += 1

    return blocks


def validate_file(filepath: str, fix: bool = False) -> int:
    """
    校验文件中的所有 Mermaid 代码块。

    Returns:
        问题数量（0 = 通过）
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"❌ 文件不存在: {filepath}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ 读取失败: {e}", file=sys.stderr)
        return 1

    blocks = extract_mermaid_blocks(content)

    if not blocks:
        print(f"ℹ️  {filepath}: 未找到 Mermaid 代码块")
        return 0

    total_issues = 0
    all_fixes = []

    for block_start, code, _fence in blocks:
        if fix:
            fixed_code, fixes = fix_mermaid_code(code)
            all_fixes.extend([(block_start, code, fixed_code)])
            for desc in fixes:
                print(f"  🔧 {desc}")
            total_issues += len(fixes)
        else:
            issues = validate_mermaid_code(code, filepath)
            total_issues += len(issues)
            if issues:
                print(f"\n📍 Mermaid 代码块 (行 {block_start}):")
                for issue in issues:
                    icon = "❌" if issue.severity == "error" else "⚠️"
                    print(f"  {icon} L{issue.line}:L{issue.column} [{issue.severity}] {issue.message}")
                    if issue.suggestion:
                        print(f"     💡 {issue.suggestion}")

    if fix and all_fixes:
        # 应用修复
        new_content = content
        for block_start, old_code, fixed_code in reversed(all_fixes):
            new_content = new_content.replace(old_code, fixed_code, 1)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"\n✅ 已修复 {len(all_fixes)} 个 Mermaid 代码块")

    if total_issues == 0:
        print(f"✅ {filepath}: 所有 Mermaid 代码块校验通过")
    else:
        status = "已修复" if fix else "发现问题"
        print(f"\n{'✅' if fix else '❌'} {filepath}: {status} {total_issues} 个")

    return total_issues


def main():
    parser = argparse.ArgumentParser(
        description='Mermaid 语法校验工具 — 检测特殊字符导致的渲染失败'
    )
    parser.add_argument('file', nargs='?', help='要校验的文件路径')
    parser.add_argument('--stdin', action='store_true', help='从 stdin 读取')
    parser.add_argument('--fix', action='store_true', help='自动修复问题')
    parser.add_argument('--json', action='store_true', help='JSON 格式输出')

    args = parser.parse_args()

    if args.stdin:
        content = sys.stdin.read()
        blocks = extract_mermaid_blocks(content)
        if not blocks:
            # 尝试作为纯 Mermaid 代码处理
            blocks = [(1, content, "```mermaid")]

        for _bstart, code, _ in blocks:
            if args.fix:
                fixed, fixes = fix_mermaid_code(code)
                if fixes:
                    print(fixed)
                else:
                    print(code, end='')
            else:
                issues = validate_mermaid_code(code)
                if args.json:
                    print(json.dumps([{
                        'line': i.line,
                        'column': i.column,
                        'severity': i.severity,
                        'message': i.message,
                        'original': i.original,
                        'suggestion': i.suggestion,
                    } for i in issues], ensure_ascii=False, indent=2))
                else:
                    for issue in issues:
                        icon = "❌" if issue.severity == "error" else "⚠️"
                        print(f"{icon} L{issue.line}:L{issue.column} [{issue.severity}] {issue.message}")
                        if issue.suggestion:
                            print(f"   💡 {issue.suggestion}")
        return

    if not args.file:
        parser.error('请提供文件路径或使用 --stdin')

    exit_code = validate_file(args.file, fix=args.fix)
    sys.exit(1 if exit_code > 0 and not args.fix else 0)


if __name__ == '__main__':
    main()
