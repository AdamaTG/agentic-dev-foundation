"""Runner stack ADF: subprocess without shell, Windows/Linux, evidence manifests."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
STAGES = ('lint', 'typecheck', 'unit', 'integration', 'e2e')

def verify(stack, profile='full', config=None, output=None):
    config = config or ROOT / 'config' / 'stacks' / (stack + '.json')
    output = output or ROOT / 'reports' / ('stack-' + stack + '.json')
    try:
        data = json.loads(config.read_text(encoding='utf-8'))
        if data.get('schema_version') != 1 or data.get('stack') != stack:
            raise ValueError('stack/schema mismatch')
        project = (ROOT / data['project_directory']).resolve()
        if not project.is_relative_to(ROOT) or not project.is_dir():
            raise ValueError('Missing or unsafe project directory: ' + str(project))
        names = data['profiles'][profile]
        if not names or not isinstance(names,list) or any(n not in STAGES for n in names) or len(set(names)) != len(names):
            raise ValueError('Invalid stage list')
        checks = []
        for name in names:
            entry=data['checks'][name]
            cwd=(ROOT / entry.get('directory',data['project_directory'])).resolve()
            if not cwd.is_relative_to(ROOT) or not cwd.is_dir():
                raise ValueError('Missing/unsafe working directory: '+str(cwd))
            cmd=entry['command']
            if not isinstance(cmd,list) or not cmd or any(not isinstance(x,str) or not x for x in cmd):
                raise ValueError('Invalid command for '+name)
            timeout=entry['timeout_seconds']
            if not isinstance(timeout,int) or timeout < 1 or timeout > 3600:
                raise ValueError('Invalid timeout')
            artifacts=entry.get('artifacts',[])
            if not isinstance(artifacts,list) or any(not isinstance(x,str) or not x or '..' in Path(x).parts or Path(x).is_absolute() for x in artifacts):
                raise ValueError('Unsafe artifacts')
            checks.append((name,cwd,cmd,timeout,artifacts))
    except (OSError,ValueError,KeyError,TypeError,IndexError) as exc:
        print('CONFIG ERROR:',exc,file=sys.stderr)
        return 2
    # Never claim old artifacts from prior runs.
    evidence_root=ROOT/'evidence'/'stacks'/stack
    if evidence_root.exists():
        shutil.rmtree(evidence_root)
    evidence_root.mkdir(parents=True,exist_ok=True)
    results=[]
    overall=0
    for name,cwd,cmd,timeout,artifacts in checks:
        started=time.monotonic()
        wall_started=time.time()
        try:
            p=subprocess.run(cmd,cwd=cwd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                             text=True,encoding='utf-8',errors='replace',timeout=timeout,shell=False)
            status='passed' if p.returncode==0 else 'failed'
            code=p.returncode
            stdout,stderr=p.stdout,p.stderr
            if code!=0 and overall==0:overall=1
        except subprocess.TimeoutExpired as exc:
            status='timeout';code=None;stdout=str(exc.stdout or '');stderr=str(exc.stderr or '')
            overall=4
        except OSError as exc:
            status='unavailable';code=None;stdout='';stderr=str(exc)
            if overall!=4:overall=3
        # Collect only paths declared in config, without traversing symlinks/outside project.
        collected=[]
        for pattern in artifacts:
            for src in sorted(cwd.glob(pattern)):
                if not src.is_file() or src.is_symlink() or not src.resolve().is_relative_to(cwd):continue
                if src.stat().st_mtime < wall_started - 2:continue
                if src.stat().st_size > 15_000_000:continue
                relative=src.relative_to(cwd)
                target=evidence_root/name/relative
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(src,target)
                collected.append({'path':str(target.relative_to(ROOT)).replace('\\','/'),
                                  'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),
                                  'bytes':target.stat().st_size})
        results.append({'stage':name,'command':cmd,'cwd':str(cwd.relative_to(ROOT)).replace('\\','/'),
                        'status':status,'exit_code':code,'seconds':round(time.monotonic()-started,3),
                        'stdout':stdout[-12000:],'stderr':stderr[-12000:], 'artifacts':collected})
        print(f'[{status.upper()}] {stack}:{name} code={code} artifacts={len(collected)}')
    report={'schema_version':1,'stack':stack,'profile':profile,'created_at':datetime.now(timezone.utc).isoformat(),
            'exit_code':overall,'results':results,
            'limitations':['Passing commands cover only configured assertions; human review remains required.',
                           'Visual screenshots are evidence of execution, not automatically validated visual correctness.']}
    try:
        output.parent.mkdir(parents=True,exist_ok=True)
        output.write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
    except OSError as exc:
        print('REPORT ERROR',exc,file=sys.stderr);return 3
    print('Report:',output)
    return overall

if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--stack',choices=('next-fastapi','expo','flutter'),required=True)
    p.add_argument('--profile',choices=('quick','full','e2e'),default='full')
    p.add_argument('--config',type=Path)
    p.add_argument('--output',type=Path)
    a=p.parse_args()
    sys.exit(verify(a.stack,a.profile,a.config,a.output))
