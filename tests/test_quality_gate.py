import unittest
from tools.check_acceptance import audit
from tools.check_policy import check
from pathlib import Path
import json
import tempfile

class QualityGateTests(unittest.TestCase):
    def setUp(self):
        self.manifest = {'schema_version': 1, 'task_id': 'T', 'plan_id': 'P',
                         'acceptance_approved': True, 'test_plan_approved': True,
                         'criteria': [{'id': 'AC-1', 'required': True,
                                       'checks': [{'kind': 'unittest', 'id': 'tests.example.test_ok'}]}]}
        self.observed = {'schema_version': 1, 'run_complete': True,
                         'cases': {'tests.example.test_ok': 'passed'}}

    def test_verified_criterion(self):
        self.assertTrue(audit(self.manifest, self.observed)['all_required_verified'])

    def test_missing_test_never_verified(self):
        self.observed['cases'] = {}
        self.assertFalse(audit(self.manifest, self.observed)['all_required_verified'])

    def test_skipped_test_never_verified(self):
        self.observed['cases']['tests.example.test_ok'] = 'skipped'
        self.assertFalse(audit(self.manifest, self.observed)['all_required_verified'])

    def test_unapproved_test_plan_refused(self):
        self.manifest['test_plan_approved'] = False
        with self.assertRaises(ValueError):
            audit(self.manifest, self.observed)

    def test_empty_checks_never_verified(self):
        self.manifest['criteria'][0]['checks'] = []
        self.assertFalse(audit(self.manifest, self.observed)['all_required_verified'])

    def test_removed_mandatory_check_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / 'config').mkdir()
            cfg = {'profiles': {'full': ['architecture', 'unit']},
                   'checks': {'architecture': {'command': ['python','tools/check_architecture.py']},
                              'unit': {'command': ['python','tools/run_unit.py']},
                              'acceptance': {'command': ['python','tools/check_acceptance.py']}}}
            (root / 'config/verification.json').write_text(json.dumps(cfg), encoding='utf-8')
            self.assertTrue(check(root))
