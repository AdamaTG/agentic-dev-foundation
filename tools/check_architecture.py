"""Garde-fou minimal de structure et de secrets évidents (non exhaustif)."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = ["AGENTS.md", "docs/project.md", "docs/permissions.md", "config/verification.json", ".github/workflows/verify.yml"]
CHECKED = [ROOT / "examples" / "signalement.py"]
PATTERNS = [re.compile(r"(?i)api[_-]?key\s*=\s*['\"][^'\"]{8,}['\"]"), re.compile(r"(?i)password\s*=\s*['\"][^'\"]{8,}['\"]")]

def check(root=ROOT):
    errors = [f"Fichier obligatoire absent : {p}" for p in REQUIRED if not (root / p).is_file()]
    for file in CHECKED:
        if not file.exists():
            errors.append(f"Code d'exemple absent : {file.name}")
            continue
        data = file.read_text(encoding="utf-8")
        for pattern in PATTERNS:
            if pattern.search(data):
                errors.append(f"Secret potentiel dans {file.relative_to(root)}")
    return errors

if __name__ == "__main__":
    found = check()
    for item in found:
        print("ERROR:", item, file=sys.stderr)
    print(f"Architecture : {len(found)} erreur(s)")
    sys.exit(1 if found else 0)
