import json

from src.agents.base import Agent
from src.models import RapportConformiteGoogle, Draft, BriefSEO


class AgentConformiteGoogle(Agent):
    def __init__(self, client):
        super().__init__(client, "conformite_google")

    def system_prompt(self) -> str:
        return (
            "Tu es un expert SEO spécialisé dans les critères de ranking Google. "
            "Évalue l'article selon les 8 critères suivants (note /10) :\n\n"
            "1. **E-E-A-T** (×2) : Expertise, expérience, autorité, fiabilité "
            "perçues. L'article cite-t-il des sources ? Montre-t-il une réelle "
            "expertise ? Y a-t-il une biographie d'auteur ?\n"
            "2. **Couverture sémantique** (×2) : Synonymes, champs lexicaux, "
            "requêtes connexes. L'article couvre-t-il le sujet en profondeur ?\n"
            "3. **Lisibilité** (×1) : Phrases courtes, paragraphes aérés, "
            "vocabulaire adapté au public cible.\n"
            "4. **Featured Snippet** (×1) : Présence de Q/R explicites, listes, "
            "tableaux, définitions que Google peut extraire en position 0.\n"
            "5. **Maillage** (×1) : Liens internes et externes pertinents, "
            "textes d'ancres optimisés.\n"
            "6. **Méta-données** (×1) : Title, meta-description, balises alt "
            "(si images).\n"
            "7. **Structure navigation** (×1) : Hiérarchie H1-H3 claire, "
            "sections logiques, sommaire implicite.\n"
            "8. **Originalité** (×1) : Valeur ajoutée réelle par rapport aux "
            "pages existantes, angle unique.\n\n"
            "Retourne un JSON avec : score_eeat, score_semantique, "
            "score_lisibilite, score_featured_snippet, score_maillage, "
            "score_meta, score_structure, score_originalite, "
            "score_global (moyenne pondérée /10), "
            "conformite_atteinte (true si ≥ 7.0), "
            "recommandations (liste de {categorie, gravite, message, suggestion}), "
            "suggestions_prioritaires (liste de strings).\n"
            "Retourne UNIQUEMENT le JSON, sans texte autour."
        )

    def formatter_entree(self, draft: Draft, brief: BriefSEO, **kwargs) -> str:
        data = {
            "brief": brief.to_dict(),
            "article": {
                "titre": draft.titre,
                "sections": draft.sections,
                "meta_description": draft.meta_description,
            },
        }
        return json.dumps(data, ensure_ascii=False, default=str)

    def parser_sortie(self, texte: str, draft: Draft | None = None,
                      **kwargs) -> RapportConformiteGoogle:
        cleaned = texte.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            cleaned = "\n".join(lines[1:-1])
        data = json.loads(cleaned)

        scores = {
            k: float(data.get(k, 0))
            for k in ["score_eeat", "score_semantique", "score_lisibilite",
                       "score_featured_snippet", "score_maillage", "score_meta",
                       "score_structure", "score_originalite", "score_global"]
        }

        return RapportConformiteGoogle(
            draft=draft,
            score_eeat=scores["score_eeat"],
            score_semantique=scores["score_semantique"],
            score_lisibilite=scores["score_lisibilite"],
            score_featured_snippet=scores["score_featured_snippet"],
            score_maillage=scores["score_maillage"],
            score_meta=scores["score_meta"],
            score_structure=scores["score_structure"],
            score_originalite=scores["score_originalite"],
            score_global=scores["score_global"],
            conformite_atteinte=bool(data.get("conformite_atteinte", False)),
            recommandations=data.get("recommandations", []),
            suggestions_prioritaires=data.get("suggestions_prioritaires", []),
        )
