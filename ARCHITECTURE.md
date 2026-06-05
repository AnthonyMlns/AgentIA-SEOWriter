# Super-Agent SEO — Architecture

## Stack

- **Langage** : Python 3.12+
- **CLI** : OpenCode (agent natif) ou Python / Typer
- **Modèle** : LLM configuré dans OpenCode (DeepSeek, Claude, GPT...)
- **Pas de clé API à gérer** — OpenCode gère l'authentification

## Pipeline

```
Input (requête utilisateur + options)
    │
    ▼
[1] Agent Stratégie SEO
    → mots-clés cibles, intention de recherche, structure cible, longueur, ton
    │
    ▼
[2] Agent Recherche
    → collecte et synthèse de sources
    │
    ▼
[3] Agent Rédaction
    → produit un draft en respectant les contraintes de l'Agent Stratégie
    │
    ▼
[4] Agent Critique
    → évalue le draft (ne le réécrit pas)
    → qualité éditoriale + conformité SEO
    → score global + rapport de critiques structuré
    │
    ├── score ≥ 7.0 ──► Output
    │
    └── score < 7.0 ──► retour à l'Agent Rédaction avec feedback (max 3x)
    │
    ▼
[5] Agent Conformité Google (optionnel)
    → E-E-A-T, sémantique, lisibilité, featured snippet, maillage, méta
    │
    └── score insuffisant ──► retour à l'Agent Rédaction

Output (article .md + rapport .json)
```

## Modes d'exécution

### OpenCode (recommandé)
L'agent `.opencode/agents/seo-writer.md` contient le prompt système complet du pipeline.
Le skill `.opencode/skills/seo/SKILL.md` déclenche automatiquement l'agent.

```bash
opencode "Rédige un article SEO sur [sujet]"
```

### Python
Le pipeline Python utilise une fonction `repondre(system, user) -> str` passée à l'orchestrateur.
Par défaut, le CLI lit les réponses sur l'entrée standard.

```bash
python main.py "Rédige un article SEO sur [sujet]"
```

## Contrats de données

Les agents échangent des objets typés (dataclasses Python) :

```python
@dataclass
class BriefSEO:
    requete: str
    mots_cles_principaux: list[str]
    mots_cles_secondaires: list[str]
    intention_recherche: str
    structure_cible: list[str]
    longueur_min: int
    longueur_max: int
    ton: str
    audience_cible: str
    contraintes_supplementaires: dict | None = None

@dataclass
class Synthese:
    brief: BriefSEO
    sources: list[dict]
    documents_fournis: list[str] | None
    insights_cles: list[str]
    lacunes_identifiees: list[str]

@dataclass
class Draft:
    brief: BriefSEO
    synthese: Synthese
    titre: str
    sections: dict[str, str]
    meta_description: str
    version: int = 1
    historique_critiques: list[dict] | None = None

@dataclass
class RapportCritique:
    draft: Draft
    score_editorial: float
    score_seo: float
    score_global: float
    seuil_atteint: bool
    critiques: list[dict]
    suggestions_prioritaires: list[str]

@dataclass
class RapportConformiteGoogle:
    draft: Draft
    score_eeat: float
    score_semantique: float
    score_lisibilite: float
    score_featured_snippet: float
    score_maillage: float
    score_meta: float
    score_structure: float
    score_originalite: float
    score_global: float
    conformite_atteinte: bool
    recommandations: list[dict]
    suggestions_prioritaires: list[str]
```

## Grille de score de l'Agent Critique

| # | Critère | Pondération |
|---|---|---|
| 1 | Présence et placement des mots-clés principaux | 2× |
| 2 | Utilisation des mots-clés secondaires | 1× |
| 3 | Qualité et fluidité de l'écriture | 2× |
| 4 | Structure et hiérarchie des titres | 1× |
| 5 | Longueur conforme au brief | 1× |
| 6 | Méta-description et balises | 1× |
| 7 | Originalité / pas de contenu dupliqué | 1× |
| 8 | Couverture complète du brief | 2× |
| 9 | Ton adapté à l'audience cible | 1× |
| 10 | Liens et références | 1× |

Seuil de validation : ≥ 7/10.

## Configuration

`config.yaml` à la racine :

```yaml
pipeline:
  max_iterations: 3
  score_seuil: 7.0
  timeout_global: 120

logging:
  niveau: INFO
  fichier: ./logs/pipeline.log
  format: json

sortie:
  format: markdown
  dossier: ./output
```
