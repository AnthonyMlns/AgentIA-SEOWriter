# AgentIA - SEO Writer

[![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)](https://python.org)
[![OpenCode](https://img.shields.io/badge/cli-opencode-purple)](https://opencode.ai)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

Pipeline multi-agents de rédaction SEO. Génère des articles optimisés pour le référencement via une orchestration automatisée : stratégie → recherche → rédaction → critique → conformité Google.

Exécutable directement **via OpenCode** (sans dépendances Python) ou en Python.

## Fonctionnalités

- Brief SEO automatique (mots-clés, structure, ton, audience)
- Recherche et synthèse de sources
- Rédaction avec boucle d'amélioration (critique → correction, max 3 itérations)
- Évaluation SEO (10 critères pondérés, seuil 7/10)
- Conformité Google (E-E-A-T, sémantique, lisibilité, featured snippet)

## Utilisation

### Via OpenCode (recommandé)

```bash
opencode "Rédige un article SEO sur [sujet]"
```

Ou avec des options avancées :

```bash
opencode --agent seo-writer "Rédige un article SEO sur l'IA générative"
```

Le skill SEO se déclenche automatiquement sur les requêtes contenant "article SEO".

### Via CLI Python

```bash
python main.py "Rédige un article SEO sur [sujet]" \
  --mots-cles "mot1,mot2" \
  --ton professionnel \
  --longueur 1200-1500
```

Le mode CLI lit les réponses LLM sur l'entrée standard (format JSON `{"system": "...", "user": "..."}` par ligne).

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
```

Aucune clé API nécessaire — OpenCode utilise son propre LLM configuré.

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

Le pipeline est défini comme un agent OpenCode natif dans `.opencode/agents/seo-writer.md`.
Le skill `.opencode/skills/seo/SKILL.md` détecte automatiquement les requêtes SEO.

## Roadmap

- [x] Pipeline CLI Python (stratégie, recherche, rédaction, critique)
- [x] Agent OpenCode natif (utilisation sans dépendances)
- [ ] Agent Conformité Google v1.5 (E-E-A-T, sémantique, featured snippets)
- [ ] Agent Meta — amélioration continue auto-optimisante
- [ ] Mode planification de contenu (calendrier éditorial)
- [ ] CI/CD — tests automatisés + lint
- [ ] Dashboard de suivi des performances SEO

## Licence

Distribué sous licence MIT. Voir [LICENSE](LICENSE).
