#!/usr/bin/env python3
"""Usage: validate_content.py presentation.md handoff.json [working-state.json] [--seal]."""
import argparse
import json
import re
from pathlib import Path
from content_contract import validate, digest, load_json


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('presentation'); p.add_argument('handoff'); p.add_argument('state',nargs='?'); p.add_argument('--seal',action='store_true'); a=p.parse_args()
    try:
        if a.seal:
            h=load_json(a.handoff)
            if h.get('contract_version')!='1.1' or not a.state: raise ValueError('--seal requires 1.1 and working-state.json')
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
            h.update(revision=state['revision'],content_sha256=current)
            Path(a.handoff).write_text(json.dumps(h,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        result=validate(a.presentation,a.handoff,a.state)
    except (OSError,ValueError,TypeError,KeyError,AttributeError) as e: result={'ok':False,'errors':[str(e)]}
    print(json.dumps(result,ensure_ascii=False,indent=2)); return 0 if result['ok'] else 1

if __name__=='__main__': raise SystemExit(main())
