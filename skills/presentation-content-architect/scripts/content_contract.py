#!/usr/bin/env python3
"""Shared content parser and mechanical gate. Python 3.10+, stdlib only."""
import hashlib
import json
import math
import re
from pathlib import Path

MARKER = re.compile(r'^<!-- slide:id=([^\s]+)\s+role=([^\s]+)\s+chapter=([^\s]+)\s*-->\s*$', re.M)
ID = re.compile(r'[a-z0-9]+(?:-[a-z0-9]+)*\Z')
EID = re.compile(r'\[(E-[A-Za-z0-9-]+)\]')
FIELDS = ('Visible', 'Evidence', 'Visual Intent', 'Speaker Notes')
NOTES = ('Purpose','Talk','Transition','Minutes','Cue','Interaction','Fallback','Delivery','Advance','Pronunciation')
GATES = ('intent','narrative','evidence','audience_fit','objections','delivery','action','handoff')
CLAIM_STATES = set('verified qualified disputed insufficient false unverified hypothesis derived illustrative user_reported recommendation'.split())
STAGE_STATUS = dict.fromkeys(('INTAKE','QUESTION_DEFINED','SKELETON'),'DRAFT') | dict.fromkeys(('ENRICHED','REVIEW'),'REVIEW') | {'READY':'READY'}


def load_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def text(value):
    return isinstance(value,str) and bool(value.strip())


def strings(value):
    return isinstance(value,list) and all(text(v) for v in value)


def positive(value):
    return isinstance(value,(int,float)) and not isinstance(value,bool) and math.isfinite(value) and value > 0


def parse(path):
    md=Path(path).read_text(encoding='utf-8-sig'); errors=[]; meta={}; slides=[]
    front=re.match(r'\A---\n(.*?)\n---\s*\n',md,re.S)
    if not front: errors.append('missing front matter'); body=md
    else:
        body=md[front.end():]
        for line in front[1].splitlines():
            k,sep,v=line.partition(':')
            if not sep or k.strip() in meta: errors.append(f'invalid/duplicate front matter: {line}'); continue
            meta[k.strip()]=v.strip().strip('"\'')
    for key in ('title','audience','objective'):
        if not text(meta.get(key)): errors.append(f'front matter missing {key}')
    try: duration=float(meta.get('duration_minutes','nan'))
    except ValueError: duration=float('nan')
    if not positive(duration): errors.append('duration_minutes must be positive finite'); duration=None
    meta['duration_minutes']=duration
    if meta.get('status') not in ('DRAFT','REVIEW','READY'): errors.append('invalid presentation status')
    matches=list(MARKER.finditer(body))
    if not matches: errors.append('no slides found')
    if body.count('<!-- slide:') != len(matches): errors.append('malformed slide marker')
    for i,m in enumerate(matches):
        sid,role,chapter=m.groups(); chunk=body[m.end():matches[i+1].start() if i+1<len(matches) else len(body)].strip()
        chunk=re.sub(r'\n---\s*\Z','',chunk).strip()
        if not ID.fullmatch(sid): errors.append(f'{sid}: invalid slide_id')
        if not re.fullmatch('[A-Z][A-Z0-9_-]*',role): errors.append(f'{sid}: invalid role')
        header=re.match(r'# (.+)\n> Takeaway: (.+)\s*\n',chunk)
        if not header: errors.append(f'{sid}: missing title or Takeaway'); title=takeaway=''
        else: title,takeaway=(s.strip() for s in header.groups())
        sections=list(re.finditer(r'^## (.+?)\s*$',chunk,re.M)); sections_data={}
        if tuple(s[1] for s in sections)!=FIELDS: errors.append(f'{sid}: missing/duplicate/out-of-order section; expected {FIELDS}')
        for j,s in enumerate(sections):
            value=chunk[s.end():sections[j+1].start() if j+1<len(sections) else len(chunk)].strip()
            sections_data[s[1]]=value
            if not value: errors.append(f'{sid}: empty {s[1]}')
        raw=sections_data.get('Speaker Notes',''); note={'id':sid,'title':title,'section':chapter}
        fields=list(re.finditer(r'^(\w+):[ \t]*(.*)$',raw,re.M)); keys=[f[1] for f in fields]
        if len(set(keys))!=len(keys) or any(k not in NOTES for k in keys): errors.append(f'{sid}: unknown/duplicate note fields')
        for k in NOTES[:4]:
            if k not in keys: errors.append(f'{sid}: missing {k}')
        for j,f in enumerate(fields):
            val=(f[2]+'\n'+raw[f.end():fields[j+1].start() if j+1<len(fields) else len(raw)]).strip(); key=f[1]
            if key=='Talk':
                lines=val.splitlines(); talk=[s[2:].strip() for s in lines if s.startswith('- ')]
                if len(lines)!=len(talk) or not 2<=len(talk)<=4 or any(not x or len(x)>40 for x in talk): errors.append(f'{sid}: Talk must contain 2–4 nonempty bullets <=40 chars')
                note['talk']=talk
            elif key=='Minutes':
                try: num=float(val)
                except ValueError: num=float('nan')
                if not positive(num): errors.append(f'{sid}: Minutes must be positive finite')
                else: note['minutes']=num
            else:
                if not val or '\n' in val: errors.append(f'{sid}: {key} must be nonempty single line')
                note[key.lower()]=val
        slides.append({'slide_id':sid,'role':role,'chapter':chapter,'title':title,'takeaway':takeaway,'visible':sections_data.get('Visible',''),'evidence':sections_data.get('Evidence',''),'visual_intent':sections_data.get('Visual Intent',''),'notes':note})
    ids=[s['slide_id'] for s in slides]
    if len(ids)!=len(set(ids)): errors.append('duplicate slide ids')
    planned=sum(s['notes'].get('minutes',0) for s in slides)
    if duration and planned>duration*.9+1e-9: errors.append(f'planned minutes {planned:g} exceeds 90% budget')
    return meta,slides,errors



QUALITY_PROFILE = 'slide-review'
QUALITY_FIELDS = ('audience_question','information_gain','support','visual_reason','notes_gain','basis')

def review_slide_quality(slides, state):
    """Check review records + obvious content defects, not actual persuasiveness."""
    if not isinstance(state,dict) or not ('quality_profile' in state or 'slide_quality' in state):
        return {'status':'not_reviewed','issues':['missing per-slide content review']}
    issues=[]
    if state.get('quality_profile')!=QUALITY_PROFILE:
        issues.append('invalid quality_profile')
    records=state.get('slide_quality')
    if not isinstance(records,dict):
        return {'status':'needs_revision','issues':issues+['slide_quality must be an object']}
    if set(records)!=set(s['slide_id'] for s in slides):
        issues.append('slide_quality ids differ from slides')
    for s in slides:
        sid=s['slide_id']; rec=records.get(sid)
        if not isinstance(rec,dict):
            issues.append(f'{sid}: missing slide_quality record'); continue
        if rec.get('result') not in ('pass','revise'):
            issues.append(f'{sid}: invalid slide_quality result')
        elif rec['result']=='revise':
            issues.append(f'{sid}: slide_quality needs revision')
        for key in QUALITY_FIELDS:
            if not text(rec.get(key)):
                issues.append(f'{sid}: missing slide_quality {key}')
        # Detect clear placeholders / exact repetition, not enforce arbitrary length.
        clean=lambda v: re.sub(r'[\s#>*`|—\-:：。，、；;！!？?]+','',v).casefold()
        title,takeaway=clean(s['title']),clean(s['takeaway'])
        lines=[]
        for line in s['visible'].splitlines():
            if re.match(r'^\s*#{1,6}\s+',line) or re.fullmatch(r'[\s|:\-]+',line):
                continue
            if line.strip().startswith('|'):
                lines += [clean(c) for c in line.strip().strip('|').split('|') if clean(c)]
            elif clean(line):lines.append(clean(line))
        placeholders={'待补充','待完善','暂无内容','todo','tbd','placeholder','此处填写','略'}
        if lines and all(x in placeholders for x in lines):
            issues.append(f'{sid}: visible contains only placeholders')
        if s['role'] not in ('COVER','AGENDA','SECTION','DIVIDER'):
            if title and title==takeaway:
                issues.append(f'{sid}: title and takeaway exactly repeat')
            if lines and all(x in {title,takeaway} for x in lines):
                issues.append(f'{sid}: visible repeats title/takeaway only')
        # Purposeful sparse pages are allowed. Semantic adequacy and visual suitability
        # require review, not a character count or an automatic approval.
    return {'status':'needs_revision' if issues else 'reviewed','issues':issues}



# Optional audience journey and short route.
EXPERIENCE_PROFILE = 'audience-journey'
SCENE_REQUIREMENTS = {'executive_proposal': ('decision_scope', 'business_value', 'options_tradeoff', 'validation_exit'), 'architecture_review': ('constraints', 'alternatives', 'mechanism', 'failure_modes', 'verification'), 'risk_change': ('change_trigger', 'impact_scope', 'risk_controls', 'go_no_go_rollback', 'owner_escalation'), 'expectation_management': ('baseline_commitment', 'delta_forecast', 'cause_uncertainty', 'replan_decision', 'next_update'), 'progress_outcome': ('baseline_target', 'actual_impact', 'attribution', 'remaining_gap', 'next_investment'), 'promotion_defense': ('level_criteria', 'challenge_scope', 'personal_contribution', 'impact_evidence', 'leverage_growth'), 'technical_deep_dive': ('entry_problem', 'mental_model', 'mechanism', 'reproduction', 'failure_boundary', 'transfer'), 'team_announcement': ('why_change', 'who_is_affected', 'before_after', 'execution_support', 'understanding_check'), 'cross_team_alignment': ('shared_goal', 'interest_tradeoff', 'interfaces_dependencies', 'ownership', 'disagreement_resolution'), 'incident_review': ('impact_timeline', 'causal_evidence', 'system_factors', 'corrective_actions', 'effectiveness_check'), 'technical_strategy': ('context_drivers', 'strategic_choices', 'tradeoff_non_goals', 'staged_investment', 'signals_exit'), 'customer_solution': ('customer_scenario', 'fit_gap', 'integration_security', 'validation_acceptance', 'next_step'), 'general': ('audience_problem', 'specific_value', 'support_boundary', 'appropriate_next_step')}
AUDIENCE_FIELDS = ('authority','prior_knowledge','stakes','barrier','evidence_threshold','secondary_audience','basis')
OUTCOME_FIELDS = ('recall','observable_signal','check_method','next_step','success_boundary','follow_up','non_goal')
OPENING_FIELDS = ('why_now','promise','tension')
JOURNEY_FIELDS = ('audience_shift','question','listen_cue','check','recovery','basis')
REHEARSAL_FIELDS = ('recall','objection','compression','synchrony','action')
BEATS = {'orient','tension','explain','prove','decide','practice','close','appendix','transition'}

def experience_digest(handoff, state):
    """Bind outcome plan and review to current content/intent; not a signature or fact check."""
    payload = {k:handoff.get(k) for k in ('content_sha256','intent','experience_profile')}
    payload.update({k:state.get(k) for k in ('experience','quality_profile','slide_quality','review')})
    raw = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(',',':'), allow_nan=False)
    return hashlib.sha256(raw.encode('utf-8')).hexdigest()

def review_experience(slides, state, handoff=None):
    """Check outcome-plan completeness and consistency, never infer audience approval."""
    h = handoff if isinstance(handoff,dict) else {}
    st = state if isinstance(state,dict) else {}
    if not ('experience_profile' in h or 'experience_sha256' in h or 'experience' in st):
        return {'status':'not_applicable','issues':[]}
    issues = []
    def require_text(obj, keys, label):
        for k in keys:
            if not isinstance(obj,dict) or not text(obj.get(k)):
                issues.append(f'{label}: missing {k}')
    def known_ids(value):
        return strings(value) and bool(value) and len(value)==len(set(value)) and set(value)<=set(ids)
    ids = [s['slide_id'] for s in slides]
    if h.get('experience_profile') != EXPERIENCE_PROFILE:
        issues.append('invalid/missing experience_profile')
    e = st.get('experience')
    if not isinstance(e,dict):
        return {'status':'needs_revision','issues':issues+['missing experience object']}
    scene = e.get('scene')
    if not isinstance(scene,str) or scene not in SCENE_REQUIREMENTS:
        issues.append('invalid experience scene'); scene = 'general'
    secondary = e.get('secondary_scenes',[])
    if not strings(secondary) or any(x not in SCENE_REQUIREMENTS or x==scene for x in secondary) or len(set(secondary))!=len(secondary):
        issues.append('invalid secondary_scenes'); secondary=[]
    require_text(e.get('audience'), AUDIENCE_FIELDS, 'audience')
    require_text(e.get('outcome'), OUTCOME_FIELDS, 'outcome')
    require_text(e.get('opening'), OPENING_FIELDS, 'opening')
    journey = e.get('journey')
    if not isinstance(journey,dict):
        issues.append('journey must be an object'); journey={}
    if set(journey)!=set(ids): issues.append('journey ids differ from slides')
    core=[]
    for sid in ids:
        j=journey.get(sid)
        require_text(j,JOURNEY_FIELDS,f'{sid} journey')
        if not isinstance(j,dict): continue
        if j.get('beat') not in BEATS: issues.append(f'{sid}: invalid journey beat')
        if j.get('priority') not in ('core','deepening'): issues.append(f'{sid}: invalid journey priority')
        elif j['priority']=='core': core.append(sid)
    if not core: issues.append('short route must retain at least one core slide')
    checks=e.get('scene_checks')
    if not isinstance(checks,dict):
        issues.append('scene_checks must be object'); checks={}
    needed={f'{sc}.{k}' for sc in [scene]+secondary for k in SCENE_REQUIREMENTS[sc]}
    if set(checks)!=needed: issues.append('scene_checks keys differ from required scene checklist')
    for key in sorted(needed):
        c=checks.get(key)
        require_text(c,('basis','gap_action'),key)
        if not isinstance(c,dict):continue
        if c.get('status') not in ('covered','proposed','unresolved'):
            issues.append(f'{key}: invalid scene check status')
        elif c['status']=='unresolved': issues.append(f'{key}: unresolved scene check')
        links=c.get('slide_ids')
        if not known_ids(links):
            issues.append(f'{key}: missing/invalid slide_ids')
        elif not set(links).intersection(core):
            issues.append(f'{key}: short route loses scene checkpoint')
    short=e.get('short_route')
    require_text(short,('basis',),'short_route')
    if isinstance(short,dict):
        if short.get('slide_ids')!=core: issues.append('short_route must retain ordered core slide ids')
        expected=sum(s['notes'].get('minutes',0) for s in slides if s['slide_id'] in core)
        if not positive(short.get('minutes')) or abs(short['minutes']-expected)>1e-8:
            issues.append('short_route minutes must equal sum of core slide notes')
        if short.get('mode')!=('same' if core==ids else 'compressed'):
            issues.append('short_route mode inconsistent with retained slides')
    qa=e.get('qa')
    if not isinstance(qa,list) or not qa:
        issues.append('qa must include at least one anticipated question')
    else:
        for i,q in enumerate(qa):
            require_text(q,('question','response','boundary'),f'qa[{i}]')
            if not isinstance(q,dict) or not known_ids(q.get('slide_ids')):
                issues.append(f'qa[{i}]: invalid slide_ids')
    gates=e.get('rehearsal')
    for k in REHEARSAL_FIELDS:
        g=gates.get(k) if isinstance(gates,dict) else None
        require_text(g,('basis',),f'rehearsal {k}')
        if not isinstance(g,dict) or g.get('result') not in ('pass','revise','not_applicable'):
            issues.append(f'rehearsal {k}: invalid result')
        elif g['result']=='revise':
            issues.append(f'rehearsal {k}: needs revision')
    if review_slide_quality(slides,st)['status']!='reviewed':
        issues.append('audience journey requires completed per-slide content review')
    return {'status':'needs_revision' if issues else 'reviewed','issues':issues,
            'scene':scene,'secondary_scenes':secondary,'core_slide_ids':core,
            'short_minutes':sum(s['notes'].get('minutes',0) for s in slides if s['slide_id'] in core),
            'scope':'mechanical outcome-plan review; audience response not observed'}

def check_experience_binding(slides, handoff, state, status, errors):
    declared = 'experience_profile' in handoff or 'experience_sha256' in handoff or (isinstance(state,dict) and 'experience' in state)
    if not declared: return
    if handoff.get('experience_profile')!=EXPERIENCE_PROFILE:
        errors.append('invalid/missing experience_profile')
    sealed=handoff.get('experience_sha256')
    if not isinstance(sealed,str) or not re.fullmatch(r'[0-9a-f]{64}',sealed):
        errors.append('missing/invalid experience_sha256')
    if state is None: return  # existing missing-state gate handles safe preview
    if sealed!=experience_digest(handoff,state):
        errors.append('experience_sha256 stale; revise and reseal outcome plan')
    quality=review_experience(slides,state,handoff)
    if status=='READY' and quality['status']!='reviewed':
        errors.extend(quality['issues'])


def validate(md_path,handoff_path,state_path=None):
    meta,slides,errors=parse(md_path); h=load_json(handoff_path); state=load_json(state_path) if state_path else None
    if not isinstance(h,dict) or (state is not None and not isinstance(state,dict)): raise ValueError('handoff/state must be objects')
    status=meta.get('status'); readiness=h.get('readiness'); ids=[s['slide_id'] for s in slides]
    if h.get('content_file')!=Path(md_path).name or not text(h.get('target_renderer')): errors.append('invalid content_file or target_renderer')
    if readiness not in ('ready','needs_review','blocked') or (status=='READY')!=(readiness=='ready'): errors.append('presentation status/readiness mismatch')
    if not strings(h.get('unresolved')): errors.append('handoff unresolved must be an array of strings')
    listed=h.get('slides')
    if not isinstance(listed,list) or any(not isinstance(s,dict) for s in listed): errors.append('handoff slides must be object array'); listed=[]
    if ids!=[s.get('slide_id') for s in listed]: errors.append('handoff slide order differs')
    for a,b in zip(slides,listed):
        for k in ('title','role','visual_intent','chapter'):
            if a[k]!=b.get(k): errors.append(f'{a["slide_id"]}: handoff {k} differs')
        if b.get('speaker_notes_present') is not True: errors.append(f'{a["slide_id"]}: speaker_notes_present must be true')
    if state is None: errors.append('working-state.json required for formal handoff')
    if state is not None:
        if STAGE_STATUS.get(state.get('stage'))!=status: errors.append('stage/status mismatch')
        if not strings(state.get('open_questions')): errors.append('open_questions must be an array of strings')
    if status=='READY':
        if h.get('unresolved'): errors.append('READY requires empty handoff unresolved')
        if state and state.get('open_questions'): errors.append('READY requires empty working-state open_questions')
    rev=h.get('revision')
    if type(rev) is not int or rev<1 or h.get('content_sha256')!=digest(md_path): errors.append('revision or content_sha256 invalid/stale; seal current revision')
    intent=h.get('intent')
    for k in ('scene','primary_audience','current_belief','desired_belief','desired_action','success_signal'):
        if not isinstance(intent,dict) or not text(intent.get(k)): errors.append(f'intent missing {k}')
    if state is not None:
        if state.get('revision')!=rev: errors.append('state/handoff revision mismatch')
        if state.get('open_questions')!=h.get('unresolved'): errors.append('state open_questions / handoff unresolved mismatch')
        for k,typ in [('confirmed',dict),('assumptions',list),('decision_log',list),('slide_maturity',dict)]:
            if not isinstance(state.get(k),typ): errors.append(f'invalid state {k}')
        if isinstance(state.get('slide_maturity'),dict) and set(state['slide_maturity'])!=set(ids): errors.append('slide_maturity ids differ')
        if not strings(state.get('limitations')): errors.append('limitations must be string array')
        review=state.get('review',{})
        for k in GATES:
            gate=review.get(k,{}) if isinstance(review,dict) else {}
            if not isinstance(gate,dict) or gate.get('result') not in ('pass','revise','not_applicable') or not text(gate.get('basis')): errors.append(f'invalid review gate {k}')
            elif status=='READY' and gate['result']=='revise': errors.append(f'READY review gate {k} needs revision')
    check_sources(Path(md_path).parent,slides,errors)
    if state is not None and (status=='READY' or 'quality_profile' in state or 'slide_quality' in state):
        quality=review_slide_quality(slides,state)
        if status=='READY' and quality['status']!='reviewed':
            errors.extend(quality['issues'])
    check_experience_binding(slides,h,state,status,errors)
    return {'ok':not errors,'slides':len(slides),'planned_minutes':sum(s['notes'].get('minutes',0) for s in slides),'status':status,'readiness':readiness,'errors':errors,'gate_scope':'mechanical only; evidence, audience fit, disclosure and rendering require review'}


def check_sources(root,slides,errors):
    try:
        ledger=(root/'sources.md').read_text(encoding='utf-8'); outline=(root/'outline.md').read_text(encoding='utf-8'); claims=load_json(root/'claim-map.json')
    except (OSError,ValueError) as e: errors.append(f'missing/invalid supporting files: {e}'); return
    if not outline.strip() or not ledger.strip(): errors.append('outline/sources must be nonempty')
    entries=re.findall(r'^- \[(E-[A-Za-z0-9-]+)\]\s+([a-z_]+):\s*(.+)$',ledger,re.M)
    keys=[e[0] for e in entries]; states={e[0]:e[1] for e in entries}
    declared=re.findall(r'^- \[(E-[A-Za-z0-9-]+)\]',ledger,re.M)
    if len(keys)!=len(set(keys)): errors.append('duplicate evidence ids')
    if keys!=declared or any(st not in CLAIM_STATES or not desc.strip() for _,st,desc in entries): errors.append('invalid evidence entry/status in sources.md')
    known=set(keys); ids={s['slide_id'] for s in slides}; coverage=set(); cids=set(); mapping={s['slide_id']:set(EID.findall(s['evidence'])) for s in slides}
    for sid,refs in mapping.items():
        if not refs<=known: errors.append(f'{sid}: unknown Evidence id {sorted(refs-known)}')
    main=claims.get('main_claim') if isinstance(claims,dict) else None
    if not isinstance(main,dict) or not text(main.get('text')) or main.get('status') not in CLAIM_STATES: errors.append('invalid main_claim')
    items=claims.get('claims') if isinstance(claims,dict) else None
    if not isinstance(items,list): errors.append('claims must be array'); return
    for c in items:
        if not isinstance(c,dict) or not text(c.get('id')) or not text(c.get('text')) or c.get('status') not in CLAIM_STATES: errors.append('invalid claim'); continue
        cid=c['id']; refs=c.get('evidence_ids'); links=c.get('slides')
        if cid in cids: errors.append(f'duplicate claim {cid}')
        cids.add(cid)
        if not strings(links) or not links or not set(links)<=ids or not strings(refs) or not set(refs)<=known: errors.append(f'{cid}: invalid slide/evidence mapping'); continue
        if c['status'] in ('verified','qualified','user_reported') and not refs: errors.append(f'{cid}: fact claim needs source id')
        if c['status'] in ('verified','qualified','user_reported') and refs:
            allowable={'verified':{'verified'},'qualified':{'verified','qualified'},'user_reported':{'user_reported','verified','qualified'}}[c['status']]
            if not any(states[r] in allowable for r in refs): errors.append(f'{cid}: no evidence source status supports factual claim')
        for sid in links:
            if not set(refs)<=mapping[sid]: errors.append(f'{cid}/{sid}: mapped evidence missing from slide')
        coverage.update(links)
    for s in slides:
        if s['role'] not in ('COVER','AGENDA','CTA','APPENDIX') and s['slide_id'] not in coverage: errors.append(f'{s["slide_id"]}: no claim mapping')
