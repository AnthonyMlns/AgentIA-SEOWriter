import json
import pytest
from unittest.mock import MagicMock

from src.config import Config
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


def _build_repondre(reponses: list[str]):
    iterator = iter(reponses)
    def repondre(system: str, user: str) -> str:
        return next(iterator)
    return repondre


def test_orchestrator_pipeline_complet(config):
    agent_strategie = AgentStrategie()
    agent_recherche = AgentRecherche()
    agent_redaction = AgentRedaction()
    agent_critique = AgentCritique()

    repondre = _build_repondre([
        json.dumps({
            "requete": "test ia",
            "mots_cles_principaux": ["ia", "pme"],
            "mots_cles_secondaires": ["automatisation"],
            "intention_recherche": "informationnelle",
            "structure_cible": ["intro", "developpement", "conclusion"],
            "ton": "vulgarisation",
            "audience_cible": "dirigeants",
        }),
        json.dumps({
            "sources": [{"url": "https://exemple.com", "titre": "Test",
                          "extrait": "...", "pertinence": 0.9}],
            "documents_fournis": None,
            "insights_cles": ["insight 1"],
            "lacunes_identifiees": ["lacune 1"],
        }),
        json.dumps({
            "titre": "Article test",
            "sections": {"intro": "contenu"},
            "meta_description": "description test",
        }),
        json.dumps({
            "score_editorial": 7.5,
            "score_seo": 7.0,
            "score_global": 7.3,
            "seuil_atteint": True,
            "critiques": [],
            "suggestions_prioritaires": [],
        }),
    ])

    orchestrator = Orchestrator(
        config=config,
        agent_strategie=agent_strategie,
        agent_recherche=agent_recherche,
        agent_redaction=agent_redaction,
        agent_critique=agent_critique,
    )

    resultat = orchestrator.executer(
        requete="test ia",
        repondre=repondre,
        mots_cles="ia,pme",
        ton="vulgarisation",
    )

    assert resultat["score"] == 7.3
    assert resultat["seuil_atteint"] is True
    assert resultat["iterations"] == 1
    assert "chemin_article" in resultat
    assert "chemin_rapport" in resultat


def test_orchestrator_boucle_feedback(config):
    agent_strategie = AgentStrategie()
    agent_recherche = AgentRecherche()
    agent_redaction = AgentRedaction()
    agent_critique = AgentCritique()

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

    repondre = _build_repondre([
        strategie_json, recherche_json,
        redaction_json, critique_mauvais,
        redaction_json, critique_bon,
    ])

    orchestrator = Orchestrator(
        config=config,
        agent_strategie=agent_strategie,
        agent_recherche=agent_recherche,
        agent_redaction=agent_redaction,
        agent_critique=agent_critique,
    )

    resultat = orchestrator.executer(requete="test", repondre=repondre)
    assert resultat["iterations"] == 2
    assert resultat["seuil_atteint"] is True
