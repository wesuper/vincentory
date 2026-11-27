#!/usr/bin/env python3
"""Usage: validate_content.py presentation.md handoff.json [working-state.json] [--seal]."""
import argparse
import json
import re
import tempfile
import os
from pathlib import Path
from content_contract import validate, digest, load_json, EXPERIENCE_PROFILE, experience_digest


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('presentation'); p.add_argument('handoff'); p.add_argument('state',nargs='?'); p.add_argument('--seal',action='store_true'); a=p.parse_args()
    try:
        if a.seal:
            h=load_json(a.handoff)
            if not a.state: raise ValueError('--seal requires working-state.json')
            state=load_json(a.state)
            if type(state.get('revision')) is not int or state['revision']<1: raise ValueError('state revision must be positive integer')
            current=digest(a.presentation); sealed=h.get('content_sha256'); previous=h.get('revision')
            if previous is not None and type(previous) is not int: raise ValueError('handoff revision must be an integer')
            if sealed is not None and not (isinstance(sealed,str) and re.fullmatch(r'[0-9a-f]{64}',sealed)):
                raise ValueError('handoff content_sha256 must be 64 lowercase hex chars')
            # A missing hash is the first seal only. Without a prior hash there is
            # nothing to compare against, so deleting it would let any edit pass.
            if sealed is None and state['revision']>1:
                raise ValueError('handoff content_sha256 missing at revision >1: restore the sealed hash before resealing')
            if sealed and sealed!=current and not (type(previous) is int and state['revision']>previous):
                raise ValueError('changed content requires incremented revision before sealing')
            if type(previous) is int and state['revision']<previous:
                raise ValueError('revision cannot decrease')
            old_experience=h.get('experience_sha256')
            h.update(revision=state['revision'],content_sha256=current)
            if 'experience' in state or 'experience_profile' in h or 'experience_sha256' in h:
                if 'experience' not in state: raise ValueError('cannot seal declared audience journey without experience')
                h['experience_profile']=EXPERIENCE_PROFILE
                new_experience=experience_digest(h,state)
                if old_experience is not None and (not isinstance(old_experience,str) or not re.fullmatch(r'[0-9a-f]{64}',old_experience)):
                    raise ValueError('invalid previous experience_sha256')
                if old_experience!=new_experience and type(previous) is int and sealed and state['revision']<=previous:
                    raise ValueError('changed/added outcome plan requires incremented revision before sealing')
                h['experience_sha256']=new_experience
            dest=Path(a.handoff)
            fd,temp=tempfile.mkstemp(prefix='.handoff-',suffix='.json',dir=dest.parent)
            try:
                with os.fdopen(fd,'w',encoding='utf-8') as f:
                    f.write(json.dumps(h,ensure_ascii=False,indent=2)+'\n')
                result=validate(a.presentation,temp,a.state)
                if result['ok']: os.replace(temp,dest)
            finally:
                if Path(temp).exists(): Path(temp).unlink()
        else:
            result=validate(a.presentation,a.handoff,a.state)
    except (OSError,ValueError,TypeError,KeyError,AttributeError) as e: result={'ok':False,'errors':[str(e)]}
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if result['ok'] else 1

if __name__=='__main__': raise SystemExit(main())
