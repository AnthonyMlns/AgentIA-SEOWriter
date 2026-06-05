---
name: seo
description: Rédige un article SEO optimisé via un pipeline multi-agents automatisé avec stratégie, recherche, rédaction, critique et conformité Google
---

## Usage
Quand l'utilisateur demande la rédaction d'un article SEO, active l'agent `seo-writer` avec la requête complète.

Exemples de déclenchement :
- "Rédige un article SEO sur [sujet]"
- "Écris un article optimisé pour le référencement sur [sujet]"
- "Génère un contenu SEO pour [sujet]"
- "Produis un article avec stratégie SEO sur [sujet]"

L'agent `seo-writer` exécute le pipeline complet : stratégie → recherche → rédaction → critique (boucle max 3x) → conformité Google.

Les options avancées peuvent être fournies dans la requête :
- Mots-clés cibles
- Ton (vulgarisation, technique, professionnel)
- Longueur (ex: 1200-1500)
- Audience cible
- URLs sources
