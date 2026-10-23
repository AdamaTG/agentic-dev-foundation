# ADF GitHub CI: validation réelle et activation des protections

État au 23 octobre 2026: compte GitHub `AdamaTG` identifié via connecteur. Aucun nouveau dépôt ADF créé; aucune exécution GitHub Actions attestée; aucune règle appliquée. Les dépôts existants du compte ne doivent pas être réutilisés sans choix explicite.

## 1. Créer le dépôt dédié

Dans GitHub, créer `AdamaTG/agentic-dev-foundation` (privé de préférence), **vide**, sans README initial. Le connecteur disponible ne sait pas créer les dépôts ni administrer les règles.

Depuis Windows PowerShell, après décompression de l'archive dans le dossier `agentic-dev-foundation` :

```powershell
gh auth login
git init
git branch -M main
git add .
git commit -m "Initial ADF CI reference apps"
git remote add origin https://github.com/AdamaTG/agentic-dev-foundation.git
git push -u origin main
```

## 2. Vérifier les runs dans GitHub

```powershell
gh run list --repo AdamaTG/agentic-dev-foundation --limit 10
gh run view RUN_ID --repo AdamaTG/agentic-dev-foundation --log-failed
```

Attendre les quatre conclusions **success**: `verify`, `gate-next-fastapi`, `gate-expo`, `gate-flutter`. Si un check échoue: corriger code, dépendances ou workflow sur branche; ouvrir PR; ne pas supprimer le check et ne pas activer les règles avant de valider chaque job.

## 3. Protéger la branche (après les runs)

Le fichier `scripts/protect-main.ps1` propose un ruleset GitHub. Il utilise GitHub CLI `gh`, nécessite les droits `Administration` sur le dépôt et est soumis aux fonctionnalités disponibles pour son plan et sa visibilité.

```powershell
./scripts/protect-main.ps1
./scripts/protect-main.ps1 -Apply
```

La première commande est une simulation sans mutation. La seconde crée un ruleset actif, sans modifier un ruleset existant. Vérifier d'abord `Settings > Rules > Rulesets` pour éviter les doublons. Le ruleset impose PR + une revue et les quatre contexts. Pour la protection de workflow, contrôler aussi les permissions de modification des fichiers `.github/`, `tools/` et `config/`.

## 4. Prouver le blocage

Créer une branche `test/broken-gate`, casser temporairement un test puis ouvrir une PR. Vérifier que GitHub refuse sa fusion. Ne pas fusionner cette PR. Documenter URL PR, SHA, run IDs, logs, statut des quatre checks et capture de blocage dans `docs/github-ci-evidence.md`.

## 5. Limites

- Des workflows YAML valides ne sont pas une preuve d'exécution réussie.
- GitHub Free, les dépôts publics/privés et les rulesets ont des capacités différentes selon l'offre et le type de dépôt.
- Les dépendances npm ne sont pas verrouillées dans cette archive; générer et versionner les `package-lock.json` après installation validée, puis préférer `npm ci`.
- Les runners Android/Flutter peuvent devoir être ajustés selon les SDK et capacités de machines.
- Ne jamais afficher de `success` si un test est omis, suspendu ou indisponible.
