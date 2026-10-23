"""Relie exigences approuvées à des résultats unittest réellement observés."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

def audit(manifest, observed):
    if manifest.get('schema_version') != 1 or observed.get('schema_version') != 1:
        raise ValueError('Version de schéma non prise en charge')
    if not manifest.get('acceptance_approved') or not manifest.get('test_plan_approved'):
        raise ValueError('Critères et plan de test non approuvés')
    if not observed.get('run_complete'):
        raise ValueError('Exécution des tests non complète')
    criteria = manifest.get('criteria')
    if not isinstance(criteria, list) or not criteria:
        raise ValueError('Aucun critère')
    seen = set()
    records = []
    for item in criteria:
        ident = item['id']
        if ident in seen:
            raise ValueError(f'Doublon: {ident}')
        seen.add(ident)
        checks = item.get('checks', [])
        statuses = []
        for check in checks:
            if check.get('kind') != 'unittest':
                raise ValueError(f'Type de preuve non supporté: {check}')
            status = observed.get('cases', {}).get(check['id'], 'missing')
            statuses.append({'test_id': check['id'], 'status': status})
        passed = bool(statuses) and all(s['status'] == 'passed' for s in statuses)
        records.append({'id': ident, 'required': bool(item.get('required', True)),
                        'status': 'passed' if passed else 'unverified', 'checks': statuses})
    success = all(r['status'] == 'passed' for r in records if r['required'])
    return {'schema_version': 1, 'created_at': datetime.now(timezone.utc).isoformat(),
            'task_id': manifest['task_id'], 'plan_id': manifest['plan_id'],
            'all_required_verified': success, 'criteria': records,
            'limitations': ['Preuve unitaire uniquement; la satisfaction métier et la validation humaine ne sont pas démontrées.']}

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--manifest', type=Path, default=ROOT / 'config/acceptance.json')
    p.add_argument('--unit-results', type=Path, default=ROOT / 'reports/unit-results.json')
    p.add_argument('--output', type=Path, default=ROOT / 'reports/acceptance-report.json')
    args = p.parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding='utf-8'))
        observed = json.loads(args.unit_results.read_text(encoding='utf-8'))
        result = audit(manifest, observed)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f'ACCEPTANCE ERROR: {exc}', file=sys.stderr)
        return 2
    for row in result['criteria']:
        print(f"[{row['status'].upper()}] {row['id']}")
    print(f'ACCEPTANCE_REPORT={args.output}')
    return 0 if result['all_required_verified'] else 1

if __name__ == '__main__':
    sys.exit(main())
