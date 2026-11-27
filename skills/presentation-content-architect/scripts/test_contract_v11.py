"""Regression tests for 1.1 gate, using shipped synthetic fixture. Stdlib only."""
import copy, json, shutil, subprocess, sys, tempfile, unittest
from pathlib import Path
from content_contract import validate,digest

EXAMPLE=Path(__file__).resolve().parents[1]/'examples'
CLI=Path(__file__).with_name('validate_content.py')
class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)/'example';shutil.copytree(EXAMPLE,self.root)
        self.md=self.root/'presentation.md'; self.h=self.root/'handoff.json'; self.s=self.root/'working-state.json'
    def tearDown(self):self.tmp.cleanup()
    def change(self,p,fn):
        obj=json.loads(p.read_text());fn(obj);p.write_text(json.dumps(obj,ensure_ascii=False))
    def valid(self):return validate(self.md,self.h,self.s)
    def reseal(self):self.change(self.h,lambda h:h.update(content_sha256=digest(self.md)))

class Contract11(Fixture):
    def test_ready(self):self.assertTrue(self.valid()['ok'])
    def test_stale(self):
        self.md.write_text(self.md.read_text()+'\n');self.assertFalse(self.valid()['ok'])
    def test_conflicting_title(self):
        self.change(self.h,lambda h:h['slides'][0].update(title='altered'));self.assertFalse(self.valid()['ok'])
    def test_revision(self):
        self.change(self.s,lambda s:s.update(revision=999));self.assertFalse(self.valid()['ok'])
    def test_missing_evidence(self):
        self.change(self.root/'claim-map.json',lambda c:c['claims'][0].update(evidence_ids=['E-NOT-THERE']));self.assertFalse(self.valid()['ok'])
    def test_false_claim_promotion(self):
        self.change(self.root/'claim-map.json',lambda c:c['claims'][0].update(status='verified'));self.assertFalse(self.valid()['ok'])
    def test_failed_review(self):
        self.change(self.s,lambda s:s['review']['objections'].update(result='revise'));self.assertFalse(self.valid()['ok'])
    def test_zero_minutes(self):
        self.md.write_text(self.md.read_text().replace('Minutes: 1.2','Minutes: 0'));self.reseal();self.assertFalse(self.valid()['ok'])
    def test_nan_duration(self):
        self.md.write_text(self.md.read_text().replace('duration_minutes: 5','duration_minutes: NaN'));self.reseal();self.assertFalse(self.valid()['ok'])
    def test_over_budget(self):
        self.md.write_text(self.md.read_text().replace('Minutes: 1.2','Minutes: 3'));self.reseal();self.assertFalse(self.valid()['ok'])
    def test_blocked_valid_preview_state(self):
        self.md.write_text(self.md.read_text().replace('status: READY','status: REVIEW'));self.reseal()
        self.change(self.h,lambda h:h.update(readiness='blocked',unresolved=['权限待确认']));self.change(self.s,lambda s:s.update(stage='REVIEW',open_questions=['权限待确认']));self.assertTrue(self.valid()['ok'],self.valid())
    def test_inline_talk_fails(self):
        self.md.write_text(self.md.read_text().replace('Talk:\n- ','Talk: ',1));self.reseal();self.assertFalse(self.valid()['ok'])
    def test_malformed_id(self):
        self.md.write_text(self.md.read_text().replace('slide:id=problem ','slide:id=bad_id '));self.reseal();self.assertFalse(self.valid()['ok'])
    def test_quality_missing_record_fails(self):
        self.change(self.s,lambda s:s['slide_quality'].pop('validation'))
        self.assertFalse(self.valid()['ok'])
    def test_quality_revise_fails(self):
        self.change(self.s,lambda s:s['slide_quality']['validation'].update(result='revise'))
        self.assertFalse(self.valid()['ok'])
    def test_quality_missing_basis_fails(self):
        self.change(self.s,lambda s:s['slide_quality']['validation'].update(basis=''))
        self.assertFalse(self.valid()['ok'])
    def test_legacy_without_quality_can_parse(self):
        def remove(s):
            s.pop('quality_profile');s.pop('slide_quality')
        self.change(self.s,remove)
        self.assertTrue(self.valid()['ok'])
    def test_quality_placeholder_fails(self):
        raw=self.md.read_text()
        before,after=raw.split('## Visible',1)
        _,tail=after.split('## Evidence',1)
        self.md.write_text(before+'## Visible\n- 待补充\n## Evidence'+tail)
        self.reseal();self.assertFalse(self.valid()['ok'])
    def test_quality_repeated_takeaway_fails(self):
        raw=self.md.read_text()
        title=raw.split('\n# ',1)[1].split('\n',1)[0]
        raw=raw.replace('> Takeaway: 目前没有真实内部基线，因此不能预先承诺效率收益。（合成示例）','> Takeaway: '+title)
        self.md.write_text(raw);self.reseal();self.assertFalse(self.valid()['ok'])

class Seal(Fixture):
    """--seal must not lose the 'content change needs a new revision' guard."""
    TAMPER=('不能预先承诺效率收益','可承诺效率收益')
    def seal(self):
        r=subprocess.run([sys.executable,str(CLI),str(self.md),str(self.h),str(self.s),'--seal'],capture_output=True,text=True)
        self.assertTrue(r.stdout,r.stderr); return json.loads(r.stdout),r.returncode
    def tamper(self):
        raw=self.md.read_text(); self.assertIn(self.TAMPER[0],raw)
        self.md.write_text(raw.replace(*self.TAMPER))
    def test_reseal_unchanged_content_passes(self):
        result,code=self.seal(); self.assertEqual(code,0,result['errors'])
        self.assertEqual(json.loads(self.h.read_text())['content_sha256'],digest(self.md))
    def test_tamper_without_revision_bump_fails(self):
        self.tamper(); result,code=self.seal()
        self.assertEqual(code,1)
        self.assertTrue(any('incremented revision' in e for e in result['errors']),result)
    def test_deleting_hash_does_not_skip_guard(self):
        self.tamper(); self.change(self.h,lambda h:h.pop('content_sha256'))
        result,code=self.seal()
        self.assertEqual(code,1)
        self.assertTrue(any('missing at revision' in e for e in result['errors']),result)
    def test_revision_cannot_decrease(self):
        self.change(self.h,lambda h:h.update(revision=9)); self.change(self.s,lambda s:s.update(revision=4))
        result,code=self.seal()
        self.assertEqual(code,1)
        self.assertTrue(any('cannot decrease' in e for e in result['errors']),result)
    def test_tamper_with_bumped_revisions_then_reseal(self):
        self.tamper()
        self.change(self.h,lambda h:h.update(revision=3)); self.change(self.s,lambda s:s.update(revision=3))
        result,code=self.seal()
        self.assertEqual(code,1,result)
        self.assertTrue(any('incremented revision' in e for e in result['errors']),result)
        # The documented path: revise content, resolve gates, then bump and seal once.
        self.change(self.s,lambda s:s.update(revision=4))
        result,code=self.seal()
        self.assertEqual(code,0,result['errors'])
        self.assertEqual(json.loads(self.h.read_text())['revision'],4)

if __name__=='__main__':unittest.main()
