"""Static contracts: reference app source and mandatory CI gates exist."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class ReferenceAppContracts(unittest.TestCase):
    def test_each_stack_has_real_source_and_checks(self):
        apps = {
            'next-fastapi': ['apps/web/app/page.tsx', 'apps/web/e2e/home.spec.ts',
                             'apps/api/app/main.py', 'apps/api/tests/integration/test_api.py'],
            'expo': ['apps/expo/App.tsx', 'apps/expo/.maestro/home.yaml',
                     'apps/expo/__tests__/app.test.tsx'],
            'flutter': ['apps/flutter/lib/main.dart', 'apps/flutter/test/widget_test.dart',
                        'apps/flutter/integration_test/app_test.dart'],
        }
        for stack, paths in apps.items():
            with self.subTest(stack=stack):
                config = json.loads((ROOT / f'config/stacks/{stack}.json').read_text())
                self.assertEqual(config['profiles']['e2e'][-1], 'e2e')
                for path in paths:
                    self.assertTrue((ROOT / path).is_file(), path)

    def test_required_ci_jobs_not_dispatch_only(self):
        text = (ROOT / '.github/workflows/stack-adapters.yml').read_text()
        self.assertIn('  pull_request:', text)
        self.assertIn('  push:', text)
        for job in ('gate-next-fastapi', 'gate-expo', 'gate-flutter'):
            self.assertIn(job, text)
        self.assertIn('if: always()', text)

if __name__ == '__main__':
    unittest.main()
