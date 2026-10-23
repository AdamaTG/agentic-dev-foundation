# Adaptateurs agent — optionnels

- `preflight.ps1` : à déclencher explicitement par PowerShell ou par l'outil de votre choix.
- Aucun hook natif Claude Code, Cursor, Codex ou GitHub Copilot n'est installé automatiquement.
- Vérifier la version et les formats des événements/documentation de l'agent **avant** de configurer un hook `Stop` ou similaire. Préférer un hook signalant un blocage plutôt que de compter sur un arrêt infini jusqu'au succès.
- Pour GitHub : les véritables protections requièrent branche protégée, revue des changements sensibles, CI obligatoire. `CODEOWNERS` seul n'impose aucune approbation.
