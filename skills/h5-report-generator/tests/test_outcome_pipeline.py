"""Audience journey H5 pipeline regression; actual browser smoke check is separate."""
import copy, json, shutil, tempfile, unittest
from pathlib import Path
from prepare_render import prepare, needs_preview, route, THEMES
from render_reference import render
from verify_render import verify
ROOT=Path(__file__).resolve().parents[1]
class OutcomePipeline(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)/'demo'
        shutil.copytree(ROOT/'examples/risk-change',self.root)
        self.md=self.root/'presentation.md';self.h=self.root/'handoff.json';self.s=self.root/'working-state.json'
        self.plan=prepare(self.md,self.h,self.s)
    def tearDown(self):self.tmp.cleanup()
    def test_v3_all_themes(self):
        for theme in THEMES:
            with self.subTest(theme=theme):
                plan=prepare(self.md,self.h,self.s,theme);out=render(plan)
                self.assertFalse(needs_preview(plan));self.assertFalse(verify(plan,out))
                self.assertNotIn('预览｜内容待确认',out)
                self.assertIn('window.PRESENTATION_ROUTE = {',out)
                self.assertNotIn('真实听众画像',out)
    def test_base_ready_retained(self):
        r=ROOT/'examples';plan=prepare(r/'presentation.md',r/'handoff.json',r/'working-state.json')
        self.assertFalse(needs_preview(plan));out=render(plan)
        self.assertNotIn('预览｜内容待确认',out);self.assertNotIn('window.PRESENTATION_ROUTE = {',out)
        self.assertFalse(verify(plan,out))
    def test_declared_unreviewed_extension_requires_preview(self):
        plan=dict(self.plan,experience_quality={'status':'needs_revision'})
        self.assertTrue(needs_preview(plan));self.assertNotIn('window.PRESENTATION_ROUTE = {',render(plan))
    def test_base_without_quality_remains_preview(self):
        r=ROOT/'examples';plan=prepare(r/'presentation.md',r/'handoff.json')
        self.assertTrue(needs_preview(plan));self.assertFalse(verify(plan,render(plan)))
    def test_no_state_preview(self):
        plan=prepare(self.md,self.h);self.assertTrue(needs_preview(plan));self.assertFalse(verify(plan,render(plan)))
    def test_route_tamper(self):
        out=render(self.plan).replace('"core_slide_ids": ["decision", "delta", "controls", "next"]','"core_slide_ids": ["decision", "next"]')
        self.assertTrue(verify(self.plan,out))
    def test_prefix_precedence(self):
        self.assertEqual(route({'role':'RISK','visual_intent':'risk: compare with comparison and metrics'}),'risk')
        self.assertEqual(route({'role':'PROBLEM','visual_intent':'attribution: architecture and metric'}),'table')
    def test_preview_route_tamper(self):
        plan=prepare(self.md);out=render(plan).replace('</body>','<script>window.PRESENTATION_ROUTE = {};</script></body>')
        self.assertTrue(verify(plan,out))
if __name__=='__main__':unittest.main()
