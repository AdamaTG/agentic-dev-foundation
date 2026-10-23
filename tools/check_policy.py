"""Minimum de contrôles obligatoires non configurable par les agents."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {'architecture', 'unit', 'acceptance'}

def check(root=ROOT):
    errors = []
    try:
        cfg = json.loads((root / 'config/verification.json').read_text(encoding='utf-8'))
        full = cfg['profiles']['full']
        if len(full) != len(set(full)) or not REQUIRED.issubset(set(full)):
            errors.append('Profil full incomplet, doublons, ou contrôle obligatoire retiré')
        for key in REQUIRED:
            item = cfg['checks'][key]
            cmd = item['command']
            if not isinstance(cmd, list) or not cmd or any(not isinstance(s, str) for s in cmd):
                errors.append(f'Commande invalide: {key}')
            expected = {'architecture': 'tools/check_architecture.py', 'unit': 'tools/run_unit.py',
                        'acceptance': 'tools/check_acceptance.py'}[key]
            if expected not in cmd:
                errors.append(f'Commande modifiée pour {key}: chemin attendu {expected}')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        errors.append(f'Politique illisible: {exc}')
    return errors

if __name__ == '__main__':
    errors = check()
    for e in errors:
        print('POLICY ERROR:', e, file=sys.stderr)
    print(f'Policy: {len(errors)} error(s)')
    sys.exit(1 if errors else 0)
