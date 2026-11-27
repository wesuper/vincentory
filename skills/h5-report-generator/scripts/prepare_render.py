#!/usr/bin/env python3
"""Parse and preflight contract, emit renderer-neutral render-input.json (stdlib)."""
import argparse, json, sys, re
from pathlib import Path
from content_contract import parse, validate, digest, load_json, review_slide_quality, review_experience

THEMES=('light-gradient','kraft-paper','dune','ink-classic')

EXPLICIT_LAYOUTS = {
    'metric':'metrics','metrics':'metrics','trend':'metrics','comparison':'comparison','table':'table',
    'timeline':'timeline','architecture':'architecture','mechanism':'architecture','flow':'flow',
    'risk':'risk','decision':'comparison','change':'comparison','expectation':'timeline',
    'attribution':'table','action':'content','learning':'content','cards':'cards','card':'cards',
    'content':'content','quote':'content','text':'content','diagram':'architecture'
}

def needs_preview(plan):
    return (plan.get('source_readiness')!='ready' or
            plan.get('content_quality',{}).get('status')!='reviewed' or
            plan.get('experience_quality',{}).get('status','not_applicable') not in ('reviewed','not_applicable'))

def route(s):
    role=s['role']; hint=s['visual_intent'].lower()
    if role=='COVER': return 'cover'
    if role=='AGENDA': return 'agenda'
    if role=='CTA': return 'closing'
    prefix=re.match(r'^([a-z_-]+)\s*[:：]',hint)
    if prefix and prefix[1] in EXPLICIT_LAYOUTS: return EXPLICIT_LAYOUTS[prefix[1]]
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
        if state is None:
            result=validate(md,handoff,None)
            remaining=[e for e in result['errors'] if e!='working-state.json required for formal handoff']
            if remaining: raise ValueError('; '.join(remaining))
            readiness='blocked' if h['readiness']=='blocked' else 'needs_review'
            issues.append('missing working-state.json; preview only')
        else:
            result=validate(md,handoff,state)
            if not result['ok']:
                # A missing review may be previewed; an invalid declared review is an error.
                st=load_json(state)
                missing_review=(result['errors']==['missing per-slide content review']
                                and 'quality_profile' not in st and 'slide_quality' not in st
                                and 'experience' not in st and 'experience_profile' not in h
                                and 'experience_sha256' not in h)
                if not missing_review: raise ValueError('; '.join(result['errors']))
                readiness='needs_review'
                issues.append('missing per-slide content review; preview only')
            else:
                readiness=h['readiness']
        issues+=h.get('unresolved',[])
    else: issues.append('no formal handoff; preview only')
    adapter=h.get('adapter',{}); selected=theme or adapter.get('theme') or 'light-gradient'
    if selected not in THEMES:raise ValueError('unknown theme '+str(selected))
    if adapter.get('profile','adaptive') not in ('standard','adaptive'):raise ValueError('unknown profile')
    st=load_json(state) if state and handoff else None
    quality=review_slide_quality(slides,st)
    experience=review_experience(slides,st,h)
    issues+=quality['issues']+experience['issues']
    for s in slides:s['suggested_layout']=route(s)
    return {'content_quality':quality,'experience_quality':experience,'source_sha256':digest(md),'revision':h.get('revision'),'source_readiness':readiness,'issues':issues,'theme':selected,'profile':adapter.get('profile','adaptive'),'meta':meta,'intent':h.get('intent',{}),'slides':slides}

def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('presentation');p.add_argument('--handoff');p.add_argument('--state');p.add_argument('--theme',choices=THEMES);p.add_argument('--out',default='render-input.json');a=p.parse_args()
    root=Path(a.presentation).parent
    try:
        h=a.handoff or (root/'handoff.json' if (root/'handoff.json').exists() else None); s=a.state or (root/'working-state.json' if (root/'working-state.json').exists() else None)
        result=prepare(a.presentation,h,s,a.theme);Path(a.out).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8'); print(f'{len(result["slides"])} slides; {result["source_readiness"]}; {result["theme"]} → {a.out}');return 0
    except (OSError,ValueError,TypeError,KeyError,AttributeError) as e:print(f'PRECHECK ERROR: {e}',file=sys.stderr);return 1
if __name__=='__main__':raise SystemExit(main())
