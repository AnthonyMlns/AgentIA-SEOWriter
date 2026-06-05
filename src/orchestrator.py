import time
import json
import logging
from pathlib import Path
from typing import Callable

from src.models import BriefSEO, Synthese, Draft, RapportCritique, RapportConformiteGoogle
from src.agents.strategie import AgentStrategie
from src.agents.recherche import AgentRecherche
from src.agents.redaction import AgentRedaction
from src.agents.critique import AgentCritique
from src.agents.conformite import AgentConformiteGoogle


logger = logging.getLogger("seo_agent")


class Orchestrator:
    def __init__(self, config, agent_strategie: AgentStrategie,
                 agent_recherche: AgentRecherche,
                 agent_redaction: AgentRedaction,
                 agent_critique: AgentCritique,
                 agent_conformite: AgentConformiteGoogle | None = None):
        self.config = config
        self.agent_strategie = agent_strategie
        self.agent_recherche = agent_recherche
        self.agent_redaction = agent_redaction
        self.agent_critique = agent_critique
        self.agent_conformite = agent_conformite

    def executer(self, requete: str, repondre: Callable[[str, str], str],
                 mots_cles: str = "", ton: str = "", longueur: str = "",
                 audience: str = "", sources: list[str] | None = None,
                 avec_conformite_google: bool = True) -> dict:
        debut = time.time()
        logger.info({"event": "pipeline_start", "requete": requete})

        try:
            system = self.agent_strategie.system_prompt()
            user = self.agent_strategie.formatter_entree(
                requete=requete, mots_cles=mots_cles,
                ton=ton, longueur=longueur, audience=audience,
            )
            reponse = repondre(system, user)
            brief = self.agent_strategie.parser_sortie(reponse)
            logger.info({"event": "brief_genere",
                         "mots_cles_principaux": brief.mots_cles_principaux})

            system = self.agent_recherche.system_prompt()
            user = self.agent_recherche.formatter_entree(brief=brief, sources=sources)
            reponse = repondre(system, user)
            synthese = self.agent_recherche.parser_sortie(reponse, brief=brief)
            logger.info({"event": "synthese_generee",
                         "sources": len(synthese.sources),
                         "insights": len(synthese.insights_cles)})

            meilleur_draft = None
            meilleur_score = 0.0
            meilleur_rapport = None
            meilleur_conformite = None
            historique_critiques = []

            for iteration in range(1, self.config.max_iterations + 1):
                critiques_pour_redaction = (
                    historique_critiques[-1]["suggestions_prioritaires"]
                    if historique_critiques else None
                )
                system = self.agent_redaction.system_prompt()
                user = self.agent_redaction.formatter_entree(
                    brief=brief, synthese=synthese,
                    critiques=critiques_pour_redaction, version=iteration,
                )
                reponse = repondre(system, user)
                draft = self.agent_redaction.parser_sortie(
                    reponse, brief=brief, synthese=synthese, version=iteration,
                )
                logger.info({"event": "draft_produit", "version": iteration,
                             "titre": draft.titre})

                system = self.agent_critique.system_prompt()
                user = self.agent_critique.formatter_entree(draft=draft, brief=brief)
                reponse = repondre(system, user)
                rapport = self.agent_critique.parser_sortie(reponse, draft=draft)
                logger.info({"event": "critique_result",
                             "iteration": iteration,
                             "score": rapport.score_global,
                             "seuil_atteint": rapport.seuil_atteint})

                suggestions = list(rapport.suggestions_prioritaires)

                if avec_conformite_google and self.agent_conformite:
                    system = self.agent_conformite.system_prompt()
                    user = self.agent_conformite.formatter_entree(draft=draft, brief=brief)
                    reponse = repondre(system, user)
                    conformite = self.agent_conformite.parser_sortie(reponse, draft=draft)
                    logger.info({"event": "conformite_result",
                                 "iteration": iteration,
                                 "score": conformite.score_global,
                                 "conformite_atteinte": conformite.conformite_atteinte})

                    score_combine = (rapport.score_global + conformite.score_global) / 2
                    suggestions.extend(conformite.suggestions_prioritaires)
                    seuil_atteint = score_combine >= self.config.score_seuil
                else:
                    conformite = None
                    score_combine = rapport.score_global
                    seuil_atteint = rapport.seuil_atteint

                historique_critiques.append({
                    "iteration": iteration,
                    "score_critique": rapport.score_global,
                    "score_conformite": conformite.score_global if conformite else None,
                    "score_combine": score_combine,
                    "seuil_atteint": seuil_atteint,
                    "critiques": rapport.critiques,
                    "recommandations_conformite": conformite.recommandations if conformite else [],
                    "suggestions_prioritaires": suggestions,
                })

                if score_combine > meilleur_score:
                    meilleur_draft = draft
                    meilleur_score = score_combine
                    meilleur_rapport = rapport
                    meilleur_conformite = conformite

                if seuil_atteint:
                    logger.info({"event": "seuil_atteint",
                                 "iteration": iteration,
                                 "score": score_combine})
                    break

                if iteration == self.config.max_iterations:
                    logger.warning({"event": "iterations_max_atteintes",
                                    "score_final": meilleur_score})

            duree = time.time() - debut

            return self._assembler_sortie(
                meilleur_draft=meilleur_draft,
                meilleur_rapport=meilleur_rapport,
                meilleur_conformite=meilleur_conformite,
                brief=brief,
                synthese=synthese,
                historique_critiques=historique_critiques,
                avec_conformite_google=avec_conformite_google,
                duree_totale=duree,
            )

        except Exception as e:
            duree = time.time() - debut
            logger.error({"event": "pipeline_error", "error": str(e),
                          "duration_s": round(duree, 2)})
            raise

    def _assembler_sortie(self, meilleur_draft: Draft,
                           meilleur_rapport: RapportCritique,
                           meilleur_conformite: RapportConformiteGoogle | None,
                           brief: BriefSEO, synthese: Synthese,
                           historique_critiques: list[dict],
                           avec_conformite_google: bool,
                           duree_totale: float) -> dict:
        article_md = self._formatter_markdown(meilleur_draft)

        dossier = Path(self.config.sortie_dossier)
        dossier.mkdir(parents=True, exist_ok=True)

        nom_base = self._slugifier(brief.requete)
        chemin_md = dossier / f"{nom_base}.md"
        chemin_md.write_text(article_md, encoding="utf-8")

        rapport_data = {
            "requete": brief.requete,
            "score_final": meilleur_rapport.score_global,
            "score_editorial": meilleur_rapport.score_editorial,
            "score_seo": meilleur_rapport.score_seo,
            "seuil_atteint": meilleur_rapport.seuil_atteint,
            "iterations": len(historique_critiques),
            "duree_totale_s": round(duree_totale, 2),
            "logs": historique_critiques,
        }

        if avec_conformite_google and meilleur_conformite:
            rapport_data["conformite_google"] = {
                "score_eeat": meilleur_conformite.score_eeat,
                "score_semantique": meilleur_conformite.score_semantique,
                "score_lisibilite": meilleur_conformite.score_lisibilite,
                "score_featured_snippet": meilleur_conformite.score_featured_snippet,
                "score_maillage": meilleur_conformite.score_maillage,
                "score_meta": meilleur_conformite.score_meta,
                "score_structure": meilleur_conformite.score_structure,
                "score_originalite": meilleur_conformite.score_originalite,
                "score_global": meilleur_conformite.score_global,
                "conformite_atteinte": meilleur_conformite.conformite_atteinte,
                "recommandations": meilleur_conformite.recommandations,
            }

        chemin_json = dossier / f"{nom_base}-rapport.json"
        chemin_json.write_text(json.dumps(rapport_data, ensure_ascii=False, indent=2), encoding="utf-8")

        return {
            "article": article_md,
            "chemin_article": str(chemin_md),
            "chemin_rapport": str(chemin_json),
            "score": meilleur_rapport.score_global,
            "score_conformite": meilleur_conformite.score_global if meilleur_conformite else None,
            "seuil_atteint": meilleur_rapport.seuil_atteint,
            "iterations": len(historique_critiques),
            "duree_totale": round(duree_totale, 2),
        }

    def _formatter_markdown(self, draft: Draft) -> str:
        lines = [f"# {draft.titre}", "", draft.meta_description, ""]
        for titre_section, contenu in draft.sections.items():
            lines.append(f"## {titre_section.replace('-', ' ').title()}")
            lines.append("")
            lines.append(contenu)
            lines.append("")
        lines.append("---")
        if draft.version > 1:
            lines.append(f"*Généré par Super-Agent SEO | Version {draft.version}*")
        else:
            lines.append("*Généré par Super-Agent SEO*")
        return "\n".join(lines)

    def _slugifier(self, texte: str) -> str:
        slug = texte.lower()
        for c in " ,;:!?.'\"()[]{}":
            slug = slug.replace(c, "-")
        slug = "-".join(p for p in slug.split("-") if p)
        return slug[:80]
