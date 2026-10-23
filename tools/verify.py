"""Exécuteur indépendant de contrôles. Ne nécessite que la bibliothèque standard."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]

def utc_now():
    return datetime.now(timezone.utc).isoformat()

def run(profile, config_file, output_file):
    try:
        config = json.loads(config_file.read_text(encoding="utf-8"))
        names = config["profiles"][profile]
        if not names or not isinstance(names, list):
            raise ValueError("Profil vide ou invalide")
        checks = []
        for name in names:
            item = config["checks"][name]
            cmd = [x.replace("{python}", sys.executable) for x in item["command"]]
            if not cmd or not all(isinstance(x, str) for x in cmd):
                raise ValueError("Commande invalide")
            timeout = int(item["timeout_seconds"])
            if timeout <= 0:
                raise ValueError("Délai invalide")
            checks.append((name, cmd, timeout))
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"ERREUR CONFIGURATION : {exc}", file=sys.stderr)
        return 2
    # Les collecteurs ne doivent pas réutiliser des preuves produites lors d'un précédent run.
    for generated in ('unit-results.json', 'acceptance-report.json'):
        path = ROOT / 'reports' / generated
        try:
            path.unlink(missing_ok=True)
        except OSError as exc:
            print(f"ERREUR PREUVE OBSOLETE : {exc}", file=sys.stderr)
            return 3
    results = []
    overall = 0
    for name, cmd, timeout in checks:
        started = time.monotonic()
        code = None
        status = "error"
        try:
            completed = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout, check=False)
            code = completed.returncode
            out, err = completed.stdout, completed.stderr
            status = "passed" if code == 0 else "failed"
            if code != 0 and overall == 0:
                overall = 1
        except subprocess.TimeoutExpired as exc:
            status = "timeout"
            out = (exc.stdout or b"")
            err = (exc.stderr or b"")
            if isinstance(out, bytes):
                out = out.decode("utf-8", errors="replace")
            if isinstance(err, bytes):
                err = err.decode("utf-8", errors="replace")
            overall = 4
        except OSError as exc:
            status = "unavailable"
            out, err = "", str(exc)
            if overall != 4:
                overall = 3
        entry = {"check": name, "command": cmd, "status": status, "exit_code": code,
                 "duration_seconds": round(time.monotonic() - started, 3), "stdout": out, "stderr": err}
        results.append(entry)
        print(f"[{status.upper()}] {name}: code={code}, {entry['duration_seconds']}s")
        if err and status != "passed":
            print(err[-1200:], file=sys.stderr)
    report = {"schema_version": 1, "created_at": utc_now(), "profile": profile, "exit_code": overall, "results": results,
              "limitations": ["Les revues humaines, la couverture E2E et les services externes ne sont pas vérifiés par la V1."]}
    try:
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    except OSError as exc:
        print(f"IMPOSSIBLE D'ECRIRE LA PREUVE : {exc}", file=sys.stderr)
        return 3
    print(f"Rapport : {output_file}")
    return overall

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--profile", default="full")
    parser.add_argument("--config", type=Path, default=ROOT / "config/verification.json")
    parser.add_argument("--output", type=Path, default=ROOT / "reports/verification.json")
    args = parser.parse_args()
    sys.exit(run(args.profile, args.config, args.output))
