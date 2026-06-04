import json

from src.agents.base import Agent
from src.models import RapportCritique, Draft, BriefSEO


class AgentCritique(Agent):
    def __init__(self, client):
        super().__init__(client, "critique")

    def system_prompt(self) -> str:
        return (
            "Tu es un expert SEO et éditorial. Évalue l'article selon les "
            "critères suivants (note /10 chaque critère) :\n"
            "1. Présence et placement des mots-clés principaux (×2)\n"
            "2. Utilisation des mots-clés secondaires (×1)\n"
            "3. Qualité et fluidité de l'écriture (×2)\n"
            "4. Structure et hiérarchie des titres (×1)\n"
            "5. Longueur conforme au brief (×1)\n"
            "6. Méta-description et balises (×1)\n"
            "7. Originalité / pas de contenu dupliqué (×1)\n"
            "8. Couverture complète du brief (×2)\n"
            "9. Ton adapté à l'audience cible (×1)\n"
            "10. Liens et références (×1)\n\n"
            "Retourne un JSON avec : score_editorial, score_seo, "
            "score_global (moyenne pondérée /10), seuil_atteint (true si ≥ 7.0), "
            "critiques (liste de {categorie, gravite, message, suggestion}), "
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
                      **kwargs) -> RapportCritique:
        cleaned = texte.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            cleaned = "\n".join(lines[1:-1])
        data = json.loads(cleaned)

        return RapportCritique(
            draft=draft,
            score_editorial=float(data.get("score_editorial", 0)),
            score_seo=float(data.get("score_seo", 0)),
            score_global=float(data.get("score_global", 0)),
            seuil_atteint=bool(data.get("seuil_atteint", False)),
            critiques=data.get("critiques", []),
            suggestions_prioritaires=data.get("suggestions_prioritaires", []),
        )
