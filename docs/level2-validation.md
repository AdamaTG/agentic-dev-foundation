# Rapport de validation du niveau 2 (génération)

Environnement observé : conteneur Linux, Python 3.13. Non encore testé sur Windows ni sur GitHub Actions.

Procédure de reproduction :

```powershell
python tools/check_policy.py
python tools/verify.py --profile full
Get-Content reports/verification.json
Get-Content reports/unit-results.json
Get-Content reports/acceptance-report.json
```

Test d'échec volontaire du manifeste : changer temporairement un ID de test de `config/acceptance.json` vers `tests.absent.test_manquant`, puis lancer `python tools/verify.py --profile full`. La vérification `acceptance` doit échouer avec code 1; restaurer ensuite le manifeste. Ne pas modifier le manifeste approuvé en production sans nouvelle validation.

Test de politique : supprimer temporairement `acceptance` de `profiles.full` dans `config/verification.json`; `python tools/check_policy.py` doit échouer. Restaurer la configuration.

Ne pas interpréter les deux critères illustratifs comme validation métier d'un projet réel. La couverture réelle du critère reste limitée aux assertions fournies dans les tests.
