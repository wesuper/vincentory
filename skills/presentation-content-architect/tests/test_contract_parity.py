"""Guard files that each skill ships its own copy of against silent drift.

Both skills carry the protocol, schema and parser so each can be installed alone,
and the H5 skill carries a fixture copy of the examples (its README says to keep
them identical by hand — this is the machine check that makes that real).
In the repository the copies must stay byte-identical (skills/README.md). When a
skill is installed standalone the sibling directory is absent, so these checks
skip rather than fail.
"""
import hashlib, unittest
from pathlib import Path

SKILL=Path(__file__).resolve().parents[1]
SIBLING=SKILL.parent/'h5-report-generator'
PAIRS=[
    ('scripts/evaluate_effectiveness.py','scripts/evaluate_effectiveness.py'),
    ('references/effectiveness-contract.md','references/effectiveness-contract.md'),
    ('scripts/content_contract.py','scripts/content_contract.py'),
    ('references/experience-contract.md','references/experience-contract.md'),
    ('schemas/handoff.schema.json','schemas/handoff.schema.json'),
    ('references/presentation-contract.md','references/presentation-content-contract.md'),
]
# Every file the H5 fixture must mirror; names match, parent directories differ.
EXAMPLE_FILES=('presentation.md','handoff.json','working-state.json','outline.md','claim-map.json','sources.md')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

@unittest.skipUnless(SIBLING.is_dir(),'sibling skill not installed; nothing to compare')
class ContractParity(unittest.TestCase):
    def test_copies_are_byte_identical(self):
        for mine,theirs in PAIRS:
            with self.subTest(file=mine):
                a,b=SKILL/mine,SIBLING/theirs
                self.assertTrue(a.is_file(),f'missing {a}')
                self.assertTrue(b.is_file(),f'missing {b}')
                self.assertEqual(sha(a),sha(b),f'{mine} drifted from h5-report-generator/{theirs}')
    def test_example_fixture_matches_content_source(self):
        source=SKILL/'examples'; fixture=SIBLING/'examples'
        self.assertTrue(fixture.is_dir(),f'missing {fixture}')
        # Same file set both ways: a fixture-only file would be invisible to the diff above.
        self.assertEqual(sorted(p.name for p in source.iterdir() if p.is_file()),
                         sorted(p.name for p in fixture.iterdir() if p.is_file()))
        for name in EXAMPLE_FILES:
            with self.subTest(file=name):
                self.assertTrue((source/name).is_file(),f'missing content source {name}')
                self.assertEqual(sha(source/name),sha(fixture/name),
                    f'examples/{name} drifted from presentation-content-architect/examples/{name}')

if __name__=='__main__':unittest.main()


@unittest.skipUnless(SIBLING.is_dir(),'sibling skill not installed')
class ExtendedFixtureParity(unittest.TestCase):
    def test_outcome_fixture(self):
        for dirname in ('risk-change','base-effectiveness'):
            mine=SKILL/'examples'/dirname; theirs=SIBLING/'examples'/dirname
            names=sorted(p.name for p in mine.iterdir() if p.is_file())
            self.assertEqual(names,sorted(p.name for p in theirs.iterdir() if p.is_file()))
            for name in names:
                self.assertEqual(sha(mine/name),sha(theirs/name))
