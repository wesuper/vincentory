"""Validate a separate effectiveness plan and optional observation ledger."""
import argparse, hashlib, json, datetime
from pathlib import Path
from content_contract import parse, validate
DIMS=('insight','understanding','credibility','transfer','action')
PROFILE='communication-effectiveness'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p): return json.loads(Path(p).read_text(encoding='utf-8'))
def require(ok,msg):
    if not ok: raise ValueError(msg)
def fields(obj,names):
    require(isinstance(obj,dict),'expected object')
    for k in names: require(isinstance(obj.get(k),str) and bool(obj[k].strip()),'missing text: '+k)
def evaluate(md,handoff,plan,observations=None):
    hd=load(handoff); p=load(plan)
    state=Path(handoff).parent/'working-state.json'
    require(validate(md,handoff,state)['ok'],'source contract invalid')
    require(hd.get('readiness')=='ready','source not ready')
    require(p.get('profile')==PROFILE,'invalid plan profile')
    require(p.get('content_sha256')==sha(md)==hd.get('content_sha256'),'source hash mismatch')
    if 'experience_profile' in hd or 'experience_sha256' in hd:
        require(hd.get('experience_profile')=='audience-journey' and p.get('experience_sha256')==hd.get('experience_sha256') and bool(hd.get('experience_sha256')),'experience seal mismatch')
    else:
        require('experience_sha256' not in p,'unexpected experience seal for base plan')
        require(p.get('handoff_sha256')==sha(handoff),'base plan handoff hash mismatch')
        require(p.get('state_sha256')==sha(state),'base plan state hash mismatch')
    require(type(p.get('revision')) is int and p['revision']==hd.get('revision'),'revision mismatch')
    _,slides,errors=parse(md); require(not errors,'source parse failed')
    ids={s['slide_id'] for s in slides}
    dims=p.get('dimensions'); require(isinstance(dims,dict) and set(dims)==set(DIMS),'five dimensions required')
    active=[]
    for k in DIMS:
        d=dims[k]; fields(d,['reason'])
        require(type(d.get('applicable')) is bool,'applicable must be boolean')
        if d['applicable']:
            active.append(k); fields(d,['baseline','criterion','method','window','owner'])
            anchors=d.get('slide_ids')
            require(isinstance(anchors,list) and bool(anchors) and all(isinstance(x,str) and x in ids for x in anchors) and len(set(anchors))==len(anchors),'invalid slide anchors: '+k)
    require(bool(active),'at least one applicable dimension')
    result={k:'unknown' if k in active else 'not_applicable' for k in DIMS}
    seen=set(); mode='unobserved'
    if observations:
        o=load(observations)
        require(o.get('profile')==PROFILE and o.get('plan_sha256')==sha(plan),'observation plan mismatch')
        mode=o.get('mode'); require(mode in ('actual','rehearsal'),'invalid mode')
        records=o.get('records'); require(isinstance(records,list),'records must be array')
        for rec in records:
            fields(rec,['dimension','result','observed_at','source','observation','limitations'])
            k=rec['dimension']; require(k in active and k not in seen,'duplicate or inapplicable observation')
            require(rec['result'] in ('met','partial','not_met','unknown'),'invalid result')
            date=datetime.date.fromisoformat(rec['observed_at'])
            require(date.isoformat()==rec['observed_at'],'date must be YYYY-MM-DD')
            seen.add(k); result[k]=rec['result']
    return {'ok':True,'mode':mode,'dimensions':result,'applicable_count':len(active),'recorded_count':len(seen),'assessed_count':sum(result[k]!='unknown' for k in active),'missing_records':[k for k in active if k not in seen],'actual_effect_assessed':mode=='actual' and any(result[k]!='unknown' for k in active),'scope':'record consistency only; no independent verification of observations'}
def main():
    p=argparse.ArgumentParser(description=__doc__)
    for k in ('presentation','handoff','plan'):p.add_argument(k)
    p.add_argument('--observations'); a=p.parse_args()
    try:r=evaluate(a.presentation,a.handoff,a.plan,a.observations)
    except (ValueError,TypeError,KeyError,AttributeError,OSError) as e:r={'ok':False,'error':str(e)}
    print(json.dumps(r,ensure_ascii=False,indent=2));return 0 if r['ok'] else 1
if __name__=='__main__':raise SystemExit(main())
