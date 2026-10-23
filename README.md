# Agentic Dev Foundation — V2 Quality & Evidence

Socle local générique pour Windows/PowerShell. Bibliothèque standard Python seulement : aucun agent ni API n'est requis pour lancer les tests. La CLI OpenSpec reste une intégration **à initialiser volontairement**.

## Pré-requis
Python 3.11+ accessible sous `python`; Git facultatif en local; Node.js >= 20.19.0 et npm uniquement pour OpenSpec. Éditeur/agent au choix. Aucun abonnement nécessaire pour les contrôles locaux.

## Démarrage PowerShell
```powershell
cd agentic-dev-foundation
python --version
python tools/verify.py --profile full
python tools/task_state.py list
```
Le premier appel produit `reports/verification.json` (sortie observable). Codes : 0 tous contrôles réussis, 1 tests/checkers échoués, 2 configuration invalide, 3 vérification indisponible/rapport impossible, 4 délai dépassé.

## Cadrage (10 modèles)
1. `docs/project.md` — fiche projet
2. `docs/requirements.md` — exigences
3. `docs/stack.md` — stack
4. `docs/architecture.md` — conventions
5. `templates/acceptance-criteria.md` — critères
6. `templates/test-plan.md` — plan de test
7. `templates/task.yaml` — tâches/dépendances
8. `docs/permissions.md` — permissions/approbations
9. `templates/progress.json` — état/reprise
10. `templates/verification-report.md` — rapport final

Adapter les modèles (ne pas effacer l'exemple si on souhaite garder une démonstration). Approuver critères et plan AVANT d'autoriser l'implémentation.

## Démonstration de suivi/reprise
```powershell
python tools/task_state.py init TASK-001 --scope "Validation locale de signalement" --criteria AC-001 AC-002
python tools/task_state.py set TASK-001 ready
python tools/task_state.py set TASK-001 in_progress
python tools/verify.py --profile full
python tools/task_state.py set TASK-001 verifying
python tools/task_state.py evidence TASK-001 reports/verification.json
python tools/task_state.py set TASK-001 awaiting_approval
# APRES revue humaine uniquement, pas par l'agent :
python tools/task_state.py approve TASK-001 --actor "responsable-produit"
python tools/task_state.py set TASK-001 done
python tools/task_state.py list
```
Ne pas lancer `approve` avant examen des résultats et du plan de test. La V1 n'assure pas la preuve cryptographique de l'identité de l'approbateur : l'accès local reste sous votre contrôle. Les données sont conservées dans `state/tasks.json` (ignoré par Git) ; sauvegardez le fichier pour préserver la reprise.

## Adapter les contrôles à la stack
Modifier `config/verification.json` : ajouter un contrôle `lint`, `typecheck`, `integration`, `e2e` avec tableau de commande et délai, puis ajouter son nom à `profiles.full`. Exemples non activés : `["npm", "run", "lint"]`, `["flutter", "test"]`. Ne jamais utiliser `shell=True`. Toute suppression/affaiblissement d'un contrôle nécessite revue humaine.

## OpenSpec (manuel, NON testé dans cette archive)
```powershell
node --version
npm install -g @fission-ai/openspec@latest
openspec --version
openspec init
```
Consulter `openspec init --help` et choisir les outils réellement utilisés. Avant init, faire une copie ou un commit : l'initialisation peut modifier des instructions et commandes d'agents. Commandes `openspec ...` = terminal ; `/opsx:...` = chat de l'assistant. Vérifier le nom exact affiché après init. Documentation : https://github.com/Fission-AI/OpenSpec

## Agents et budgets
`AGENTS.md` = consignes communes; `CLAUDE.md` et `.github/copilot-instructions.md` = adaptateurs. Superpowers est facultatif et non installé. Aucun modèle local/cloud n'est invoqué automatiquement. Ollama possible ultérieurement, sous réserve de RAM/VRAM et de qualité adaptée; API cloud susceptible de facturation. Consigner coût et quota selon le fournisseur, ne jamais supposer une fenêtre identique.

## CI
`.github/workflows/verify.yml` fonctionne lors d'un push/PR sur GitHub, pas dans ce dossier local. Le résultat de `verify.py` ne dépend pas de l'affirmation d'un agent. Pour un vrai dépôt, protéger la branche et demander une revue humaine des scripts, politiques et workflows; seul un mainteneur décide des permissions.

## Limites V1
Pas d'orchestration autonome, pas de navigateur/émulateur, pas de scan complet des secrets, pas de contrôle des dépenses, pas de hooks agent, pas de vérification des critères par machine ni garantie d'identité de l'approbateur. Les rapports peuvent contenir des sorties sensibles : ne pas les publier sans revue. `task_state.py` n'est pas conçu pour des écritures concurrentes multi-processus; usage local mono-opérateur.

## Niveau 2 — vérifications et traçabilité
```powershell
python tools/check_policy.py
python tools/verify.py --profile full
Get-Content reports/verification.json
Get-Content reports/unit-results.json
Get-Content reports/acceptance-report.json
```
`config/acceptance.json` mappe chaque critère obligatoire vers un identifiant `unittest` exact. Dans le jeu de démonstration, deux critères sont associés à deux tests réellement exécutables. Les drapeaux d'approbation de cet EXEMPLE ne valent pas signature; sur un projet réel faire approuver critères, plan et manifeste par la personne responsable.

Avant de déclarer une tâche terminée : contrôle de politique 0, `verify.py` 0, `all_required_verified` vrai, preuve actualisée et revue humaine des limites. La commande `task_state.py` V1 ne vérifie pas automatiquement les champs du manifeste; ne contournez pas cette étape manuelle.

Pour les revues IA et visuelles, utiliser `templates/ai-review.md` et `templates/visual-review.md`. Aucun navigateur, simulateur ou modèle IA n'est lancé automatiquement. La configuration CI Windows est fournie mais **non exécutée sur GitHub**. Voir `docs/quality-gates.md` pour protections contre les contournements et limites connues.


## V2.1 — Stack adapters

See [`docs/stack-adapters.md`](docs/stack-adapters.md). Commands: `python tools/stack_verify.py --stack next-fastapi --profile full` (or `expo` / `flutter`). Without actual apps and dependencies, commands intentionally fail rather than report a pass.


## V2.2 : projets réels et CI par stack
Voir [docs/ci-real-apps.md](docs/ci-real-apps.md) pour les trois applications, les prérequis et les règles de protection obligatoires.
