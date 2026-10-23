# Exemple fil rouge — TASK-001 : création locale d'un signalement

## Besoin et périmètre
Un agent municipal saisit une description; le système local retourne un identifiant `SIG-...` et un statut initial `nouveau`. Pas de réseau, base, authentification ni UI en V1.

## Critères proposés (pour exemple seulement)
- AC-001 : description vide, espaces ou `None` -> `ValueError`.
- AC-002 : deux créations produisent des identifiants distincts avec préfixe `SIG-`.
- AC-003 : statut initial `nouveau`.

## Plan de test
- UT-001 -> AC-001 : `tests/test_signalement.py::test_description_obligatoire` (unittest).
- UT-002 -> AC-002 / AC-003 : `tests/test_signalement.py::test_identifiant_unique_et_statut`.
- AR-001 : `tools/check_architecture.py` contrôle structure et quelques secrets en dur; ne remplace pas une analyse de sécurité.
- Validation humaine : décider si la description doit avoir une longueur maximale, si un doublon doit être détecté, et si un identifiant aléatoire suffit (risque de collision très faible, pas de garantie mathématique).

## Séquence
1. Le responsable valide le périmètre, AC et plan de test.
2. L'agent travaille uniquement dans `examples/` et `tests/`, avec revue en cas de changement de tests approuvés.
3. Exécuter `python tools/verify.py --profile full` et ouvrir `reports/verification.json`.
4. Attacher la preuve via `task_state.py evidence` et passer `awaiting_approval`.
5. Le responsable vérifie code, couverture réelle, limites et approbation; consigne son identité (locale, non authentifiée).
6. Passer `done` seulement après approbation.

## Rapport type
- Tests machine : voir `reports/verification.json` (le fichier d'archive est un exemple d'exécution dans cet environnement, pas une garantie pour la machine cible).
- Non testés : interface, web/mobile, réseau, CI GitHub, sessions d'agents et sécurité complète.
- Décisions en attente : longueur maximale et stratégie d'identifiants en production.
