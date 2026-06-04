# Pipeline SEO — Mode opératoire OpenCode

Quand l'utilisateur demande à rédiger un article SEO ou invoque la commande `rediger-article`, exécute le pipeline suivant étape par étape.

## Déroulement

### Phase 1 : Brief SEO (Stratégie)

Analyse la requête utilisateur et produit un brief structuré. Écris-le dans `output/{slug}-brief.json`.

```json
{
  "requete": "...",
  "mots_cles_principaux": ["..."],
  "mots_cles_secondaires": ["..."],
  "intention_recherche": "informationnelle|transactionnelle|navigationnelle",
  "structure_cible": ["section 1", "section 2", "..."],
  "longueur_min": 1200,
  "longueur_max": 1500,
  "ton": "vulgarisation|technique|professionnel",
  "audience_cible": "...",
  "contraintes_supplementaires": {}
}
```

### Phase 2 : Recherche (synthèse documentaire)

Utilise `webfetch` pour explorer 2-3 sources pertinentes sur le sujet. Produis une synthèse dans `output/{slug}-synthese.json`.

### Phase 3 : Rédaction

Rédige l'article en Markdown dans `output/{slug}.md` (v1) en respectant strictement le brief : structure, mots-clés, ton, longueur.

Format attendu :
```markdown
# Titre principal

Meta-description : ...

## Introduction
...

## Section 1
...
```

### Phase 4 : Critique

Évalue l'article selon les 10 critères (note /10, seuil ≥ 7/10) :

| # | Critère | Poids |
|---|---|---|
| 1 | Mots-clés principaux | ×2 |
| 2 | Mots-clés secondaires | ×1 |
| 3 | Qualité d'écriture | ×2 |
| 4 | Structure des titres | ×1 |
| 5 | Longueur conforme | ×1 |
| 6 | Meta-description | ×1 |
| 7 | Originalité | ×1 |
| 8 | Couverture du brief | ×2 |
| 9 | Ton adapté | ×1 |
| 10 | Liens/références | ×1 |

Score global = moyenne pondérée / 10.

Produis le rapport dans `output/{slug}-rapport.json`.

### Phase 5 : Boucle de feedback

Si score < 7/10 et < 3 itérations :
- Relis les critiques
- Améliore l'article
- Repasse en Phase 4

### Phase 6 : Finalisation

Affiche à l'utilisateur :
- ✅ Chemin de l'article : `output/{slug}.md`
- 📊 Rapport : `output/{slug}-rapport.json`
- Score : X.X/10 — Itérations : N — Seuil atteint : Oui/Non
