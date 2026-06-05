---
name: seo-redaction
description: |
  Use ONLY when the user asks to rédiger un article SEO, write SEO content, produire du contenu optimisé SEO, or when they mention: article SEO, contenu SEO, rédaction SEO, brief SEO, stratégie SEO. Do NOT use for general writing tasks.
---

# Pipeline de Rédaction SEO Multi-Agents

Quand l'utilisateur demande un article SEO, exécute le pipeline complet suivant de façon autonome, **sans rien demander à l'utilisateur** entre les étapes.

## Phase 1 : Brief Stratégie SEO

Analyse la requête et produis un brief structuré :
- Mots-clés principaux (2-4), Mots-clés secondaires (3-5)
- Intention de recherche (informationnelle/transactionnelle/navigationnelle)
- Structure cible (sections), Longueur (min/max mots)
- Ton (professionnel/vulgarisation/technique), Audience cible

## Phase 2 : Recherche & Synthèse

Génère une synthèse : 3-5 sources simulées, 3-5 insights clés, 2-3 lacunes.

## Phase 3 : Rédaction v1

Article Markdown complet : titre, meta-description, sections H1→H2→H3, exemples concrets, liens, CTA.

## Phase 4 : Auto-Critique

Note sur 10 critères (pondérés), seuil 7.0/10. Si < 7.0 → liste de suggestions.

## Phase 5 : Itération (max 3)

Corrige l'article avec les suggestions. Conserve le meilleur draft.

## Phase 6 : Conformité Google

Évalue E-E-A-T, sémantique, lisibilité, featured snippet, maillage, meta, structure, originalité.

## Phase 7 : Sauvegarde

Écris dans `./output/` :
1. `{sujet}.md` — article Markdown complet
2. `{sujet}-rapport.json` — rapport structuré

## Règles

- Exécute TOUTES les phases sans interruption.
- Sois exigeant dans les notes.
- L'article final doit être en français (sauf demande contraire).
- N'attends jamais la validation de l'utilisateur entre les phases.
