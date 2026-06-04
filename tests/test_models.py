import pytest
from src.models import BriefSEO, Synthese, Draft, RapportCritique


def test_brief_seo():
    brief = BriefSEO(
        requete="test",
        mots_cles_principaux=["ia", "pme"],
        mots_cles_secondaires=["automatisation"],
        intention_recherche="informationnelle",
        structure_cible=["intro", "corps"],
        longueur_min=800,
        longueur_max=1500,
        ton="vulgarisation",
        audience_cible="dirigeants PME",
    )
    d = brief.to_dict()
    assert d["requete"] == "test"
    assert len(d["mots_cles_principaux"]) == 2


def test_draft_avec_historique():
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
        meta_description="desc", version=2,
        historique_critiques=[{"iteration": 1, "score": 5.0}],
    )
    assert draft.version == 2
    assert draft.historique_critiques[0]["score"] == 5.0


def test_rapport_critique():
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
        titre="Test", sections={}, meta_description="",
    )
    rapport = RapportCritique(
        draft=draft,
        score_editorial=7.0,
        score_seo=6.0,
        score_global=6.5,
        seuil_atteint=False,
        critiques=[{"categorie": "mots_cles", "gravite": "haute",
                     "message": "test", "suggestion": "test"}],
        suggestions_prioritaires=["ajouter des mots-clés"],
    )
    assert rapport.score_global == 6.5
    assert rapport.seuil_atteint is False
