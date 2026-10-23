#!/usr/bin/env python3
"""Fail if the required ADF workflow jobs and events are absent."""
from pathlib import Path
import sys

root = Path(__file__).resolve().parents[1]
requirements = {
    '.github/workflows/verify.yml': ['pull_request:', 'push:', '    name: ', 'python tools/check_policy.py', 'python tools/verify.py --profile full'],
    '.github/workflows/stack-adapters.yml': ['pull_request:', 'push:', 'name: gate-next-fastapi', 'name: gate-expo', 'name: gate-flutter', 'actions/upload-artifact@v4'],
}
for filename, markers in requirements.items():
    path = root / filename
    if not path.is_file():
        print(f'FAIL: missing {filename}')
        sys.exit(1)
    content = path.read_text(encoding='utf-8')
    missing = [marker for marker in markers if marker not in content]
    if missing:
        print(f'FAIL: {filename} missing {missing}')
        sys.exit(1)
    print(f'PASS: {filename}')
print('PASS: CI contract (textual structural check, not GitHub execution)')
