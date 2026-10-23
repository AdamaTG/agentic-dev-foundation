# Instructions communes aux agents — ADF

1. Lire `docs/project.md`, `docs/architecture.md`, la specification concernée et `docs/permissions.md` avant de modifier du code. Ne lire que les sous-dossiers pertinents.
2. Ne pas inventer de critères d'acceptation approuvés. Proposer les changements et demander la validation humaine du plan de test avant d'implémenter.
3. Limiter chaque changement au périmètre de sa tâche; ne pas modifier les tests, CI, règles de sécurité ou permissions pour obtenir artificiellement un succès.
4. Ne jamais utiliser de secrets de production, effectuer une opération payante, supprimer des données, lancer une migration destructive ou déployer en production sans approbation explicite.
5. Exécuter `python tools/verify.py --profile full`; rapporter la sortie et le chemin du fichier JSON créé. Ne jamais affirmer qu'une commande a été exécutée sans journal observable.
6. Une erreur persistante après deux tentatives doit être enregistrée comme blocage, pas bouclée sans limite.
7. Séparer *observations vérifiées*, *jugements IA* et *points à valider*. Seul un humain peut autoriser la clôture d'une tâche avec une validation requise.
8. Ne pas modifier `.github/workflows`, `tools/verify.py`, `tools/task_state.py`, `config/verification.json`, `docs/permissions.md` sans revue humaine explicite.
9. Si un outil dispose de son propre fichier d'instructions, il doit pointer vers ce document, sans dupliquer des politiques divergentes.
10. Lorsque survient une erreur récurrente, proposer une entrée dans `docs/lessons-learned.md` avec cause, correctif et garde-fou mesurable.

11. Niveau 2 : lancer `python tools/check_policy.py` puis `python tools/verify.py --profile full`; regarder `reports/acceptance-report.json` et signaler tous les critères `unverified`. Ne jamais inventer une approbation dans `config/acceptance.json`.
12. Les captures visuelles et commentaires IA sont des observations complémentaires; ils ne remplacent pas des tests instrumentés.
