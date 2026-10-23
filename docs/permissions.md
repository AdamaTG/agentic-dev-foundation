# 08 — Permissions et validations humaines
- **Responsable des autorisations :** `[nom/role]`
- **Agent autorisé :** `[liste des agents]`
- **Zones de modification permises :** `[paths]` (ex. `apps/demo/**`)
- **Exécution locale autorisée :** `scripts de validation configurés, sans privilèges élevés`
- **Accès réseau / API payantes :** `interdit par défaut ; autorisation préalable`
- **Secrets / données de production :** `interdit sans validation nominative, périmètre et durée`
- **Déploiement production :** `approbation humaine préalable et contrôle CI`
- **Suppression / migration destructive :** `approbation préalable + sauvegarde + plan de retour`
- **Modification CI / politiques / tests de sécurité :** `revue humaine obligatoire`
- **Décision produit ambiguë ou à fort impact :** `blocked jusqu'à arbitrage`

## Registre de décision
| ID | Opération | Risque | Demandeur | Approbateur | Décision | Date | Référence |
|---|---|---|---|---|---|---|---|
| APR-001 | `[exemple : modification d'une permission]` | élevé | agent | PO | pending | `[date]` | `[ticket]` |

Une hypothèse locale, peu risquée et réversible peut être consignée, jamais une décision sensible.
