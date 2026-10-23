"""Suivi JSON local : transitions atomiques et approbation humaine explicite."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
STATE = ROOT / "state" / "tasks.json"
STATES = {"pending", "ready", "in_progress", "verifying", "blocked", "awaiting_approval", "done", "failed"}
ALLOWED = {"pending": {"ready", "blocked"}, "ready": {"in_progress", "blocked"},
           "in_progress": {"verifying", "blocked", "failed"},
           "verifying": {"in_progress", "awaiting_approval", "blocked", "failed"},
           "awaiting_approval": {"done", "blocked"}, "blocked": {"ready", "failed"},
           "failed": {"ready"}, "done": set()}

def now():
    return datetime.now(timezone.utc).isoformat()

def save(data, path=STATE):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp, path)

def load(path=STATE):
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"schema_version": 1, "tasks": {}}

def apply(data, action, task_id, **kwargs):
    tasks = data["tasks"]
    if action == "init":
        if task_id in tasks:
            raise ValueError("Tâche déjà créée")
        tasks[task_id] = {"id": task_id, "scope": kwargs["scope"], "dependencies": kwargs.get("depends_on", []),
                          "acceptance_criteria": kwargs["criteria"], "status": "pending", "attempts": 0,
                          "max_attempts": kwargs["max_attempts"], "evidence_refs": [], "approval_required": True,
                          "approval_granted": False, "last_error": None, "updated_at": now(), "history": []}
        return tasks[task_id]
    task = tasks[task_id]
    if action == "evidence":
        evidence = kwargs["evidence"]
        if not (ROOT / evidence).is_file():
            raise ValueError("Preuve introuvable sur disque (chemin relatif au dépôt)")
        if evidence not in task["evidence_refs"]:
            task["evidence_refs"].append(evidence)
        task["updated_at"] = now()
        return task
    if action == "approve":
        if task["status"] != "awaiting_approval":
            raise ValueError("Approbation seulement à l'étape awaiting_approval")
        if not task["evidence_refs"]:
            raise ValueError("Preuve requise avant approbation")
        task["approval_granted"] = True
        task["history"].append({"timestamp": now(), "event": "approval_recorded", "actor": kwargs["actor"]})
        task["updated_at"] = now()
        return task
    destination = kwargs["status"]
    origin = task["status"]
    if destination not in ALLOWED[origin]:
        raise ValueError(f"Transition non autorisée : {origin} -> {destination}")
    if destination == "in_progress":
        if origin == "ready":
            for d in task["dependencies"]:
                if d not in tasks or tasks[d]["status"] != "done":
                    raise ValueError(f"Dépendance non terminée : {d}")
        if task["attempts"] >= task["max_attempts"]:
            raise ValueError("Limite de tentatives atteinte")
        task["attempts"] += 1
    if destination == "done" and (not task["approval_granted"] or not task["evidence_refs"]):
        raise ValueError("Preuve et approbation exigées")
    task["status"] = destination
    task["updated_at"] = now()
    task["history"].append({"timestamp": now(), "from": origin, "to": destination, "note": kwargs.get("note", "")})
    if destination == "blocked":
        task["last_error"] = kwargs.get("note", "Blocage sans précision")
    return task

def main():
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    i = sub.add_parser("init")
    i.add_argument("task_id"); i.add_argument("--scope", required=True); i.add_argument("--criteria", nargs="+", required=True)
    i.add_argument("--depends-on", nargs="*", default=[]); i.add_argument("--max-attempts", type=int, default=2)
    s = sub.add_parser("set")
    s.add_argument("task_id"); s.add_argument("status", choices=sorted(STATES)); s.add_argument("--note", default="")
    e = sub.add_parser("evidence")
    e.add_argument("task_id"); e.add_argument("evidence")
    a = sub.add_parser("approve")
    a.add_argument("task_id"); a.add_argument("--actor", required=True)
    sub.add_parser("list")
    args = parser.parse_args()
    data = load()
    try:
        if args.action == "list":
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return 0
        kwargs = vars(args).copy(); kwargs.pop("action"); task_id = kwargs.pop("task_id")
        if args.action == "init" and kwargs["max_attempts"] < 1:
            raise ValueError("max-attempts doit être positif")
        item = apply(data, args.action, task_id, **kwargs)
        save(data)
        print(json.dumps(item, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, KeyError, OSError) as exc:
        print(f"ERREUR : {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
