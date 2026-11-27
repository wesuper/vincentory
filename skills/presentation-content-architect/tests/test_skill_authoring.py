"""Lightweight authoring guardrails; not a substitute for model evaluation."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

class SkillAuthoring(unittest.TestCase):
    def test_frontmatter_and_stable_entry(self):
        text = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
        head = text.split('---', 2)[1]
        name = re.search(r'^name: (.+)$', head, re.M).group(1)
        desc = re.search(r'^description: (.+)$', head, re.M).group(1)
        self.assertEqual(name, ROOT.name)
        self.assertRegex(name, r'^[a-z0-9-]{1,64}$')
        self.assertTrue(0 < len(desc) <= 1024)
        self.assertLess(len(text.splitlines()), 500)
        self.assertNotRegex(text, r'(?i)\\bv\\d+(?:\\.\\d+)?\\b')
        for link in re.findall(r'\\]\\(([^)]+)\\)', text):
            if '://' not in link:
                self.assertTrue((ROOT / link.split('#')[0]).exists(), link)

    def test_base_and_optional_paths_present(self):
        text = (ROOT / 'SKILL.md').read_text(encoding='utf-8')
        for word in ('基础','扩展','校验','预览','复盘'):
            self.assertIn(word, text)
        for name in ('presentation.md','handoff.json','working-state.json'):
            for directory in (ROOT/'examples', ROOT/'examples'/'risk-change'):
                self.assertTrue((directory/name).is_file())
