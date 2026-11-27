import unittest, tempfile, shutil, json, hashlib
from pathlib import Path
from evaluate_effectiveness import evaluate
class Effectiveness(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.d=Path(self.tmp.name)/'demo'
        shutil.copytree(Path(__file__).resolve().parents[1]/'examples/risk-change',self.d)
        self.md=self.d/'presentation.md';self.h=self.d/'handoff.json';self.p=self.d/'effectiveness-plan.json';self.o=self.d/'effectiveness-observations.rehearsal.json'
    def tearDown(self):self.tmp.cleanup()
    def run_eval(self,obs=None):return evaluate(self.md,self.h,self.p,obs)
    def edit(self,p,fn):
        obj=json.loads(p.read_text());fn(obj);p.write_text(json.dumps(obj))
    def test_unknown(self):
        r=self.run_eval();self.assertEqual(r['assessed_count'],0);self.assertFalse(r['actual_effect_assessed'])
    def test_rehearsal(self):
        r=self.run_eval(self.o);self.assertEqual(r['dimensions']['understanding'],'partial');self.assertFalse(r['actual_effect_assessed'])
    def test_wrong_revision(self):
        self.edit(self.p,lambda x:x.update(revision=99))
        with self.assertRaises(ValueError):self.run_eval()
    def test_wrong_anchor(self):
        self.edit(self.p,lambda x:x['dimensions']['insight'].update(slide_ids=['fake']))
        with self.assertRaises(ValueError):self.run_eval()
    def test_stale_observation(self):
        self.edit(self.p,lambda x:x['dimensions']['insight'].update(criterion='changed'))
        with self.assertRaises(ValueError):self.run_eval(self.o)
    def test_duplicate(self):
        self.edit(self.o,lambda x:x['records'].append(x['records'][0]))
        with self.assertRaises(ValueError):self.run_eval(self.o)
    def test_actual_record(self):
        self.edit(self.o,lambda x:x.update(mode='actual'))
        self.assertTrue(self.run_eval(self.o)['actual_effect_assessed']) # structural test only
    def test_no_applicable(self):
        self.edit(self.p,lambda x:[v.update(applicable=False) for v in x['dimensions'].values()])
        with self.assertRaises(ValueError):self.run_eval()
    def test_wrong_seal(self):
        self.edit(self.p,lambda x:x.update(experience_sha256='bad'))
        with self.assertRaises(ValueError):self.run_eval()
    def test_base_plan_without_experience(self):
        original=Path(__file__).resolve().parents[1]/'examples'
        for name in ('presentation.md','handoff.json','working-state.json','outline.md','claim-map.json','sources.md'):
            shutil.copyfile(original/name,self.d/name)
        hand=json.loads(self.h.read_text())
        def convert(obj):
            obj.pop('experience_sha256')
            obj.update(content_sha256=hand['content_sha256'],revision=hand['revision'],
                       handoff_sha256=hashlib.sha256(self.h.read_bytes()).hexdigest(),
                       state_sha256=hashlib.sha256((self.d/'working-state.json').read_bytes()).hexdigest())
            for d in obj['dimensions'].values():
                if d['applicable']: d['slide_ids']=['validation']
        self.edit(self.p,convert)
        self.assertEqual(self.run_eval()['mode'],'unobserved')
        self.assertFalse(self.run_eval()['actual_effect_assessed'])
        self.edit(self.h,lambda x:x['intent'].update(success_signal='changed'))
        with self.assertRaisesRegex(ValueError,'base plan handoff hash mismatch'):self.run_eval()
    def test_invalid_date(self):
        self.edit(self.o,lambda x:x['records'][0].update(observed_at='2026-02-30'))
        with self.assertRaises(ValueError):self.run_eval(self.o)
if __name__=='__main__':unittest.main()
