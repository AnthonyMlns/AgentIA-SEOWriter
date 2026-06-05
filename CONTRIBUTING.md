# Contribuer à AgentIA - SEO Writer

Merci de vouloir contribuer ! Voici comment faire.

## Branches

- `main` — production, protégée
- `develop` — intégration
- `feature/*` — nouvelles fonctionnalités
- `fix/*` — corrections de bugs
- `docs/*` — documentation
- `hotfix/*` — correctifs urgents

## Workflow

1. Crée une branche depuis `develop`
2. Travaille sur ta branche
3. Ouvre une Pull Request vers `develop`
4. Attends la review
5. Merge et suppression de la branche

## Commits

Utilise [Conventional Commits](https://www.conventionalcommits.org/) :

```
feat(agent): add Google compliance evaluation
fix(orchestrator): handle timeout on API calls
docs(readme): update installation steps
```

Types : `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`.

## Code

- Python 3.12+
- Respecte le style existant
- Ajoute des tests pour les nouvelles fonctionnalités
- Passe `ruff check src/` avant de commit

## Tests

```bash
pytest tests/ --tb=short -v
```
