import json

from src.agents.base import Agent
from src.models import Synthese, BriefSEO


class AgentRecherche(Agent):
    def __init__(self):
        super().__init__("recherche")

    def system_prompt(self) -> str:
        return (
            "Tu es un assistant de recherche spécialisé en SEO. "
            "À partir d'un brief SEO et de sources optionnelles, produis "
            "une synthèse documentaire en JSON. "
            "Retourne UNIQUEMENT le JSON, sans texte autour."
        )

    def formatter_entree(self, brief: BriefSEO, sources: list[str] | None = None,
                         **kwargs) -> str:
        data = {
            "brief": brief.to_dict(),
            "sources_fournies": sources or [],
        }
        return json.dumps(data, ensure_ascii=False, default=str)

    def parser_sortie(self, texte: str, brief: BriefSEO | None = None,
                      **kwargs) -> Synthese:
        cleaned = texte.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            cleaned = "\n".join(lines[1:-1])
        data = json.loads(cleaned)

        return Synthese(
            brief=brief,
            sources=data.get("sources", []),
            documents_fournis=data.get("documents_fournis"),
            insights_cles=data.get("insights_cles", []),
            lacunes_identifiees=data.get("lacunes_identifiees", []),
        )
