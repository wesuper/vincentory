#!/usr/bin/env python3
"""Safe, offline baseline renderer for simple Markdown. Advanced visual layouts remain agent work."""
import argparse, html, json, re, sys
from pathlib import Path
from prepare_render import THEMES, needs_preview

ROOT=Path(__file__).resolve().parents[1]/'assets'/'deck'

def plain(s):
    s=re.sub(r'^\s*(?:#{1,6}\s+|[-*+]\s+|\d+[.)]\s+)', '',s)
    s=re.sub(r'\[([^]]+)\]\(([^)]+)\)',r'\1 (\2)',s)
    return s.replace('**','').replace('`','').strip()

def esc(s):return html.escape(plain(str(s)))
def lines(s):return [plain(x) for x in s.splitlines() if x.strip()]

def render_table(rows):
    """Render a run of `|` rows. Ragged rows are padded, not dropped: verify_render
    checks row association, so a truncated table would fail fidelity."""
    cells=[[c.strip() for c in x.strip().strip('|').split('|')] for x in rows]
    cells=[r for r in cells if not all(re.fullmatch(r':?-{3,}:?',c) for c in r)]
    if not cells: return None
    width=max(len(r) for r in cells)
    if width<2: return None
    cells=[r+['']*(width-len(r)) for r in cells]
    return '<table class="mini-table evidence-table"><thead><tr>'+''.join('<th>'+esc(c)+'</th>' for c in cells[0])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(c)+'</td>' for c in row)+'</tr>' for row in cells[1:])+'</tbody></table>'

def render_prose(raw, layout="content"):
    groups=[]; current=None
    for line in raw:
        if line.startswith('### '):
            current=[plain(line),[]];groups.append(current)
        elif current is not None:current[1].append(plain(line))
        else:groups.append(['',[plain(line)]])
    if groups and all(g[0] for g in groups) and 2<=len(groups)<=4:
        flow=layout=='flow'
        cls='evidence-grid evidence-flow' if flow else 'evidence-grid'
        cards=[]
        for i,(title,vals) in enumerate(groups):
            step='<span class="evidence-step" aria-hidden="true">'+f'{i+1:02d}'+'</span>' if flow else ''
            cards.append('<div class="evidence-card">'+step+'<h2 class="evidence-title">'+esc(title)+'</h2><ul class="card-list">'+''.join('<li class="card-item"><span>'+esc(x)+'</span></li>' for x in vals)+'</ul></div>')
        return '<div class="'+cls+'" data-cols="'+str(len(groups))+'">'+''.join(cards)+'</div>'
    return '<div class="card"><ul class="card-list">'+''.join('<li class="card-item"><span class="card-item-dot"></span><span>'+esc(x)+'</span></li>' for x in lines('\n'.join(raw)))+'</ul></div>'

def render_visible(s, layout="content"):
    """Visible accepts tables, lists and headings mixed (content contract). Render
    consecutive `|` rows as one table and the rest as prose, preserving source order."""
    raw=[x for x in s.splitlines() if x.strip()]
    blocks=[]; run=[]; mode=None
    for line in raw:
        kind='table' if line.lstrip().startswith('|') else 'prose'
        if kind!=mode and run: blocks.append((mode,run)); run=[]
        mode=kind; run.append(line)
    if run: blocks.append((mode,run))
    if len(blocks)==1: return render_table(blocks[0][1]) or render_prose(blocks[0][1],layout)
    parts=[]
    for kind,rows in blocks:
        parts.append(render_table(rows) if kind=='table' else render_prose(rows,layout))
    return ''.join(p for p in parts if p)

def render(plan):
    theme=plan['theme']; slides=plan['slides']; meta=plan['meta'];
    if theme not in THEMES or not slides:raise ValueError('invalid theme or empty slides')
    if plan.get('source_readiness')=='blocked':raise ValueError('blocked source: resolve or sanitize in source before rendering')
    base=(ROOT/'skeleton.html').read_text(encoding='utf-8')
    # Replace only the original presentation region; preserve nav/engine intact.
    start=base.index('<div class="presentation">');end=base.index('<!-- 导航：',start)
    sections=[];num=0;preview=needs_preview(plan)
    for i,s in enumerate(slides):
        sid=s['slide_id'];title=esc(s['title']);take=esc(s['takeaway']);visible=s['visible'];items=lines(visible);role=s['role']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',sid):raise ValueError('invalid slide id')
        status='<div class="footnote" data-review="preview">预览｜内容待确认</div>' if preview else ''
        cls='slide active' if i==0 else 'slide'
        if role=='COVER' and 2<=len(items)<=3 and all(len(x)<=45 for x in items):
            content='<div class="cover-page"><div class="cover-badge">'+esc(meta.get('audience',''))+'</div><h1 class="cover-title">'+title+'</h1><p class="cover-subtitle">'+take+'</p><div class="cover-info">'+''.join('<div class="cover-info-item">'+esc(meta[k])+'</div>' for k in ('author','department','date') if meta.get(k))+'</div><div class="cover-chips">'+''.join('<div class="cover-chip">'+esc(x)+'</div>' for x in items)+'</div>'+status+'<div class="cover-hint">← / → 翻页 · P 演讲者视图</div></div>'
        elif role=='AGENDA' and re.search(r'^### ',visible,re.M):
            groups=[]
            for raw in visible.splitlines():
                if raw.startswith('### '):groups.append([plain(raw),[]])
                elif raw.strip() and groups:groups[-1][1].append(plain(raw))
            if not groups or not all(3<=len(vals)<=4 for _,vals in groups) or not visible.strip().startswith('### '):
                num+=1;content='<div class="content-page"><div class="content-header"><div class="content-number">'+f'{num:02d}'+'</div><div><div class="content-title">'+title+'</div><div class="content-subtitle">'+esc(s['chapter'])+'</div></div></div><div class="content-body"><div class="lead-bar"><b>结论：</b>'+take+'</div>'+render_visible(visible,s.get('suggested_layout','content'))+status+'</div></div>'
            else:
                cells=''.join('<div class="toc-cell"><div class="toc-cell-header"><div class="toc-column-number">'+str(j+1)+'</div><div class="toc-column-title">'+esc(heading)+'</div></div><div class="toc-concl">'+esc(vals[0])+'</div><ul class="toc-points">'+''.join('<li>'+esc(v)+'</li>' for v in vals[1:])+'</ul></div>' for j,(heading,vals) in enumerate(groups))
                content='<div class="toc-page"><div class="toc-header"><div><div class="toc-title">'+title+'</div><div class="toc-subtitle">'+take+'</div></div></div><div class="toc-stack">'+cells+'</div>'+status+'</div>'
        elif role=='CTA' and 1<=len(items)<=3:
            content='<div class="qa-page"><h1 class="content-title">'+title+'</h1><p class="cover-subtitle">'+take+'</p><div class="close-lines">'+''.join('<div class="close-line">'+esc(x)+'</div>' for x in items)+'</div>'+status+'</div>'
        else:
            num+=1;content='<div class="content-page"><div class="content-header"><div class="content-number">'+f'{num:02d}'+'</div><div><div class="content-title">'+title+'</div><div class="content-subtitle">'+esc(s['chapter'])+'</div></div></div><div class="content-body"><div class="lead-bar"><b>结论：</b>'+take+'</div>'+render_visible(visible,s.get('suggested_layout','content'))+status+'</div></div>'
        sections.append(f'<section class="{cls}" id="slide-{sid}" data-slide-id="{sid}">{content}</section>')
    base=base[:start]+'<div class="presentation">\n'+'\n'.join(sections)+'\n</div>\n'+base[end:]
    base=base.replace('{{THEME}}',theme).replace('{{TITLE}}',esc(meta['title']))
    base=re.sub(r'<script src="https://cdn\.jsdelivr\.net/[^\"]+"\s*></script>','',base)
    for marker,file in [('STYLE_CSS',ROOT/'style.css'),('THEME_CSS',ROOT/'themes'/f'{theme}.css'),('SCRIPT_JS',ROOT/'script.js')]:
        slot=f'/* === {marker} === */'
        if base.count(slot)!=1:raise ValueError('template slot invalid: '+marker)
        base=base.replace(slot,slot+'\n'+file.read_text(encoding='utf-8'),1)
    notes=json.dumps([s['notes'] for s in slides],ensure_ascii=False).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026').replace('\u2028','\\u2028').replace('\u2029','\\u2029')
    base=base.replace('window.SPEAKER_NOTES = [];','window.SPEAKER_NOTES = '+notes+';',1)
    exp=plan.get('experience_quality',{})
    if not preview and exp.get('status')=='reviewed':
        route={'core_slide_ids':exp['core_slide_ids'],'short_minutes':round(exp['short_minutes'],6)}
        route_json=json.dumps(route,ensure_ascii=True).replace('<','\\u003c').replace('>','\\u003e').replace('&','\\u0026')
        base=base.replace('</body>', '<script>window.PRESENTATION_ROUTE = '+route_json+';</script>\n</body>',1)
    return base

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('plan');p.add_argument('out');a=p.parse_args()
    try:
        plan=json.loads(Path(a.plan).read_text(encoding='utf-8'));Path(a.out).write_text(render(plan),encoding='utf-8');print(a.out);return 0
    except (OSError,ValueError,TypeError,KeyError) as e:print(f'RENDER ERROR: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
