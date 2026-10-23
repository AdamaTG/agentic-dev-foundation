# 06 — Plan de test à approuver AVANT implémentation
- **ID plan :** `[PLAN-ID]`
- **Tâche :** `[TASK-ID]`
- **Révision :** `1`
- **Approbateur / date / décision :** `[nom / AAAA-MM-JJ / pending|approved|rejected]`

| Test ID | Critère | Niveau | Commande | Résultat attendu | Preuve |
|---|---|---|---|---|---|
| UT-001 | AC-001 | unitaire | `python -m unittest discover -s tests -v` | exit 0 | log + JSON |

**Données synthétiques :** `[sources]`
**Tests non couverts et justification :** `[limites]`
**Critères d'arrêt :** `tout test obligatoire manquant, panne ou validation absente => non terminé`
