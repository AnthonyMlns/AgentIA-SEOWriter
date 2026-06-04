import json
import pytest
from unittest.mock import MagicMock

from src.config import Config
from src.client import DeepSeekClient
from src.models import BriefSEO, Synthese, Draft, RapportConformiteGoogle
from src.agents.conformite import AgentConformiteGoogle
from src.agents.strategie import AgentStrategie
from src.agents.recherche import AgentRecherche
from src.agents.redaction import AgentRedaction
from src.agents.critique import AgentCritique
from src.orchestrator import Orchestrator


def test_agent_conformite_parser():
    client = MagicMock(spec=DeepSeekClient)
    agent = AgentConformiteGoogle(client)

    reponse_json = json.dumps({
        "score_eeat": 7.0,
        "score_semantique": 6.5,
        "score_lisibilite": 8.0,
        "score_featured_snippet": 5.0,
        "score_maillage": 6.0,
        "score_meta": 7.5,
        "score_structure": 8.0,
        "score_originalite": 7.0,
        "score_global": 6.8,
        "conformite_atteinte": False,
        "recommandations": [
            {"categorie": "eeat", "gravite": "moyenne",
             "message": "Manque de sources d'autorité",
             "suggestion": "Ajouter des citations d'études reconnues"}
        ],
        "suggestions_prioritaires": ["Ajouter des sources d'autorité"],
    })

    brief = BriefSEO(
        requete="test", mots_cles_principaux=[], mots_cles_secondaires=[],
        intention_recherche="info", structure_cible=[],
        longueur_min=500, longueur_max=1000, ton="pro", audience_cible="",
    )
    synthese = Synthese(
        brief=brief, sources=[], documents_fournis=None,
        insights_cles=[], lacunes_identifiees=[],
    )
    draft = Draft(
        brief=brief, synthese=synthese,
        titre="Test", sections={"intro": "contenu"},
        meta_description="desc",
    )

    resultat = agent.parser_sortie(reponse_json, draft=draft)

    assert isinstance(resultat, RapportConformiteGoogle)
    assert resultat.score_eeat == 7.0
    assert resultat.score_semantique == 6.5
    assert resultat.score_global == 6.8
    assert resultat.conformite_atteinte is False
    assert len(resultat.recommandations) == 1
    assert resultat.recommandations[0]["categorie"] == "eeat"


def test_orchestrator_avec_conformite():
    config = MagicMock(spec=Config)
    config.max_iterations = 3
    config.score_seuil = 7.0
    config.sortie_dossier = "./output"

    mock_client = MagicMock(spec=DeepSeekClient)
    agent_strategie = AgentStrategie(mock_client)
    agent_recherche = AgentRecherche(mock_client)
    agent_redaction = AgentRedaction(mock_client)
    agent_critique = AgentCritique(mock_client)
    agent_conformite = AgentConformiteGoogle(mock_client)

    strategie_json = json.dumps({
        "requete": "test",
        "mots_cles_principaux": ["ia"],
        "mots_cles_secondaires": [],
        "intention_recherche": "informationnelle",
        "structure_cible": ["intro"],
        "ton": "pro", "audience_cible": "",
    })
    recherche_json = json.dumps({
        "sources": [], "documents_fournis": None,
        "insights_cles": [], "lacunes_identifiees": [],
    })
    redaction_json = json.dumps({
        "titre": "Test", "sections": {"intro": "contenu"},
        "meta_description": "desc",
    })

    critique_json = json.dumps({
        "score_editorial": 7.0, "score_seo": 7.0,
        "score_global": 7.0, "seuil_atteint": True,
        "critiques": [], "suggestions_prioritaires": [],
    })

    conformite_json = json.dumps({
        "score_eeat": 6.0, "score_semantique": 6.0,
        "score_lisibilite": 8.0, "score_featured_snippet": 5.0,
        "score_maillage": 5.0, "score_meta": 7.0,
        "score_structure": 8.0, "score_originalite": 7.0,
        "score_global": 6.3, "conformite_atteinte": False,
        "recommandations": [
            {"categorie": "eeat", "gravite": "moyenne",
             "message": "E-E-A-T insuffisant",
             "suggestion": "Ajouter des sources"}
        ],
        "suggestions_prioritaires": ["Ajouter des sources d'autorité"],
    })

    # Retourne la conformité avec un score bas la 1ère fois, ok la 2ème
    conformite_json_bon = json.dumps({
        "score_eeat": 8.0, "score_semantique": 7.0,
        "score_lisibilite": 8.0, "score_featured_snippet": 7.0,
        "score_maillage": 7.0, "score_meta": 8.0,
        "score_structure": 8.0, "score_originalite": 7.0,
        "score_global": 7.5, "conformite_atteinte": True,
        "recommandations": [], "suggestions_prioritaires": [],
    })

    mock_client.chat.side_effect = [
        strategie_json, recherche_json,
        redaction_json, critique_json, conformite_json,
        redaction_json, critique_json, conformite_json_bon,
    ]

    orchestrator = Orchestrator(
        config=config,
        agent_strategie=agent_strategie,
        agent_recherche=agent_recherche,
        agent_redaction=agent_redaction,
        agent_critique=agent_critique,
        agent_conformite=agent_conformite,
    )

    resultat = orchestrator.executer(requete="test")
    assert resultat["score_conformite"] is not None
    assert resultat["iterations"] >= 1
