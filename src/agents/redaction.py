import json

from src.agents.base import Agent
from src.models import Draft, BriefSEO, Synthese


class AgentRedaction(Agent):
    def __init__(self):
        super().__init__("redaction")

    def system_prompt(self) -> str:
        return (
            "Tu es un rédacteur SEO expert. Rédige un article en respectant "
            "strictement le brief fourni. Utilise les insights de la synthèse. "
            "Retourne un JSON avec les champs : titre, sections (dictionnaire "
            "titre_section → contenu), meta_description. "
            "Retourne UNIQUEMENT le JSON, sans texte autour."
        )

    def formatter_entree(self, brief: BriefSEO, synthese: Synthese,
                         critiques: list[str] | None = None,
                         version: int = 1, **kwargs) -> str:
        data = {
            "brief": brief.to_dict(),
            "synthese": synthese.to_dict(),
            "version": version,
        }
        if critiques:
            data["retour_critique"] = critiques

        return json.dumps(data, ensure_ascii=False, default=str)

    def parser_sortie(self, texte: str, brief: BriefSEO | None = None,
                      synthese: Synthese | None = None,
                      version: int = 1,
                      historique_critiques: list[dict] | None = None,
                      **kwargs) -> Draft:
        cleaned = texte.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            cleaned = "\n".join(lines[1:-1])
        data = json.loads(cleaned)

        return Draft(
            brief=brief,
            synthese=synthese,
            titre=data.get("titre", ""),
            sections=data.get("sections", {}),
            meta_description=data.get("meta_description", ""),
            version=version,
            historique_critiques=historique_critiques,
        )
