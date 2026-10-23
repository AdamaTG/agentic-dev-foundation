"""Exécute unittest et produit des résultats par test, observables sur disque."""
import argparse
import json
from pathlib import Path
import sys
import unittest
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]

class Result(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cases = {}

    def startTest(self, test):
        super().startTest(test)
        self.cases[test.id()] = 'running'

    def addSuccess(self, test):
        super().addSuccess(test)
        self.cases[test.id()] = 'passed'

    def addFailure(self, test, err):
        super().addFailure(test, err)
        self.cases[test.id()] = 'failed'

    def addError(self, test, err):
        super().addError(test, err)
        self.cases[test.id()] = 'error'

    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self.cases[test.id()] = 'skipped'

    def addExpectedFailure(self, test, err):
        super().addExpectedFailure(test, err)
        self.cases[test.id()] = 'expected_failure'

    def addUnexpectedSuccess(self, test):
        super().addUnexpectedSuccess(test)
        self.cases[test.id()] = 'unexpected_success'

class Runner(unittest.TextTestRunner):
    resultclass = Result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=ROOT / 'reports/unit-results.json')
    args = parser.parse_args()
    sys.path.insert(0, str(ROOT))
    suite = unittest.defaultTestLoader.discover(str(ROOT / 'tests'), pattern='test_*.py', top_level_dir=str(ROOT))
    result = Runner(verbosity=2).run(suite)
    output = {
        'schema_version': 1, 'created_at': datetime.now(timezone.utc).isoformat(),
        'run_complete': True, 'tests_run': result.testsRun,
        'cases': result.cases, 'successful': result.wasSuccessful(),
        'errors': len(result.errors), 'failures': len(result.failures),
        'skips': len(result.skipped)
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding='utf-8')
    print(f'UNIT_RESULT_FILE={args.output}')
    return 0 if result.wasSuccessful() else 1

if __name__ == '__main__':
    sys.exit(main())
