# Niveau 2 : contrat de qualité et preuves

## Chaîne de vérification
1. Revue humaine des `templates/acceptance-criteria.md` et `templates/test-plan.md` avant tout changement.
2. Traduction du plan approuvé dans `config/acceptance.json`. Les drapeaux `*_approved` de la démonstration **ne constituent pas une preuve d'identité**.
3. `python tools/check_policy.py` valide la présence des contrôles obligatoires indépendamment de la configuration des profils.
4. `python tools/verify.py --profile full` exécute architecture, unitaires, traçabilité, dans cet ordre.
5. Les sorties de tests sont enregistrées dans `reports/unit-results.json`; l'audit conserve par critère les identifiants et résultats de tests dans `reports/acceptance-report.json`.
6. `reports/verification.json` contient commandes, code de retour, durée, stdout, stderr. Des fichiers JSON sur disque doivent être confrontés au code retour du pipeline.
7. L'humain contrôle les limites, les changements sensibles et autorise la clôture. Il doit consulter **la version actuelle** du rapport.

## Critères de résultat
- `passed` : le test identifié a été exécuté et a réussi dans le run observable.
- `unverified` : test manquant, ignoré, en erreur ou échoué, ou aucun test lié.
- Exit `0` : contrôles exécutés et réussis. Exit `1` : contrôle/critère en échec. Exit `2` : configuration ou preuve invalide. Exit `3` : indisponibilité. Exit `4` : timeout.
- Un contrôle omis ne signifie **jamais** qu'une fonctionnalité est correcte.

## Réserves de sécurité
- Les agents n'ont pas le droit de modifier des tests, la CI, les manifestes de critères ou `tools/` pour obtenir un vert artificiel sans revue humaine.
- `check_policy.py` constitue une défense partielle. Une modification simultanée de ce script et des autres vérificateurs peut le contourner. **Les règles de protection de branche et les approbations CODEOWNERS sont nécessaires après publication**.
- Le manifeste d'exemple est marqué approuvé uniquement pour la démonstration. Tout projet nouveau doit repasser par une validation humaine.
- Aucun hook facultatif ne remplace la CI. Les preuves enregistrent potentiellement des informations sensibles et ne doivent pas inclure d'accès de production.
- Aucun E2E, test visuel, scan exhaustif de secrets ou test mobile ne s'exécute sans adaptateur de stack explicite.

## Ajouter des tests d'intégration ou E2E
Ajouter une commande avec timeout dans `config/verification.json` puis le contrôle au profil `full`. Créer des identifiants de tests et des collecteurs de preuves dédiés. **Ne pas associer un critère `kind: unittest` à une capture d'écran** : l'auditeur V2 ne supporte que les résultats unittest. Toute extension exige une version de schéma ou validation stricte du nouveau type.
