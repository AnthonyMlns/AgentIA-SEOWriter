import json

from src.agents.base import Agent
from src.models import BriefSEO


class AgentStrategie(Agent):
    def __init__(self, client):
        super().__init__(client, "strategie")

    def system_prompt(self) -> str:
        return (
            "Tu es un stratège SEO expert. À partir de la requête utilisateur "
            "et des mots-clés fournis, produis un brief SEO structuré en JSON. "
            "Retourne UNIQUEMENT le JSON, sans texte autour."
        )

    def formatter_entree(self, requete: str, mots_cles: str = "",
                         ton: str = "", longueur: str = "",
                         audience: str = "", **kwargs) -> str:
        return json.dumps({
            "requete": requete,
            "mots_cles": mots_cles,
            "ton_suggere": ton,
            "longueur_souhaitee": longueur,
            "audience": audience,
        }, ensure_ascii=False)

    def parser_sortie(self, texte: str, **kwargs) -> BriefSEO:
        cleaned = texte.strip()
        if cleaned.startswith("```"):
            lines = cleaned.splitlines()
            cleaned = "\n".join(lines[1:-1])
        data = json.loads(cleaned)

        longueur_min, longueur_max = 800, 1500
        if "longueur_souhaitee" in data and data["longueur_souhaitee"]:
            parts = data["longueur_souhaitee"].replace(" ", "").split("-")
            if len(parts) == 2:
                try:
                    longueur_min = int(parts[0])
                    longueur_max = int(parts[1])
                except ValueError:
                    pass

        return BriefSEO(
            requete=data.get("requete", ""),
            mots_cles_principaux=data.get("mots_cles_principaux", []),
            mots_cles_secondaires=data.get("mots_cles_secondaires", []),
            intention_recherche=data.get("intention_recherche", "informationnelle"),
            structure_cible=data.get("structure_cible", []),
            longueur_min=longueur_min,
            longueur_max=longueur_max,
            ton=data.get("ton", "professionnel"),
            audience_cible=data.get("audience_cible", ""),
            contraintes_supplementaires=data.get("contraintes_supplementaires"),
        )
