"""Independent H5 pipeline regression (stdlib only), using bundled fixture."""
import copy,json,re,shutil,tempfile,unittest
from pathlib import Path
from prepare_render import prepare, THEMES
from render_reference import render
from verify_render import verify
from validate_deck import Report,check_structure,check_slides,parse_notes,check_notes,check_budget,check_placeholders,check_duplicate_ids,check_theme
from content_contract import digest
EXAMPLE=Path(__file__).resolve().parents[1]/'examples'
ROOT=Path(__file__).resolve().parents[1]
class Pipeline(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)/'fixture';shutil.copytree(EXAMPLE,self.root)
        self.md=self.root/'presentation.md';self.h=self.root/'handoff.json';self.state=self.root/'working-state.json'
        self.plan=prepare(self.md,self.h,self.state)
    def tearDown(self):self.temp.cleanup()
    def structural(self,html,theme='dune',profile='adaptive'):
        rep=Report();check_structure(html,rep,profile);ids,_=check_slides(html,rep,profile); notes=parse_notes(html,rep);check_notes(notes,ids,rep);check_budget(notes,5,rep);check_placeholders(html,rep);check_duplicate_ids(html,rep);check_theme(html,theme,rep);return rep.errors
    def test_short_deck_all_themes(self):
        for theme in THEMES:
            with self.subTest(theme=theme):
                plan=prepare(self.md,self.h,self.state,theme);out=render(plan);self.assertFalse(self.structural(out,theme));self.assertFalse(verify(plan,out));self.assertNotIn('script src=',out)
    def test_standard_rejects_short(self):self.assertTrue(self.structural(render(self.plan),profile='standard'))
    def test_no_handoff_preview(self):
        plan=prepare(self.md);self.assertEqual(plan['source_readiness'],'needs_review');self.assertIn('预览｜内容待确认',render(plan));self.assertFalse(verify(plan,render(plan)))
    def test_no_state_preview(self):self.assertEqual(prepare(self.md,self.h)['source_readiness'],'needs_review')
    def test_source_changed(self):
        self.md.write_text(self.md.read_text()+'\n');self.assertRaises(ValueError,prepare,self.md,self.h,self.state)
    def test_changed_number_or_qualifier(self):
        out=render(self.plan).replace('不能预先承诺效率收益','可承诺效率收益');self.assertTrue(verify(self.plan,out))
    def test_swapped_table_cells(self):
        out=render(self.plan).replace('同类任务完成时间对比','@@tmp@@').replace('检查回答与原文一致性','同类任务完成时间对比').replace('@@tmp@@','检查回答与原文一致性');self.assertTrue(verify(self.plan,out))
    def test_empty_notes(self):
        out=render(self.plan);start=out.index('window.SPEAKER_NOTES = ');end=out.index(';</script>',start) if ';</script>' in out[start:] else out.index(';\n',start);out=out[:start]+'window.SPEAKER_NOTES = []'+out[end:];self.assertTrue(self.structural(out));self.assertTrue(verify(self.plan,out))
    def test_notes_changed(self):
        out=render(self.plan).replace('不要求今天承诺正式上线或采购。','承诺正式采购。');self.assertTrue(verify(self.plan,out))
    def test_duplicate_id(self):self.assertTrue(self.structural(render(self.plan).replace('data-slide-id="next"','data-slide-id="problem"')))
    def test_blocked_stops(self):
        plan=copy.deepcopy(self.plan);plan['source_readiness']='blocked';self.assertRaises(ValueError,render,plan)
    def test_untrusted_text_escaped(self):
        plan=copy.deepcopy(self.plan);plan['slides'][0]['visible']+='\n- <script>alert(1)</script>';plan['slides'][0]['notes']['fallback']='</script><script>alert(1)</script>';out=render(plan);self.assertNotIn('<script>alert(1)</script>',out);self.assertFalse(verify(plan,out))
    def test_preview_label_required(self):
        plan=prepare(self.md);out=render(plan).replace('预览｜内容待确认','');self.assertTrue(verify(plan,out))
    def test_legacy_quality_missing_is_preview(self):
        state=json.loads(self.state.read_text());state.pop('quality_profile');state.pop('slide_quality')
        self.state.write_text(json.dumps(state))
        plan=prepare(self.md,self.h,self.state)
        self.assertEqual(plan['source_readiness'],'ready')
        self.assertEqual(plan['content_quality']['status'],'not_reviewed')
        out=render(plan);self.assertIn('预览｜内容待确认',out);self.assertFalse(verify(plan,out))
    def test_flow_and_independent_groups(self):
        out=render(self.plan)
        self.assertEqual(out.count('class="evidence-grid evidence-flow"'),1)
        self.assertEqual(out.count('class="evidence-grid"'),1)
        self.assertEqual(out.count('class="mini-table evidence-table"'),1)
        self.assertFalse(verify(self.plan,out))
    def test_table_followed_by_list_keeps_both(self):
        raw=self.md.read_text(); i=raw.index('| 答复质量'); end=raw.index('\n',i)
        self.md.write_text(raw[:end]+'\n- 额外说明行：限制必须可见'+raw[end:])
        h=json.loads(self.h.read_text()); h['content_sha256']=digest(self.md); self.h.write_text(json.dumps(h))
        plan=prepare(self.md,self.h,self.state)
        out=render(plan)
        self.assertIn('<table class="mini-table evidence-table">',out)
        self.assertIn('额外说明行',out)
        self.assertFalse(verify(plan,out))
    def test_quiet_nav(self):
        out=render(self.plan)
        self.assertIn('background: transparent;',out)
        self.assertIn('id="currentPage"',out)
        css=(ROOT/'templates'/'deck'/'style.css').read_text(encoding='utf-8')
        nav=re.sub(r'/\*[\s\S]*?\*/','',re.search(r'\.navigation\s*\{[^}]*\}',css).group(0))
        # Container opacity would dim text and background together (2.4:1 at 0.6).
        self.assertNotIn('opacity',nav)
        self.assertIn('color: var(--ink-faint);',css)
        self.assertIn('@media (pointer: coarse)',css)

class ShippedArtifacts(unittest.TestCase):
    """The repo's own template and docs must pass the validator with default flags.

    A strict-JSON notes rule is only usable if every shipped example already
    complies; otherwise `npm run validate:skill` fails on the repository itself.
    """
    def test_template_notes_are_strict_json(self):
        html=(ROOT/'templates'/'h5-report-template.html').read_text(encoding='utf-8')
        rep=Report(); notes=parse_notes(html,rep)
        self.assertFalse(rep.errors,rep.errors)
        self.assertTrue(notes)
        ids,_=check_slides(html,rep)
        self.assertFalse(rep.errors,rep.errors)
        self.assertEqual([n.get('id') for n in notes],ids)
    def test_documented_notes_sample_is_strict_json(self):
        doc=(ROOT/'templates'/'deck'/'page-templates.md').read_text(encoding='utf-8')
        sample=re.search(r'```(?:js|json)\n(window\.SPEAKER_NOTES\s*=\s*)(\[[\s\S]*?\])\s*;?\n```',doc)
        self.assertIsNotNone(sample,'page-templates.md must contain a SPEAKER_NOTES sample')
        json.loads(sample[2])  # raises if the documented sample uses JS literals
    def test_js_literal_is_rejected_by_default(self):
        html=(ROOT/'templates'/'h5-report-template.html').read_text(encoding='utf-8')
        js=html.replace('window.SPEAKER_NOTES = [','window.SPEAKER_NOTES = [\n  // legacy sample\n  {a: 1},',1)
        rep=Report(); parse_notes(js,rep)
        self.assertTrue(rep.errors)
if __name__=='__main__':unittest.main()
