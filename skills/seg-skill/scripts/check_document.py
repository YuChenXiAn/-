#!/usr/bin/env python3
"""Check document syntax/contract invariants; not an algorithm accuracy test."""
import argparse, difflib, hashlib, json, re
from pathlib import Path

def check(path, forbidden):
    s=Path(path).read_text(encoding='utf-8'); errors=[]
    for term in forbidden:
        if term in s: errors.append('Removed term remains: '+term)
    blocks=re.findall(r'```json\s*\n(.*?)\n```',s,re.S)
    if not blocks: errors.append('No JSON examples found')
    for i,b in enumerate(blocks,1):
        try: d=json.loads(b)
        except json.JSONDecodeError as e:
            errors.append(f'JSON {i}: {e}'); continue
        if not isinstance(d,dict): continue
        a=d.get('algorithm_data')
        if not isinstance(a,dict): continue
        if 'config' in a: errors.append(f'JSON {i}: nested config remains')
        for k,v in a.items():
            if isinstance(v,dict): errors.append(f'JSON {i}: dictionary value in {k}')
        targets=a.get('target_info')
        if isinstance(targets,list):
            if a.get('target_count')!=len(targets): errors.append(f'JSON {i}: target_count mismatch')
            if a.get('is_alert')!=bool(targets): errors.append(f'JSON {i}: is_alert mismatch')
    return {'json_blocks':len(blocks),'errors':errors}

def main():
    p=argparse.ArgumentParser();p.add_argument('file',nargs='?');p.add_argument('--forbid',nargs='*',default=[]);p.add_argument('--compare',nargs=2)
    a=p.parse_args()
    if a.compare:
        x,y=(Path(v).read_bytes() for v in a.compare)
        out={'identical_bytes':x==y,'sha256':[hashlib.sha256(v).hexdigest() for v in (x,y)],'diff_lines':len(list(difflib.unified_diff(x.decode().splitlines(),y.decode().splitlines())))}
        print(json.dumps(out,ensure_ascii=False,indent=2))
    if a.file:
        out=check(a.file,a.forbid);print(json.dumps(out,ensure_ascii=False,indent=2));return bool(out['errors'])
    if not a.compare:p.error('Provide file or --compare ORIGINAL FINAL')
    return 0
if __name__=='__main__':raise SystemExit(main())
