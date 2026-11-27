#!/usr/bin/env python3
"""Check render plan vs HTML text, order, notes; static only, no JS evaluation."""
import argparse, json, re, sys
from pathlib import Path
from html.parser import HTMLParser
from render_reference import plain
from content_contract import digest
from prepare_render import needs_preview

class Slides(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.pages=[];self.current=None;self.skip=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ('script','style'):self.skip+=1
        if tag=='section' and 'slide' in a.get('class','').split():
            self.current={'id':a.get('data-slide-id'),'text':[]};self.pages.append(self.current)
    def handle_endtag(self,tag):
        if tag in ('script','style'):self.skip=max(0,self.skip-1)
        if tag=='section':self.current=None
    def handle_data(self,data):
        if self.current is not None and not self.skip:self.current['text'].append(data)

def norm(s):return re.sub(r'\s+','',s)
def required(s):
    yield plain(s['title']);yield plain(s['takeaway'])
    for raw in s['visible'].splitlines():
        if not raw.strip():continue
        if raw.strip().startswith('|'):
            cells=[c.strip() for c in raw.strip().strip('|').split('|')]
            if all(re.fullmatch(r':?-{3,}:?',c) for c in cells):continue
            for c in cells:
                if c:yield plain(c)
            # Preserve row association as well as individual cell text.
            yield ''.join(plain(c) for c in cells)
        else:yield plain(raw)

def verify(plan,html):
    p=Slides();p.feed(html);errors=[];slides=plan['slides']
    if [x['id'] for x in p.pages]!=[x['slide_id'] for x in slides]:errors.append('slide id/order differs')
    for s,page in zip(slides,p.pages):
        actual=norm(''.join(page['text']))
        for val in required(s):
            if val and norm(val) not in actual:errors.append(f'{s["slide_id"]}: missing visible text {val[:100]}')
        if needs_preview(plan) and norm('预览｜内容待确认') not in actual:errors.append(f'{s["slide_id"]}: missing preview label')
    m=re.search(r'window\.SPEAKER_NOTES\s*=\s*',html)
    if not m:errors.append('missing notes')
    else:
        try:
            notes,_=json.JSONDecoder().raw_decode(html[m.end():]);expected=[s['notes'] for s in slides]
            if notes!=expected:errors.append('notes differ from source (including ID/order/time)')
        except ValueError:errors.append('notes must be JSON')
    route_matches=list(re.finditer(r'window\.PRESENTATION_ROUTE\s*=\s*(?=\{)',html))
    exp=plan.get('experience_quality',{})
    if not needs_preview(plan) and exp.get('status')=='reviewed':
        expected_route={'core_slide_ids':exp['core_slide_ids'],'short_minutes':round(exp['short_minutes'],6)}
        if len(route_matches)!=1: errors.append('missing or duplicate reviewed short route')
        else:
            try:
                route,_=json.JSONDecoder().raw_decode(html[route_matches[0].end():])
                if route!=expected_route: errors.append('short route differs from reviewed plan')
            except ValueError: errors.append('short route must be JSON')
    elif route_matches: errors.append('unreviewed short route must not be activated')
    return errors

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('plan');p.add_argument('html');p.add_argument('--source',help='verify source SHA-256 has not changed');a=p.parse_args()
    try:
        plan=json.loads(Path(a.plan).read_text(encoding='utf-8')); errors=verify(plan,Path(a.html).read_text(encoding='utf-8'))
        if a.source and digest(a.source)!=plan['source_sha256']:errors.append('source has changed; rerun prepare_render')
    except (ValueError,OSError,KeyError,TypeError) as e:errors=[str(e)]
    print(json.dumps({'ok':not errors,'errors':errors,'scope':'static text/order/notes only; human semantics and browser still required'},ensure_ascii=False,indent=2));return int(bool(errors))
if __name__=='__main__':raise SystemExit(main())
