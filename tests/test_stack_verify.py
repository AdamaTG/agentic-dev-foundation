import json
from pathlib import Path
import tempfile
import unittest
from tools.stack_verify import verify, ROOT

class StackRunnerTests(unittest.TestCase):
    def test_all_configs_have_expected_stages(self):
        for name in ('next-fastapi','expo','flutter'):
            c=json.loads((ROOT/'config'/'stacks'/(name+'.json')).read_text())
            self.assertEqual(list(c['checks']),['lint','typecheck','unit','integration','e2e'])
    def test_fake_stack_pass_and_evidence(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            path=Path(d)
            relative=str(path.relative_to(ROOT))
            conf={'schema_version':1,'stack':'expo','project_directory':relative,
                  'profiles':{'full':['unit']},'checks':{'unit':{
                   'command':['python','-c','from pathlib import Path; Path("proof.txt").write_text("observed"); print("ok")'],'directory':relative,'timeout_seconds':10,'artifacts':['proof.txt']}}}
            cfg=path/'cfg.json';out=path/'report.json';cfg.write_text(json.dumps(conf))
            self.assertEqual(verify('expo','full',cfg,out),0)
            result=json.loads(out.read_text())
            self.assertEqual(result['results'][0]['status'],'passed')
            self.assertEqual(len(result['results'][0]['artifacts']),1)
    def test_missing_binary_not_success(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            path=Path(d);relative=str(path.relative_to(ROOT))
            conf={'schema_version':1,'stack':'expo','project_directory':relative,
                  'profiles':{'full':['unit']},'checks':{'unit':{'command':['adf-nonexistent-xyz-987'],
                  'timeout_seconds':5}}}
            cfg=path/'cfg.json';out=path/'report.json';cfg.write_text(json.dumps(conf))
            self.assertEqual(verify('expo','full',cfg,out),3)
            self.assertEqual(json.loads(out.read_text())['results'][0]['status'],'unavailable')
    def test_missing_project_rejected(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            path=Path(d);conf={'schema_version':1,'stack':'expo','project_directory':'apps/nonexistent',
              'profiles':{'full':['lint']},'checks':{'lint':{'command':['python'],'timeout_seconds':4}}}
            cfg=path/'c.json';cfg.write_text(json.dumps(conf))
            self.assertEqual(verify('expo','full',cfg,path/'o.json'),2)
    def test_failed_command_is_not_pass(self):
        with tempfile.TemporaryDirectory(dir=ROOT) as d:
            path=Path(d);relative=str(path.relative_to(ROOT))
            conf={'schema_version':1,'stack':'expo','project_directory':relative,
              'profiles':{'full':['lint']},'checks':{'lint':{'command':['python','-c','import sys;sys.exit(7)'],'timeout_seconds':4}}}
            cfg=path/'c.json';cfg.write_text(json.dumps(conf))
            self.assertEqual(verify('expo','full',cfg,path/'o.json'),1)

if __name__=='__main__':unittest.main()
