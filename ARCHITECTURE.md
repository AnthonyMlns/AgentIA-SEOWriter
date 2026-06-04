# Super-Agent SEO — Architecture & Feuille de route

## Contexte

Outil multi-agents pour la rédaction et la planification de contenu SEO.
Stack : OpenCode (CLI) + DeepSeek v4 Flash via API.
Approche : version CLI d'abord, évolution vers un mode long terme ensuite.

---

## Pipeline (version 1 — ponctuel)

```
Input (requête utilisateur + documents optionnels)
    │
    ▼
┌─────────────────────────────────────┐
│         Orchestrator                │
│  valide l'entrée, gère le contexte, │
│  les timeouts, retries, logging     │
└─────────────────────────────────────┘
    │
    ▼
[1] Agent Stratégie SEO
    → mots-clés cibles, intention de recherche, structure cible, longueur, ton
    │
    ▼
[2] Agent Recherche
    → collecte et synthèse de sources (web scraping, documents fournis)
    │
    ▼
[3] Agent Rédaction
    → produit un draft en respectant les contraintes de l'Agent Stratégie
    │
    ▼
[4] Agent Critique
    → évalue le draft (ne le réécrit pas)
    → qualité éditoriale (clarté, ton, fluidité)
    → conformité SEO (densité mots-clés, balises, structure)
    → score global + rapport de critiques structuré
    │
    ├── score ≥ seuil (ex: 7/10) ──► Output
    │
    └── score < seuil ──► retour à l'Orchestrateur
            │
            ▼
    Orchestrateur transmet les critiques
    → retour à Agent Rédaction avec feedback
    → boucle max. 2-3 tours
    → si dépassé : output avec le meilleur draft + avertissement

    │
    ▼
[5] Agent Conformité Google (v1.5+)
    → E-E-A-T (expertise, autorité, fiabilité, expérience)
    → Sémantique NLP (synonymes, requêtes connexes)
    → Lisibilité (score Flesch, longueur phrases)
    → Featured Snippet (Q/R, listes, tableaux)
    → Maillage interne/externe
    → Méta-données (title, description, alt)
    │
    └── score insuffisant ──► retour à Agent Rédaction avec recommandations
                             (boucle indépendante ou fusionnée avec Critique)

Output (article + rapport SEO + conformité Google + métadonnées d'exécution)
```

---

## Rôle de chaque agent

| Agent | Entrée | Sortie | Responsabilité |
|---|---|---|---|
| Stratégie SEO | requête utilisateur | `BriefSEO` | Définir les contraintes avant la rédaction |
| Recherche | brief + sources | `Synthese` | Collecter matière et références |
| Rédaction | brief + synthèse (+ critiques optionnelles) | `Draft` | Produire le contenu |
| Critique | draft + brief | `RapportCritique` | Évaluer (notes, pas réécriture), retourner score + feedback structuré |

---

## Contrats de données

Les agents échangent des objets typés (dataclasses Python).

```python
@dataclass
class BriefSEO:
    requete: str
    mots_cles_principaux: list[str]
    mots_cles_secondaires: list[str]
    intention_recherche: str               # informationnelle, transactionnelle, navigationnelle
    structure_cible: list[str]             # sections de l'article
    longueur_min: int                      # mots
    longueur_max: int
    ton: str                               # professionnel, vulgarisation, technique
    audience_cible: str
    contraintes_supplementaires: dict | None = None

@dataclass
class Synthese:
    brief: BriefSEO
    sources: list[dict]                    # [{url, titre, extrait, pertinence}]
    documents_fournis: list[str] | None
    insights_cles: list[str]
    lacunes_identifiees: list[str]

@dataclass
class Draft:
    brief: BriefSEO
    synthese: Synthese
    titre: str
    sections: dict[str, str]               # {titre_section: contenu}
    meta_description: str
    version: int = 1
    historique_critiques: list[dict] | None = None

@dataclass
class RapportCritique:
    draft: Draft
    score_editorial: float                  # /10
    score_seo: float                        # /10
    score_global: float                     # /10
    seuil_atteint: bool
    critiques: list[dict]                   # [{categorie, gravite, message, suggestion}]
    suggestions_prioritaires: list[str]
```

---

## Orchestrateur

Composant central qui pilote le pipeline :

| Responsabilité | Détail |
|---|---|
| Validation | Vérifie la requête, les fichiers fournis, la configuration |
| Ordonnancement | Appelle chaque agent dans l'ordre, transmet les données |
| Gestion des erreurs | Retry 2x sur échec API, timeout global (120s), fallback |
| Boucle de feedback | Limite les itérations (2-3), choisit le meilleur draft si échec |
| Logging | Trace chaque étape (durée, tokens, coût, erreurs) |
| Output | Assemble l'article final + rapport de score + métadonnées |

---

## Grille de score de l'Agent Critique

L'Agent Critique note sur **10 critères** (note /10 chacun, sauf indication) :

| # | Critère | Pondération |
|---|---|---|
| 1 | Présence et placement des mots-clés principaux | 2× |
| 2 | Utilisation des mots-clés secondaires | 1× |
| 3 | Qualité et fluidité de l'écriture | 2× |
| 4 | Structure et hiérarchie des titres (H1-H3) | 1× |
| 5 | Longueur conforme au brief (bonus/malus) | 1× |
| 6 | Méta-description et balises | 1× |
| 7 | Originalité / pas de contenu dupliqué | 1× |
| 8 | Couverture complète du brief | 2× |
| 9 | Ton adapté à l'audience cible | 1× |
| 10 | Liens et références (interne/externe) | 1× |

Score global = moyenne pondérée / 10.
Seuil de validation : ≥ 7/10.
Sous un seuil critique (≤ 3/10) → alerte dans le rapport.

---

## Décisions architecturales clés

### Ordre des agents
Les critères SEO sont définis **avant** la rédaction (Agent Stratégie en premier).
Corriger après coup est moins efficace que contraindre dès le départ.

### Boucle de feedback pilotée par l'Orchestrateur
L'Agent Critique **ne modifie pas** le draft. Il produit un rapport de critiques.
L'Orchestrateur décide si le seuil est atteint et réinjecte les critiques dans l'Agent Rédaction.
Limiter à 2-3 itérations max pour éviter les boucles infinies et maîtriser les coûts.

### Stateless en v1
Le pipeline v1 est sans état : chaque requête est indépendante.
Pas de mémoire entre deux exécutions — simplifie le démarrage.

### Gestion des erreurs et résilience
- Timeout API : 30s par appel, 120s pour l'ensemble du pipeline
- Retry : 2 tentatives sur erreur transitoire (429, 500, 503)
- Fallback : si un agent plante, l'Orchestrateur peut utiliser un prompt simplifié ou demander à l'utilisateur
- Budget tokens : tracking consommation par étape, alerte si dépassement

---

## Modes d'utilisation prévus

### Mode ponctuel (v1 — CLI)
- Déclenchement manuel par l'utilisateur
- Une requête → un article
- Pas de persistance entre les sessions

### Mode long terme (v2 — évolution)
- État persistant : historique des contenus produits
- Calendrier de contenu : clustering de sujets, planification
- Déclenchement planifié ou événementiel
- Stockage à définir : fichiers locaux, Notion, Google Drive, BDD

| Dimension | Ponctuel (v1) | Long terme (v2) |
|---|---|---|
| État | Stateless | Persistant |
| Déclencheur | Manuel | Planifié / événementiel |
| Mémoire | Contexte de la requête | Historique des contenus |
| Output | Article + rapport + métadonnées | Article + mise à jour du calendrier |

---

## Interface CLI

```bash
# Usage
opencode "Rédige un article SEO sur [sujet]"

# Avec options avancées
opencode "Rédige un article sur le machine learning" \
  --mots-cles "ia,deep learning,réseaux de neurones" \
  --ton technique \
  --longueur 1500-2000 \
  --sources "https://exemple.com/article1" \
  --output ./output/article.md

# Format de sortie (-o) : markdown (défaut), json, both
# Niveau de détail (-v) : basic, detailed
# Pas de confirmation (-y) : mode non-interactif
```

Le CLI expose les flags suivants :
- `--mots-cles` ou `-k` : mots-clés cibles (séparés par des virgules)
- `--ton` : ton de rédaction (vulgarisation, technique, professionnel)
- `--longueur` : intervalle de mots (ex: `1500-2000`)
- `--sources` : URLs sources (séparées par des espaces)
- `--documents` : chemin vers fichiers joints (.txt, .pdf, .md)
- `--output` : dossier de sortie
- `--format` ou `-o` : format de sortie (markdown, json, both)
- `--verbose` ou `-v` : niveau de détail dans le rapport
- `--yes` ou `-y` : mode non-interactif (pas de confirmation)

---

## Stack technique

### v1 — CLI
- **Langage** : Python 3.12+
- **Modèle** : DeepSeek v4 Flash (API compatible OpenAI)
- **Client API** : `openai` SDK Python (compatible OpenAI)
- **CLI** : `argparse` (stdlib) ou `typer` / `click`
- **Environnement** : OpenCode CLI
- **Configuration** : `.env` (clé API), `config.yaml` (paramètres agents, seuils, tokens)
- **Logging** : `structlog` ou `logging` (JSON lines, fichier + console)
- **Tests** : `pytest` + `pytest-cov`, `vcrpy` pour mock API

### v2 — Options d'évolution
- **LangGraph** : idéal pour les boucles de feedback et les états persistants
- **CrewAI** : plus haut niveau, bon si on veut prototyper vite
- **Stockage** : à définir selon le besoin (fichiers, Notion, Google Drive, BDD)

---

## Configuration

Fichier `config.yaml` (ou `config.json`) à la racine :

```yaml
api:
  model: "deepseek-chat"         # ou gpt-4o-mini, etc.
  temperature: 0.7
  max_tokens_per_call: 4096
  timeout: 30                    # secondes par appel
  retry_attempts: 2

pipeline:
  max_iterations: 3
  score_seuil: 7.0
  timeout_global: 120            # secondes

logging:
  niveau: INFO                   # DEBUG, INFO, WARNING, ERROR
  fichier: ./logs/pipeline.log
  format: json                   # json ou text

sortie:
  format: markdown               # markdown, json, both
  dossier: ./output
```

---

## Logging et observabilité

Chaque étape du pipeline produit une entrée structurée :

```json
{"event": "agent_start", "agent": "strategie", "timestamp": "...", "requete": "..."}
{"event": "agent_end",   "agent": "strategie", "duration_s": 3.2, "tokens": 850, "cost": 0.002}
{"event": "critique_result", "score": 6.5, "iteration": 2, "seuil_atteint": false}
{"event": "pipeline_end",   "duration_s": 45.0, "total_tokens": 12500, "total_cost": 0.035}
```

Utile pour debug, facturation, et optimisation des prompts.

---

## Tests

| Niveau | Outil | Cible |
|---|---|---|
| Unitaire | pytest | Chaque agent isolé (mock API) |
| Intégration | pytest + vcrpy | Pipeline complet avec réponses API enregistrées |
| E2E | script bash/CLI | Cas réel sur un sujet (avec vraie API, optionnel) |
| Fiabilité | pytest + hypothesis | Fuzzing des entrées, cas limites, timeout |

Les tests mockent l'API DeepSeek via `vcrpy` : les appels sont enregistrés une fois, rejoués ensuite. Pas de coût API en CI.

---

---

## Exemple complet — "Rédige un article sur l'IA générative pour les PME"

### 1. Commande utilisateur

```bash
opencode "Rédige un article SEO sur l'IA générative pour les PME" \
  --mots-cles "ia générative,pme,intelligence artificielle,automatisation" \
  --ton vulgarisation \
  --longueur 1200-1500 \
  --output ./output/ia-pme.md
```

### 2. Orchestrateur — Validation

```python
# L'Orchestrateur reçoit la requête brute
requete = "Rédige un article SEO sur l'IA générative pour les PME"
args = {
    "mots_cles": "ia générative,pme,intelligence artificielle,automatisation",
    "ton": "vulgarisation",
    "longueur": "1200-1500",
    "output": "./output/ia-pme.md"
}

# Validation : requête non vide, mots-clés présents, format longueur valide
# Chargement config.yaml → modèle, seuils, timeout
# Initialisation du logger

log = {"event": "pipeline_start", "requete": requete, "timestamp": "..."}
```

### 3. Agent Stratégie SEO → `BriefSEO`

Appel API DeepSeek avec prompt système spécialisé :

```
Tu es un stratège SEO expert. À partir de la requête utilisateur et des mots-clés,
produis un brief SEO structuré au format JSON.
```

Sortie (parsing du JSON retourné par l'API) :

```python
brief = BriefSEO(
    requete="Rédige un article SEO sur l'IA générative pour les PME",
    mots_cles_principaux=["ia générative", "pme"],
    mots_cles_secondaires=["intelligence artificielle", "automatisation",
                           "chatgpt entreprise", "productivité"],
    intention_recherche="informationnelle",
    structure_cible=[
        "Introduction : pourquoi l'IA générative devient accessible aux PME",
        "Qu'est-ce que l'IA générative ? (définition simple)",
        "Cas d'usage concrets pour les PME (rédaction, service client, marketing)",
        "Avantages et limites",
        "Comment démarrer sans budget énorme",
        "Conclusion et perspectives"
    ],
    longueur_min=1200,
    longueur_max=1500,
    ton="vulgarisation",
    audience_cible="dirigeants de PME, non-techniciens",
    contraintes_supplementaires={
        "eviter_jargon": True,
        "inclure_chiffres_concrets": True,
        "exemples_francais": True
    }
)

log = {"event": "agent_end", "agent": "strategie", "duration_s": 4.1,
       "tokens": 920, "cost": 0.003}
```

### 4. Agent Recherche → `Synthese`

Appel API avec le brief en contexte. L'agent génère des recherches simulées (v1) et les synthétise :

```python
synthese = Synthese(
    brief=brief,
    sources=[
        {"url": "https://exemple.com/ia-pme-2024",
         "titre": "L'IA générative expliquée aux PME",
         "extrait": "75% des PME pourraient bénéficier de l'IA générative...",
         "pertinence": 0.92},
        {"url": "https://exemple.com/outils-gratuits-ia",
         "titre": "Top 5 des outils IA gratuits pour TPE/PME",
         "extrait": "ChatGPT, Claude, Canva AI... accessibles sans abonnement coûteux",
         "pertinence": 0.88}
    ],
    documents_fournis=None,
    insights_cles=[
        "L'IA générative n'est plus réservée aux grands groupes",
        "Les outils gratuits ou freemium sont nombreux",
        "Le ROI est rapide sur des tâches répétitives (emails, descriptions produits)"
    ],
    lacunes_identifiees=[
        "Peu de données récentes spécifiques au marché français",
        "Manque de retours d'expérience de PME françaises"
    ]
)

log = {"event": "agent_end", "agent": "recherche", "duration_s": 5.8,
       "tokens": 1240, "cost": 0.004}
```

### 5. Agent Rédaction → `Draft` (version 1)

Appel API avec brief + synthèse. Prompt système :

```
Tu es un rédacteur SEO expert. Rédige un article en respectant strictement
le brief ci-dessous. Utilise les insights de la synthèse. Ton : vulgarisation
pour dirigeants de PME non-techniciens. Inclus des exemples concrets.
```

```python
draft = Draft(
    brief=brief,
    synthese=synthese,
    titre="IA générative pour les PME : le guide pratique 2025",
    sections={
        "introduction": (
            "Imaginez pouvoir rédiger un devis, répondre à un client ou "
            "créer une publication LinkedIn en 30 secondes. C'est ce que "
            "l'IA générative rend possible, même avec un petit budget..."
        ),
        "quest-ce-que-ia-generative": (
            "L'IA générative, c'est une technologie capable de créer du "
            "contenu (texte, images, code) à partir d'une simple description. "
            "Contrairement aux idées reçues, pas besoin d'être expert..."
        ),
        "cas-usage-concrets": (
            "1. Service client : chatbots alimentés par GPT pour répondre 24/7\n"
            "2. Marketing : génération d'articles blog, posts réseaux sociaux\n"
            "3. Commercial : emails personnalisés en masse..."
        ),
        "avantages-et-limites": (
            "Avantages : gain de temps (jusqu'à 40% sur la rédaction), "
            "coût réduit, disponibilité 24/7. "
            "Limites : nécessite une relecture humaine, risques de confidentialité..."
        ),
        "comment-demarrer": (
            "Étape 1 : identifiez les tâches répétitives de votre équipe. "
            "Étape 2 : testez ChatGPT (gratuit) ou Claude sur un cas concret. "
            "Étape 3 : formez un collaborateur pour superviser les sorties..."
        ),
        "conclusion": (
            "L'IA générative n'est pas une mode passagère. Pour les PME, "
            "c'est une opportunité d'égaler les grands groupes sur le plan "
            "de la productivité, à condition de commencer petit et d'itérer..."
        )
    },
    meta_description="Découvrez comment les PME peuvent utiliser l'IA générative "
                     "pour gagner en productivité. Guide pratique avec outils "
                     "gratuits, cas concrets et conseils pour démarrer.",
    version=1
)

log = {"event": "agent_end", "agent": "redaction", "duration_s": 12.3,
       "tokens": 2150, "cost": 0.007}
```

### 6. Agent Critique → `RapportCritique` (itération 1)

Appel API avec draft + brief. Prompt système :

```
Tu es un expert SEO et éditorial. Évalue cet article selon les critères
suivants (note /10). Retourne un JSON structuré : scores, critiques,
suggestions. Ne réécris PAS l'article.
```

Retour API parsé :

```python
rapport = RapportCritique(
    draft=draft,
    score_editorial=6.0,
    score_seo=5.5,
    score_global=5.8,           # (6.0×2 + 5.5×1) / 3 = 5.8
    seuil_atteint=False,         # 5.8 < 7.0
    critiques=[
        {
            "categorie": "mots_cles",
            "gravite": "haute",
            "message": "Le mot-clé 'IA générative' apparaît seulement 3 fois "
                       "dans le corps (objectif : 6-8 pour 1200 mots)",
            "suggestion": "Ajouter 'IA générative' naturellement dans les "
                          "sections 'Avantages' et 'Comment démarrer'"
        },
        {
            "categorie": "structure",
            "gravite": "moyenne",
            "message": "Les sous-titres ne contiennent pas les mots-clés "
                       "secondaires (ex: 'automatisation' manquant)",
            "suggestion": "Renommer 'Cas d'usage concrets' → 'Cas d'usage : "
                          "automatisation concrète pour PME'"
        },
        {
            "categorie": "longueur",
            "gravite": "basse",
            "message": "Article à 1100 mots, sous le minimum de 1200",
            "suggestion": "Développer la section 'Comment démarrer' avec un "
                          "tableau comparatif d'outils"
        },
        {
            "categorie": "liens",
            "gravite": "moyenne",
            "message": "Aucun lien externe ou appel à action",
            "suggestion": "Ajouter 2-3 liens vers des outils cités et une "
                          "CTA en conclusion"
        }
    ],
    suggestions_prioritaires=[
        "Augmenter la densité du mot-clé principal à 6+ occurrences",
        "Ajouter des mots-clés secondaires dans les sous-titres",
        "Développer pour atteindre 1200 mots minimum",
        "Ajouter des liens externes et une CTA"
    ]
)

log = {"event": "critique_result", "score": 5.8, "iteration": 1,
       "seuil_atteint": False, "tokens": 980, "cost": 0.003}
```

### 7. Orchestrateur — Décision

```python
# Pseudo-logique de l'Orchestrateur
iteration = 1
meilleur_draft = draft
meilleur_score = rapport.score_global

while rapport.seuil_atteint is False and iteration < config.max_iterations:
    iteration += 1
    # Transmettre le rapport de critique à l'Agent Rédaction
    draft = agent_redaction.executer(
        brief=brief,
        synthese=synthese,
        critiques=suggestions_prioritaires,  # feedback de l'itération précédente
        version=iteration
    )
    rapport = agent_critique.executer(draft=draft, brief=brief)
    if rapport.score_global > meilleur_score:
        meilleur_draft = draft
        meilleur_score = rapport.score_global

# Si seuil non atteint après max_iterations, sortir le meilleur draft
# avec un avertissement dans le rapport final
```

### 8. Agent Rédaction → `Draft` (version 2, avec feedback)

Appel API avec brief + synthèse + critiques :

```
Tu es un rédacteur SEO expert. Tu as déjà produit une première version
ci-dessous. Voici les retours d'un expert SEO à corriger impérativement :
1. Augmente la densité du mot-clé 'IA générative' à 6-8 occurrences
2. Ajoute des mots-clés secondaires dans les sous-titres
3. Développe pour atteindre 1200 mots minimum
4. Ajoute 2-3 liens externes et une CTA

Conserve le ton et la structure générale.
```

```python
draft_v2 = Draft(
    brief=brief,
    synthese=synthese,
    titre="IA générative pour les PME : le guide pratique 2025",
    sections={
        "introduction": "Imaginez... (inchangé)",
        "quest-ce-que-ia-generative": "L'IA générative... (développé + mots-clés)",
        "cas-usage-automatisation-pme": (
            "← titre enrichi avec mot-clé secondaire\n"
            "Cas d'usage : automatisation concrète pour PME\n"
            "1. Service client : chatbots IA disponibles 24/7... (développé)\n"
            "2. Marketing : génération de contenu automatisée...\n"
            "3. Commercial : relances automatiques personnalisées..."
        ),
        "avantages-et-limites-ia-generative": (
            "← titre enrichi\n"
            "Avantages : l'IA générative fait gagner jusqu'à 40% de temps..."
        ),
        "comment-demarrer": (
            "Tableau comparatif : ChatGPT (gratuit), Claude (freemium), "
            "Perplexity (gratuit)...\n"
            "[Lien vers outil 1](https://...) [Lien vers outil 2](https://...)"
        ),
        "conclusion": (
            "Prêt à passer à l'action ? Téléchargez notre checklist... (CTA)\n"
            "L'IA générative est une chance pour les PME..."
        )
    },
    meta_description="Découvrez comment les PME peuvent utiliser l'IA générative...",
    version=2,
    historique_critiques=[
        {"iteration": 1, "suggestions": suggestions_prioritaires}
    ]
)
```

### 9. Agent Critique → `RapportCritique` (itération 2)

```python
rapport_v2 = RapportCritique(
    draft=draft_v2,
    score_editorial=7.5,
    score_seo=7.0,
    score_global=7.3,           # (7.5×2 + 7.0×1) / 3 = 7.3
    seuil_atteint=True,          # 7.3 ≥ 7.0 ✓
    critiques=[
        {
            "categorie": "mots_cles",
            "gravite": "basse",
            "message": "Densité ok (7 occurrences), mais 'automatisation' "
                       "pourrait apparaître une fois de plus",
            "suggestion": "Optionnel : mention dans la conclusion"
        }
    ],
    suggestions_prioritaires=[]
)

log = {"event": "critique_result", "score": 7.3, "iteration": 2,
       "seuil_atteint": True, "tokens": 890, "cost": 0.003}
```

### 10. Orchestrateur — Finalisation

```python
# Seuil atteint → on sort
article_final = draft_v2
rapport_final = rapport_v2

# Assemblage de l'output
output = {
    "article": article_final,
    "rapport": rapport_final,
    "metadonnees": {
        "iterations": 2,
        "duree_totale_s": 38.7,
        "tokens_total": 6180,
        "cout_total": 0.020,
        "modele": "deepseek-chat",
        "score_final": 7.3
    }
}

# Écriture des fichiers
# ./output/ia-pme.md            → article en Markdown
# ./output/ia-pme-rapport.json  → rapport SEO + métadonnées

log = {"event": "pipeline_end", "duration_s": 38.7,
       "total_tokens": 6180, "total_cost": 0.020}
```

### 11. Fichiers produits

**`./output/ia-pme.md`** — Article Markdown formaté :

```markdown
# IA générative pour les PME : le guide pratique 2025

Meta-description : Découvrez comment les PME peuvent utiliser l'IA générative
pour gagner en productivité. Guide pratique avec outils gratuits, cas concrets
et conseils pour démarrer.

## Introduction
...

## Qu'est-ce que l'IA générative ?
...

## Cas d'usage : automatisation concrète pour PME
...

## Avantages et limites de l'IA générative
...

## Comment démarrer sans budget énorme
| Outil | Prix | Cas d'usage |
|---|---|---|
| ChatGPT | Gratuit/Freemium | Rédaction, brainstorming |
| Claude | Freemium | Analyse, synthèse |
| Canva AI | Freemium | Visuels marketing |

[→ Découvrir ChatGPT](https://chat.openai.com)
[→ Découvrir Claude](https://claude.ai)

## Conclusion
... Prêt à passer à l'action ? [Téléchargez notre checklist](#)...

---

*Généré par Super-Agent SEO | Score : 7.3/10 | 2 itérations | Coût : 0.020 $*
```

**`./output/ia-pme-rapport.json`** — Rapport d'exécution :

```json
{
  "requete": "Rédige un article SEO sur l'IA générative pour les PME",
  "score_final": 7.3,
  "score_editorial": 7.5,
  "score_seo": 7.0,
  "seuil_atteint": true,
  "iterations": 2,
  "duree_totale_s": 38.7,
  "tokens_total": 6180,
  "cout_total": 0.020,
  "modele": "deepseek-chat",
  "logs": [
    {"agent": "strategie", "duration_s": 4.1, "tokens": 920, "cost": 0.003},
    {"agent": "recherche", "duration_s": 5.8, "tokens": 1240, "cost": 0.004},
    {"agent": "redaction", "duration_s": 12.3, "tokens": 2150, "cost": 0.007, "version": 1},
    {"agent": "critique",  "duration_s": 4.2, "tokens": 980,  "cost": 0.003, "iteration": 1, "score": 5.8},
    {"agent": "redaction", "duration_s": 8.5, "tokens": 1580, "cost": 0.005, "version": 2},
    {"agent": "critique",  "duration_s": 3.8, "tokens": 890,  "cost": 0.003, "iteration": 2, "score": 7.3}
  ]
}
```

---

## Agent Meta — amélioration continue (v2+)

Un cinquième agent, **Agent Meta**, qui analyse les rapports accumulés et ajuste les autres agents.

### Principe

```
                  ┌──────────────────────────┐
                  │   Base de rapports (.jsonl) │
                  └──────────┬───────────────┘
                             │
                             ▼
                  ┌──────────────────────────┐
                  │      Agent Meta           │
                  │  - Agrège les scores       │
                  │  - Détecte les patterns    │
                  │  - Génère des recommandations│
                  └────┬──────┬──────┬────────┘
                       │      │      │
              ┌────────┘      │      └────────┐
              ▼               ▼                ▼
      Agent Stratégie   Agent Rédaction   Agent Critique
      ← ajustement      ← ajustement      ← ajustement
        des prompts       des prompts       des seuils/grille
```

### Ce que l'Agent Meta analyse

| Analyse | Données utilisées | Action possible |
|---|---|---|
| **Scores récurrents bas** | Moyenne des scores par critère sur N rapports | Ajuster le prompt de l'Agent Rédaction (ex: insister sur la densité mots-clés) |
| **Critiques qui reviennent** Fréquence par catégorie (mots_cles, structure, liens...) | Ajouter une règle dans le prompt système |
| **Dérive de qualité** | Évolution du score moyen dans le temps | Alerter l'utilisateur, re-calibrer les seuils |
| **Coût par article** | Tokens consommés par agent, nombre d'itérations moyen | Optimiser : augmenter la température pour réduire les boucles, ou ajuster max_iterations |
| **Échecs de boucle** | Cas où max_iterations atteint sans seuil validé | Assouplir le seuil ou renforcer le prompt Rédaction |
| **Longueur réelle vs cible** | Écart type entre longueur commandée et produite | Ajuster la consigne de longueur dans le brief |

### Format des recommandations

```python
@dataclass
class RecommendationMeta:
    agent_cible: str                    # "strategie", "redaction", "critique"
    type_ajustement: str                # "prompt_systeme", "seuil", "poids_grille"
    raison: str                         # analyse qui motive l'ajustement
    modification: str                   # texte à ajouter/modifier dans le prompt ou config
    impact_attendu: str                 # "amelioration_score", "reduction_couts", ...
    appliquee_automatiquement: bool     # True si confiance > 80%, False si validation requise
    confiance: float                    # 0.0 - 1.0, basée sur taille échantillon et cohérence
```

### Exemple concret

```python
# Après 50 articles, l'Agent Meta détecte :
#   → 70% des rapports mentionnent "densité mots-clés insuffisante"
#   → Score moyen SEO : 5.8/10
#   → Pattern : les articles de → 1500 mots sous-utilisent les mots-clés

recommendation = RecommendationMeta(
    agent_cible="redaction",
    type_ajustement="prompt_systeme",
    raison="Sur 50 articles, 35 ont reçu une critique 'densité mots-clés'. "
           "Score SEO moyen : 5.8 (vs objectif 7.0). Corrélation : articles > 1500 mots.",
    modification="Ajouter en tête de prompt : "
                 "'Règle impérative : le mot-clé principal doit apparaître "
                 "au moins une fois tous les 200 mots.'",
    impact_attendu="amelioration_score",
    appliquee_automatiquement=True,
    confiance=0.92
)
```

### Déclenchement

- **Périodique** : après chaque N exécutions (ex: toutes les 10)
- **Sur seuil** : si le score moyen des 5 derniers articles descend sous un seuil
- **Manuel** : l'utilisateur peut lancer `opencode --optimize`

### Boucle fermée

```
Exécution → Rapports → Agent Meta → Ajustements
                                        │
                              ┌─────────┴─────────┐
                              ▼                   ▼
                     Mise à jour des         Mise à jour de la
                     prompts système         configuration (seuils)
```

En v2, le système devient auto-optimisant : chaque article rend les suivants meilleurs, sans intervention humaine.

---

## Agent Conformité Google (v1.5+)

Vérifie les critères de ranking Google directement exploitables sur le contenu rédigé.

### Grille d'évaluation

| # | Critère | Note /10 | Poids | Détail |
|---|---|---|---|---|
| 1 | **E-E-A-T** | /10 | ×2 | Expertise, expérience, autorité, fiabilité perçues |
| 2 | **Couverture sémantique** | /10 | ×2 | Synonymes, champs lexicaux, requêtes connexes |
| 3 | **Lisibilité** | /10 | ×1 | Score Flesch, longueur des phrases, paragraphes |
| 4 | **Featured Snippet** | /10 | ×1 | Présence de Q/R, listes, tableaux exploitables |
| 5 | **Maillage** | /10 | ×1 | Liens internes/externes pertinents, ancres |
| 6 | **Méta-données** | /10 | ×1 | Title, meta-description, alt sur les images |
| 7 | **Structure navigation** | /10 | ×1 | Hiérarchie H1-H3, sommaire, ancres |
| 8 | **Originalité** | /10 | ×1 | Valeur ajoutée vs contenu existant |

Score = moyenne pondérée / 10. Seuil ≥ 7/10.

### Contrat de données

```python
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

### Intégration dans le pipeline

Deux modes possibles :

**Mode fusionné (défaut)** : l'Agent Critique intègre déjà certains critères Google (originalité, structure, liens). L'Agent Conformité Google s'exécute après lui et complète l'évaluation. Le score final est la moyenne des deux rapports.

**Mode indépendant** : l'Agent Conformité Google s'exécute en parallèle de l'Agent Critique. L'Orchestrateur combine les deux scores et réinjecte les recommandations cumulées dans l'Agent Rédaction.

```python
# Dans l'Orchestrateur
rapport_critique = agent_critique.executer(draft=draft, brief=brief)
rapport_conformite = agent_conformite.executer(draft=draft, brief=brief)

score_combine = (rapport_critique.score_global + rapport_conformite.score_global) / 2
recommandations = (
    rapport_critique.suggestions_prioritaires +
    rapport_conformite.suggestions_prioritaires
)
```

---

## Mise à jour du rôle des agents

| Agent | Entrée | Sortie | Responsabilité |
|---|---|---|---|
| Stratégie SEO | requête utilisateur | `BriefSEO` | Définir les contraintes avant la rédaction |
| Recherche | brief + sources | `Synthese` | Collecter matière et références |
| Rédaction | brief + synthèse (+ critiques) | `Draft` | Produire le contenu |
| Critique | draft + brief | `RapportCritique` | Évaluer (score + feedback structuré) |
| **Conformité Google** | draft + brief | `RapportConformiteGoogle` | Vérifier les critères de ranking Google |
| **Meta** *(v2)* | Base de rapports | `RecommendationMeta` | Analyser, détecter les patterns, ajuster les autres agents |

---

## Prochaines étapes

### v1 — Pipeline de base

- [x] Définir le format d'entrée CLI (flags, fichier de config, stdin)
- [x] Définir le format de l'output (Markdown, JSON, both)
- [x] Définir les contrats de données entre agents
- [x] Définir la grille de score de l'Agent Critique
- [x] Définir la grille de l'Agent Conformité Google
- [ ] Implémenter la configuration (lecture config.yaml + .env)
- [ ] Implémenter l'Orchestrateur (pipeline, erreurs, boucle, logging)
- [ ] Implémenter l'Agent Stratégie SEO
- [ ] Implémenter l'Agent Recherche
- [ ] Implémenter l'Agent Rédaction
- [ ] Implémenter l'Agent Critique + logique de boucle
- [ ] Implémenter l'Agent Conformité Google
- [ ] Implémenter le CLI (typer/argparse)
- [ ] Mettre en place les tests unitaires (pytest + vcrpy)
- [ ] Tester le pipeline end-to-end sur un cas réel
- [ ] Ajouter la CI (GitHub Actions) avec lint + tests

### v2 — Optimisation continue

- [ ] Accumuler les rapports dans une base (fichier JSONL / SQLite)
- [ ] Implémenter l'Agent Meta (analyse + recommandations)
- [ ] Ajouter le mécanisme d'auto-ajustement des prompts
- [ ] Ajouter le mode `--optimize` (déclenchement manuel Agent Meta)
- [ ] Ajouter le déclenchement périodique (toutes les N exécutions)
- [ ] Dashboard ou rapport de synthèse "santé du pipeline"
- [ ] Décider du stockage pour la v2 (fichiers, Notion, Google Drive, BDD)
