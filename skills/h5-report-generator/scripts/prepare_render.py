#!/usr/bin/env python3
"""Parse and preflight contract, emit renderer-neutral render-input.json (stdlib)."""
import argparse, json, sys
from pathlib import Path
from content_contract import parse, validate, digest, load_json, review_slide_quality

THEMES=('light-gradient','kraft-paper','dune','ink-classic')

def route(s):
    role=s['role']; hint=s['visual_intent'].lower()
    if role=='COVER': return 'cover'
    if role=='AGENDA': return 'agenda'
    if role=='CTA': return 'closing'
    for key,layout in [('metric','metrics'),('指标','metrics'),('comparison','comparison'),('对比','comparison'),('table','table'),('timeline','timeline'),('时间轴','timeline'),('architecture','architecture'),('架构','architecture'),('flow','flow'),('因果','flow'),('risk','risk'),('风险','risk'),('card','cards'),('卡片','cards')]:
        if key in hint:return layout
    return 'content'

def prepare(md,handoff=None,state=None,theme=None):
    md=Path(md); meta,slides,errors=parse(md)
    if errors: raise ValueError('; '.join(errors))
    h={}; readiness='needs_review'; issues=[]
    if handoff:
        h=load_json(handoff)
        # A missing state can be a safe preview only if the handoff is otherwise coherent.
        if state is None and (h.get('contract_version')=='1.1' or meta['status']=='READY'):
            result=validate(md,handoff,None)
            remaining=[e for e in result['errors'] if e!='working-state.json required for READY or 1.1']
            if remaining: raise ValueError('; '.join(remaining))
            readiness='blocked' if h['readiness']=='blocked' else 'needs_review'
            issues.append('missing working-state.json; preview only')
        else:
            result=validate(md,handoff,state)
            if not result['ok']:raise ValueError('; '.join(result['errors']))
            readiness=h['readiness']
        issues+=h.get('unresolved',[])
    else: issues.append('no formal handoff; preview only')
    adapter=h.get('adapter',{}); selected=theme or adapter.get('theme') or 'light-gradient'
    if selected not in THEMES:raise ValueError('unknown theme '+str(selected))
    if adapter.get('profile','adaptive') not in ('standard','adaptive'):raise ValueError('unknown profile')
    quality=review_slide_quality(slides,load_json(state) if state and handoff else None)
    issues+=quality['issues']
    for s in slides:s['suggested_layout']=route(s)
    return {'content_quality':quality,'contract_version':h.get('contract_version','standalone'),'source_sha256':digest(md),'revision':h.get('revision'),'source_readiness':readiness,'issues':issues,'theme':selected,'profile':adapter.get('profile','adaptive'),'meta':meta,'intent':h.get('intent',{}),'slides':slides}

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('presentation');p.add_argument('--handoff');p.add_argument('--state');p.add_argument('--theme',choices=THEMES);p.add_argument('--out',default='render-input.json');a=p.parse_args()
    root=Path(a.presentation).parent
    try:
        h=a.handoff or (root/'handoff.json' if (root/'handoff.json').exists() else None); s=a.state or (root/'working-state.json' if (root/'working-state.json').exists() else None)
        result=prepare(a.presentation,h,s,a.theme);Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(f'{len(result["slides"])} slides; {result["source_readiness"]}; {result["theme"]} → {a.out}');return 0
    except (OSError,ValueError,TypeError,KeyError,AttributeError) as e:print(f'PRECHECK ERROR: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
