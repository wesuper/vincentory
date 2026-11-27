"""Audience journey extension: mechanical regression, not a simulation of real audience response."""
import copy, json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
from content_contract import parse, validate, review_experience, experience_digest, SCENE_REQUIREMENTS, EXPERIENCE_PROFILE
ROOT=Path(__file__).resolve().parents[1]
DEMO=ROOT/'examples/risk-change'
class AudienceJourney(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.root=Path(self.tmp.name)/'demo'
        shutil.copytree(DEMO,self.root)
        self.md=self.root/'presentation.md'; self.h=self.root/'handoff.json'; self.s=self.root/'working-state.json'
        self.hd=json.loads(self.h.read_text()); self.st=json.loads(self.s.read_text())
        _,self.slides,errors=parse(self.md); self.assertFalse(errors)
    def tearDown(self): self.tmp.cleanup()
    def put(self, reseal=True):
        if reseal:self.hd['experience_sha256']=experience_digest(self.hd,self.st)
        self.h.write_text(json.dumps(self.hd,ensure_ascii=False))
        self.s.write_text(json.dumps(self.st,ensure_ascii=False))
    def runseal(self):
        return subprocess.run([sys.executable,'-S',str(ROOT/'scripts/validate_content.py'),str(self.md),str(self.h),str(self.s),'--seal'],capture_output=True,text=True)
    def test_ready_fixture(self): self.assertTrue(validate(self.md,self.h,self.s)['ok'])
    def test_all_scene_enum_requirements(self):
        for scene,keys in SCENE_REQUIREMENTS.items():
            with self.subTest(scene=scene):
                st=copy.deepcopy(self.st); e=st['experience']; e['scene']=scene;e['secondary_scenes']=[]
                e['scene_checks']={scene+'.'+key:{'status':'proposed','basis':'synthetic structural test only','gap_action':'validate with actual material','slide_ids':['decision']} for key in keys}
                self.assertEqual(review_experience(self.slides,st,self.hd)['status'],'reviewed')
                e['scene_checks'].pop(scene+'.'+keys[0])
                self.assertEqual(review_experience(self.slides,st,self.hd)['status'],'needs_revision')
    def test_missing_checkpoint(self):
        self.st['experience']['scene_checks'].pop('risk_change.go_no_go_rollback'); self.put()
        self.assertFalse(validate(self.md,self.h,self.s)['ok'])
    def test_unresolved(self):
        self.st['experience']['scene_checks']['risk_change.go_no_go_rollback']['status']='unresolved'; self.put()
        self.assertFalse(validate(self.md,self.h,self.s)['ok'])
    def test_core_checkpoint_only_deepening_fails(self):
        self.st['experience']['scene_checks']['risk_change.go_no_go_rollback']['slide_ids']=['mechanism']; self.put()
        self.assertFalse(validate(self.md,self.h,self.s)['ok'])
    def test_route_order_and_time(self):
        for key,value in [('slide_ids',['next','decision','delta','controls']),('minutes',0),('mode','same')]:
            with self.subTest(key=key):
                st=copy.deepcopy(self.st); st['experience']['short_route'][key]=value
                self.assertEqual(review_experience(self.slides,st,self.hd)['status'],'needs_revision')
    def test_missing_journey(self):
        self.st['experience']['journey'].pop('delta');self.put()
        self.assertFalse(validate(self.md,self.h,self.s)['ok'])
    def test_invalid_qa_anchor(self):
        self.st['experience']['qa'][0]['slide_ids']=['does-not-exist'];self.put()
        self.assertFalse(validate(self.md,self.h,self.s)['ok'])
    def test_failed_rehearsal(self):
        self.st['experience']['rehearsal']['synchrony']['result']='revise';self.put()
        self.assertFalse(validate(self.md,self.h,self.s)['ok'])
    def test_stale_outcome_metadata(self):
        self.st['experience']['outcome']['recall']='changed';self.put(False)
        self.assertFalse(validate(self.md,self.h,self.s)['ok'])
    def test_changed_outcome_requires_revision_and_atomic_seal(self):
        old=self.h.read_bytes()
        self.st['experience']['outcome']['recall']='changed'
        self.s.write_text(json.dumps(self.st,ensure_ascii=False))
        r=self.runseal(); self.assertNotEqual(r.returncode,0);self.assertEqual(self.h.read_bytes(),old)
        self.st['revision']+=1;self.s.write_text(json.dumps(self.st,ensure_ascii=False))
        r=self.runseal();self.assertEqual(r.returncode,0,r.stdout+r.stderr)
    def test_invalid_gate_does_not_replace_sealed_handoff(self):
        old=self.h.read_bytes();self.st['revision']+=1
        self.st['experience']['rehearsal']['action']['result']='revise'
        self.s.write_text(json.dumps(self.st,ensure_ascii=False))
        r=self.runseal();self.assertNotEqual(r.returncode,0);self.assertEqual(self.h.read_bytes(),old)
    def test_duplicate_secondary_scene(self):
        self.st['experience']['secondary_scenes']=['risk_change']; self.put()
        self.assertFalse(validate(self.md,self.h,self.s)['ok'])
    def test_base_without_extension_is_valid(self):
        self.st.pop('experience'); self.hd.pop('experience_profile'); self.hd.pop('experience_sha256');self.put(False)
        self.assertTrue(validate(self.md,self.h,self.s)['ok'])
        self.assertEqual(review_experience(self.slides,self.st,self.hd)['status'],'not_applicable')
if __name__=='__main__':unittest.main()
