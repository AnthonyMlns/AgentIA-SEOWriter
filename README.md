# AgentIA - SEO Writer

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://python.org)
[![DeepSeek](https://img.shields.io/badge/model-deepseek--v4--flash-green)](https://deepseek.com)
[![OpenCode](https://img.shields.io/badge/cli-opencode-purple)](https://opencode.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

Pipeline multi-agents de rédaction SEO. Génère des articles optimisés pour le référencement via une orchestration automatisée : stratégie → recherche → rédaction → critique → conformité Google.

## Fonctionnalités

- Brief SEO automatique (mots-clés, structure, ton, audience)
- Recherche et synthèse de sources
- Rédaction avec boucle d'amélioration (critique → correction, max 3 itérations)
- Évaluation SEO (10 critères pondérés, seuil 7/10)
- Conformité Google (E-E-A-T, sémantique, lisibilité, featured snippet)
- Pipeline exécutable via OpenCode (sans dépendances) ou en Python

## Utilisation

### Via OpenCode (recommandé)

```bash
opencode --agent seo "Rédige un article SEO sur [sujet]"
```

Ou simplement "Rédige un article SEO sur..." — le skill se déclenche automatiquement.

### Via CLI Python

```bash
python main.py "Rédige un article SEO sur [sujet]" \
  --mots-cles "mot1,mot2" \
  --ton professionnel \
  --longueur 1200-1500
```

### Options

| Option | Description |
|---|---|
| `--mots-cles, -k` | Mots-clés cibles (séparés par des virgules) |
| `--ton, -t` | Ton : vulgarisation, technique, professionnel |
| `--longueur, -l` | Intervalle ex: `1200-1500` |
| `--audience, -a` | Audience cible |
| `--sources, -s` | URLs sources |
| `--yes, -y` | Mode non-interactif |

## Installation

```bash
git clone https://github.com/AnthonyMlns/AgentIA-SEOWriter.git
cd AgentIA-SEOWriter

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt
cp .env.example .env
# Éditer .env : ajouter DEEPSEEK_API_KEY
```

## Architecture

```
Utilisateur → Agent Stratégie → Agent Recherche → Agent Rédaction
                                                       ↓ (boucle max 3x)
                                                 Agent Critique ←┘
                                                       ↓
                                              Agent Conformité Google
                                                       ↓
                                              Article .md + Rapport .json
```

Détail complet dans [ARCHITECTURE.md](ARCHITECTURE.md).

## Roadmap

- [x] Pipeline CLI Python (stratégie, recherche, rédaction, critique)
- [x] Agent OpenCode natif (utilisation sans dépendances)
- [ ] Agent Conformité Google v1.5 (E-E-A-T, sémantique, featured snippets)
- [ ] Agent Meta — amélioration continue auto-optimisante
- [ ] Mode planification de contenu (calendrier éditorial)
- [ ] CI/CD — tests automatisés + lint
- [ ] Dashboard de suivi des performances SEO

## Contribuer

Les contributions sont les bienvenues ! Voir [CONTRIBUTING.md](CONTRIBUTING.md).

## Licence

Distribué sous licence MIT. Voir [LICENSE](LICENSE).
