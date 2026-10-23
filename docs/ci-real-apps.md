# Références réelles et CI obligatoires — V2.2

Trois applications **minimales mais avec du code exécutable** sont fournies sous `apps/`.
Ce ne sont pas les applications métier de Mawaba Technologies et elles ne remplacent pas leurs tests.

## Prérequis
- Web : Node >= 20.9, Python 3.12+, npm, navigateur Playwright.
- Expo : Node 22, Android SDK/émulateur, Java 17, Maestro. La CI compile une application Android native; cela peut être lent.
- Flutter : Flutter stable, compilateur desktop Linux et Xvfb dans la CI.

## Démarrage Windows
```powershell
cd apps/web; npm install; cd ../api; python -m pip install -r requirements.txt; cd ../web
npx playwright install chromium
cd ../..
python tools/stack_verify.py --stack next-fastapi --profile e2e

cd apps/expo; npm install; cd ../..
python tools/stack_verify.py --stack expo --profile full
# Pour e2e: ouvrir un émulateur, construire l'application, lancer Metro, installer Maestro

cd apps/flutter; flutter create . --platforms=windows; flutter pub get; cd ../..
python tools/stack_verify.py --stack flutter --profile quick
# Pour l'intégration Windows, remplacer les commandes -d linux par -d windows dans le JSON.
```

## CI et règles de protection
1. Publier le dépôt sur GitHub (aucun dépôt distant n'a été créé ici).
2. Déclencher le workflow `ADF required stack gates` sur un premier push.
3. Corriger tout job en échec ; aucun échec n'est toléré volontairement.
4. Dans Settings > Rules > Rulesets, protéger la branche principale ; exiger les checks
   `gate-next-fastapi`, `gate-expo`, `gate-flutter` et le contrôle principal V2 `verify`.
5. Exiger la validation des PR et interdire l'auto-contournement par les agents ; réserver
   la modification des workflows et politiques à des responsables avec CODEOWNERS.
6. La protection devient **effective après** publication et activation du ruleset ;
   le simple fichier YAML ne suffit pas.

## Limites connues
- Le runner Expo reconstruit une application native et le démarrage de Metro doit être validé sur GitHub.
- Le `flutter create` en CI génère des fichiers de plateforme Linux ; il faut inspecter les changements générés.
- Les captures produites par un parcours E2E sont des artefacts, pas un jugement visuel.
- `npm install` sans lockfile n'est pas reproductible : ajouter et versionner les `package-lock.json`
  après une installation réussie puis passer la CI à `npm ci`.
- Les apps sont des références techniques, non une couverture suffisante des fonctionnalités métier.
- **Aucune exécution réelle de GitHub Actions ou d'émulateur Android n'a été effectuée ici.**

## Portée des tests
- L'intégration FastAPI utilise un client HTTP in-process ; elle ne valide pas un réseau externe ni une base de données.
- L'intégration Expo est un test de composant React Native avec Jest, pas un test de services distants ; Maestro apporte le contrôle sur émulateur.
- Le test Flutter `integration_test` est utilisé par les étapes `integration` et `e2e`. Ce sont les **mêmes assertions** ; le passage deux fois ne prouve pas deux couvertures indépendantes.
- Les captures Playwright et Maestro sont attendues ; la preuve visuelle Flutter n'est pas configurée dans cette version.
