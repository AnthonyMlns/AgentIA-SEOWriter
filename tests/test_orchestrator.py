import json
import pytest
from unittest.mock import MagicMock

from src.config import Config
from src.client import DeepSeekClient
from src.models import BriefSEO, Synthese, Draft, RapportCritique
from src.agents.strategie import AgentStrategie
from src.agents.recherche import AgentRecherche
from src.agents.redaction import AgentRedaction
from src.agents.critique import AgentCritique
from src.orchestrator import Orchestrator


@pytest.fixture
def config():
    cfg = MagicMock(spec=Config)
    cfg.max_iterations = 3
    cfg.score_seuil = 7.0
    cfg.sortie_dossier = "./output"
    return cfg


@pytest.fixture
def mock_client():
    client = MagicMock(spec=DeepSeekClient)
    client.chat.return_value = '{"ok": true}'
    return client


def test_orchestrator_pipeline_complet(config, mock_client):
    agent_strategie = AgentStrategie(mock_client)
    agent_recherche = AgentRecherche(mock_client)
    agent_redaction = AgentRedaction(mock_client)
    agent_critique = AgentCritique(mock_client)

    mock_client.chat.side_effect = [
        json_strategie := json.dumps({
            "requete": "test ia",
            "mots_cles_principaux": ["ia", "pme"],
            "mots_cles_secondaires": ["automatisation"],
            "intention_recherche": "informationnelle",
            "structure_cible": ["intro", "developpement", "conclusion"],
            "ton": "vulgarisation",
            "audience_cible": "dirigeants",
        }),
        json_recherche := json.dumps({
            "sources": [{"url": "https://exemple.com", "titre": "Test",
                          "extrait": "...", "pertinence": 0.9}],
            "documents_fournis": None,
            "insights_cles": ["insight 1"],
            "lacunes_identifiees": ["lacune 1"],
        }),
        json_redaction := json.dumps({
            "titre": "Article test",
            "sections": {"intro": "contenu"},
            "meta_description": "description test",
        }),
        json_critique := json.dumps({
            "score_editorial": 7.5,
            "score_seo": 7.0,
            "score_global": 7.3,
            "seuil_atteint": True,
            "critiques": [],
            "suggestions_prioritaires": [],
        }),
    ]

    orchestrator = Orchestrator(
        config=config,
        agent_strategie=agent_strategie,
        agent_recherche=agent_recherche,
        agent_redaction=agent_redaction,
        agent_critique=agent_critique,
    )

    resultat = orchestrator.executer(
        requete="test ia",
        mots_cles="ia,pme",
        ton="vulgarisation",
    )

    assert resultat["score"] == 7.3
    assert resultat["seuil_atteint"] is True
    assert resultat["iterations"] == 1
    assert "chemin_article" in resultat
    assert "chemin_rapport" in resultat


def test_orchestrator_boucle_feedback(config, mock_client):
    agent_strategie = AgentStrategie(mock_client)
    agent_recherche = AgentRecherche(mock_client)
    agent_redaction = AgentRedaction(mock_client)
    agent_critique = AgentCritique(mock_client)

    strategie_json = json.dumps({
        "requete": "test",
        "mots_cles_principaux": ["ia"],
        "mots_cles_secondaires": [],
        "intention_recherche": "informationnelle",
        "structure_cible": ["intro"],
        "ton": "pro",
        "audience_cible": "",
    })

    recherche_json = json.dumps({
        "sources": [], "documents_fournis": None,
        "insights_cles": [], "lacunes_identifiees": [],
    })

    redaction_json = json.dumps({
        "titre": "Test", "sections": {"intro": "contenu"},
        "meta_description": "desc",
    })

    critique_mauvais = json.dumps({
        "score_editorial": 5.0, "score_seo": 5.0,
        "score_global": 5.0, "seuil_atteint": False,
        "critiques": [{"categorie": "mots_cles", "gravite": "haute",
                        "message": "manque mots-clés",
                        "suggestion": "ajouter des mots-clés"}],
        "suggestions_prioritaires": ["ajouter des mots-clés"],
    })

    critique_bon = json.dumps({
        "score_editorial": 8.0, "score_seo": 7.0,
        "score_global": 7.5, "seuil_atteint": True,
        "critiques": [], "suggestions_prioritaires": [],
    })

    mock_client.chat.side_effect = [
        strategie_json, recherche_json,
        redaction_json, critique_mauvais,
        redaction_json, critique_bon,
    ]

    orchestrator = Orchestrator(
        config=config,
        agent_strategie=agent_strategie,
        agent_recherche=agent_recherche,
        agent_redaction=agent_redaction,
        agent_critique=agent_critique,
    )

    resultat = orchestrator.executer(requete="test")
    assert resultat["iterations"] == 2
    assert resultat["seuil_atteint"] is True
